"""
AWI Body Constructor - Two-Phase Approach

This module implements a two-phase approach for constructing request bodies:
1. Extract required/optional fields from the AWI manifest schema
2. Prompt the LLM to provide just the values (simple task)
3. System constructs the properly structured body

This approach works with weaker models by simplifying the LLM's task.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FieldValue(BaseModel):
	"""Simple field-value pair for LLM to fill."""
	field_name: str = Field(description="Name of the field (from schema)")
	value: Any = Field(description="Value for this field")


class AWIBodyValues(BaseModel):
	"""
	Simple action for LLM to provide just field values.

	The system will look up required fields from the schema, and the LLM
	only needs to provide values for each field. This is much simpler than
	constructing the entire body structure.
	"""
	values: List[FieldValue] = Field(
		description=(
			"List of field values to include in the request body. "
			"Each entry should have field_name and value. "
			"Only provide values for fields that are relevant to your task."
		)
	)


class BodyConstructor:
	"""
	Constructs request bodies from AWI manifest schema and LLM-provided values.

	This implements the two-phase approach:
	1. System extracts required/optional fields from manifest
	2. LLM provides simple field values
	3. System constructs the body dict
	"""

	def __init__(self, manifest: Dict[str, Any]):
		"""
		Initialize with AWI manifest.

		Args:
			manifest: AWI manifest containing operations schema
		"""
		self.manifest = manifest
		self.operations = manifest.get('operations', {})
		self.quick_reference = manifest.get('llm_quick_reference', {})

	def _get_requirements_from_quick_reference(
		self,
		resource: str,
		operation: str
	) -> Optional[tuple[List[str], List[str]]]:
		"""
		Try to get field requirements from llm_quick_reference section.

		Args:
			resource: Resource name (e.g., 'posts', 'comments')
			operation: Operation name (e.g., 'create', 'update')

		Returns:
			Tuple of (required_fields, optional_fields) or None if not found
		"""
		if not self.quick_reference:
			return None

		field_summary = self.quick_reference.get('field_requirements_summary', {})
		if not field_summary:
			return None

		# Try resource.operation format (e.g., "comments.create")
		key = f"{resource}.{operation}"
		if key in field_summary:
			entry = field_summary[key]
			required = entry.get('required', [])
			optional = entry.get('optional', [])
			logger.info(f"✅ Using llm_quick_reference for {key}")
			return required, optional

		return None

	def get_field_requirements(
		self,
		operation: str,
		endpoint: str
	) -> tuple[List[str], List[str], Dict[str, str]]:
		"""
		Extract field requirements from manifest for a given operation.

		Args:
			operation: Operation type (e.g., 'create', 'update')
			endpoint: API endpoint (e.g., '/posts', '/posts/{id}/comments')

		Returns:
			Tuple of (required_fields, optional_fields, validation_rules)
		"""
		# Determine resource from endpoint
		resource = None
		if '/comments' in endpoint:
			resource = 'comments'
		elif '/posts' in endpoint and '/comments' not in endpoint:
			resource = 'posts'
		elif '/search' in endpoint:
			resource = 'search'

		if not resource:
			logger.warning(f"Could not determine resource from endpoint: {endpoint}")
			return [], [], {}

		# Try quick reference first (optimized for weak models)
		quick_ref_result = self._get_requirements_from_quick_reference(resource, operation)
		if quick_ref_result:
			required, optional = quick_ref_result
			# Quick reference might not have detailed validation rules
			# Try to get validation from operations if available
			validation = {}
			if resource in self.operations:
				resource_ops = self.operations[resource]
				if resource == 'search':
					op_spec = resource_ops
				else:
					op_spec = resource_ops.get(operation, {})
				validation = op_spec.get('validation', {})

			logger.info(f"📋 Field requirements for {resource}.{operation} (from quick reference):")
			logger.info(f"   Required: {required}")
			logger.info(f"   Optional: {optional}")
			return required, optional, validation

		# Fall back to full operations schema
		if resource not in self.operations:
			logger.warning(f"Resource {resource} not found in operations")
			return [], [], {}

		# Get operation spec
		resource_ops = self.operations[resource]

		# Search is at root level
		if resource == 'search':
			op_spec = resource_ops
		else:
			op_spec = resource_ops.get(operation, {})

		if not op_spec:
			logger.warning(f"No spec found for {resource}.{operation}")
			return [], [], {}

		required = op_spec.get('required_fields', [])
		optional = op_spec.get('optional_fields', [])
		validation = op_spec.get('validation', {})

		logger.info(f"📋 Field requirements for {resource}.{operation}:")
		logger.info(f"   Required: {required}")
		logger.info(f"   Optional: {optional}")
		logger.info(f"   Validation: {validation}")

		return required, optional, validation

	def construct_body_from_values(
		self,
		values: List[FieldValue],
		required_fields: List[str]
	) -> Dict[str, Any]:
		"""
		Construct request body from LLM-provided field values.

		Args:
			values: List of field-value pairs from LLM
			required_fields: List of required field names from schema

		Returns:
			Dict ready to use as request body

		Raises:
			ValueError: If required fields are missing
		"""
		body = {}

		# Convert list of FieldValue to dict
		for fv in values:
			body[fv.field_name] = fv.value

		# Validate required fields are present
		missing = [f for f in required_fields if f not in body]
		if missing:
			raise ValueError(
				f"Missing required fields: {missing}. "
				f"Required: {required_fields}, Provided: {list(body.keys())}"
			)

		logger.info(f"✅ Constructed body: {body}")
		return body

	def get_field_guidance(
		self,
		operation: str,
		endpoint: str,
		task_description: str
	) -> str:
		"""
		Generate guidance message for LLM to help it provide field values.

		Args:
			operation: Operation type
			endpoint: API endpoint
			task_description: User's task description

		Returns:
			Formatted guidance string
		"""
		required, optional, validation = self.get_field_requirements(operation, endpoint)

		if not required and not optional:
			return ""

		guidance = f"""

╔══════════════════════════════════════════════════════════════════════════════╗
║                    📝 PROVIDE FIELD VALUES                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

You need to provide values for the following fields to complete this {operation} operation:

"""

		if required:
			guidance += f"✅ REQUIRED FIELDS (you MUST provide these):\n"
			for field in required:
				rule = validation.get(field, 'No specific validation')
				guidance += f"  • {field}: {rule}\n"
			guidance += "\n"

		if optional:
			guidance += f"📎 OPTIONAL FIELDS (include if relevant to your task):\n"
			for field in optional:
				rule = validation.get(field, 'No specific validation')
				guidance += f"  • {field}: {rule}\n"
			guidance += "\n"

		guidance += f"""
💡 TASK REMINDER: {task_description}

🎯 WHAT TO DO:
Instead of constructing the full body dict yourself, just tell me the values for each field:

Example:
  values: [
    {{field_name: "content", value: "Great post!"}},
    {{field_name: "authorName", value: "Agent"}}
  ]

The system will automatically construct the proper request body for you.
This is much simpler than building the whole {{}} structure!
"""

		return guidance


def should_use_two_phase(
	method: str,
	body: Optional[Dict[str, Any]],
	operation: str
) -> bool:
	"""
	Determine if two-phase approach should be used.

	Use two-phase if:
	- Method requires a body (POST/PUT/PATCH)
	- Body is empty or None
	- Operation is a create/update type

	Args:
		method: HTTP method
		body: Current body parameter
		operation: Operation type

	Returns:
		True if two-phase should be used
	"""
	if method.upper() not in ['POST', 'PUT', 'PATCH']:
		return False

	if body and isinstance(body, dict) and len(body) > 0:
		return False  # Body already provided

	if operation in ['create', 'update', 'search']:
		return True

	return False
