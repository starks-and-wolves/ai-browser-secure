"""
Generic AWI Execution Tool

Provides a single, task-agnostic tool for executing AWI API calls.
The LLM decides all parameters based on:
- Task requirements
- Available operations from manifest
- Endpoint structure from base URL

Supports TWO MODES for providing body data:
1. Traditional: Provide complete body dict
2. Two-Phase: Provide simple field-value pairs (easier for weak models)
"""

import logging
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field  # type: ignore[reportMissingImports]

from browser_use.agent.views import ActionResult

logger = logging.getLogger(__name__)


class FieldValue(BaseModel):
	"""Simple field-value pair for two-phase body construction."""
	field_name: str = Field(description="Field name from the API schema")
	value: str = Field(
		description="Value for this field as a string. For complex values, use JSON string format."
	)


class AWIExecuteAction(BaseModel):
	"""
	Generic AWI API execution action.

	All parameters are determined by the LLM based on:
	- The user's task
	- Available operations from the AWI manifest
	- The API structure discovered from the manifest
	"""

	operation: str = Field(
		description=(
			'The operation type from the AWI manifest (e.g., read, write, list, get, create, search, delete). '
			'This should match one of the allowed_operations from the manifest.'
		)
	)

	endpoint: str = Field(
		description=(
			'The API endpoint path relative to base URL (e.g., /posts, /posts/{id}, /posts/{id}/comments). '
			'The LLM should construct this based on the task and API structure.'
		)
	)

	method: str = Field(
		description=(
			'HTTP method to use: GET, POST, PUT, PATCH, DELETE. '
			'The LLM should choose based on the operation type and semantic meaning.'
		)
	)

	params: Optional[Dict[str, Any]] = Field(
		default=None,
		description=(
			'Optional query parameters as key-value pairs (e.g., {"sort": "popular", "limit": 3}). '
			'Used for filtering, sorting, pagination, etc. The LLM decides based on task requirements.'
		)
	)

	body: Optional[Dict[str, Any]] = Field(
		default=None,
		description=(
			'Request body as complete JSON object for POST/PUT/PATCH requests. '
			'Use this if you can construct the full body. '
			'Refer to API OPERATIONS SCHEMA in context for required fields and their types.'
		)
	)

	field_values: Optional[List[FieldValue]] = Field(
		default=None,
		description=(
			'Alternative to body: Provide simple field-value pairs. '
			'Use this simpler approach if constructing the full body is difficult. '
			'Example: [{"field_name": "required_field_name", "value": "your_value_here"}]'
		)
	)


async def awi_execute(
	params: AWIExecuteAction,
	awi_manager
) -> ActionResult:
	"""
	Execute a generic AWI API call.

	This is a task-agnostic function that executes whatever API call
	the LLM has planned based on the task and manifest.

	Supports two modes for body construction:
	1. Direct: LLM provides complete body dict
	2. Two-Phase: LLM provides field_values, system constructs body

	Args:
		params: Execution parameters decided by the LLM
		awi_manager: AWI manager instance with authentication

	Returns:
		ActionResult with the API response formatted for the agent
	"""
	try:
		logger.info(
			f"AWI Execute: {params.method} {params.endpoint} "
			f"(operation: {params.operation})"
		)

		# Handle body construction for POST/PUT/PATCH operations
		if params.method.upper() in ['POST', 'PUT', 'PATCH']:
			# Check if we have either body or field_values
			has_body = params.body and isinstance(params.body, dict) and len(params.body) > 0
			field_values = params.field_values or []
			has_field_values = len(field_values) > 0

			if not has_body and not has_field_values:
				# Neither provided - return helpful error
				error_msg = (
					f"❌ Empty body for {params.method} {params.endpoint}\n\n"
					f"⚠️  You need to provide request data using ONE of these approaches:\n\n"
					f"Option 1 - Full Body (if you can construct it):\n"
					f"  body={{\"content\": \"Great post!\", \"authorName\": \"Agent\"}}\n\n"
					f"Option 2 - Simple Field Values (easier for complex structures):\n"
					f"  field_values=[\n"
					f"	{{\"field_name\": \"content\", \"value\": \"Great post!\"}},\n"
					f"	{{\"field_name\": \"authorName\", \"value\": \"Agent\"}}\n"
					f"  ]\n\n"
					f"💡 Option 2 is simpler - just list field names and values!\n"
					f"The system will construct the proper body structure for you.\n\n"
					f"Refer to the API OPERATIONS SCHEMA in your context for required fields."
				)
				logger.error(f"❌ Empty body and no field_values for {params.method} {params.endpoint}")
				return ActionResult(error=error_msg)

			# Two-Phase Mode: Construct body from field_values
			if has_field_values:
				logger.info(f"🔧 Two-Phase Mode: Constructing body from {len(field_values)} field values")
				from browser_use.awi.body_constructor import BodyConstructor, FieldValue as BodyConstructorFieldValue

				constructor = BodyConstructor(awi_manager.manifest)
				required, optional, validation = constructor.get_field_requirements(
					params.operation,
					params.endpoint
				)

				try:
					converted_values = [
						BodyConstructorFieldValue(field_name=v.field_name, value=v.value) for v in field_values
					]
					params.body = constructor.construct_body_from_values(
						converted_values,
						required
					)
					logger.info(f"✅ Constructed body: {params.body}")
				except ValueError as e:
					error_msg = (
						f"❌ Failed to construct body from field_values\n\n"
						f"Error: {str(e)}\n\n"
						f"Required fields: {required}\n"
						f"Optional fields: {optional}\n\n"
						f"Please provide all required fields in your field_values list."
					)
					logger.error(f"❌ Body construction failed: {e}")
					return ActionResult(error=error_msg)

		# Construct full URL
		base_url = awi_manager.base_url
		logger.debug(f"Base URL from manager: '{base_url}'")
		logger.debug(f"Endpoint: '{params.endpoint}'")

		# Handle both cases: base_url with/without trailing slash
		if base_url.endswith('/') and params.endpoint.startswith('/'):
			url = base_url + params.endpoint[1:]
		elif not base_url.endswith('/') and not params.endpoint.startswith('/'):
			url = base_url + '/' + params.endpoint
		else:
			url = base_url + params.endpoint

		logger.debug(f"Constructed URL: '{url}'")

		# Get authentication headers
		headers = awi_manager._get_headers()

		# Make the HTTP request
		async with awi_manager.session.request(
			method=params.method.upper(),
			url=url,
			params=params.params,
			json=params.body,
			headers=headers
		) as response:

			# Get response status
			status = response.status

			# Try to parse JSON response
			try:
				data = await response.json()
			except Exception:
				# If not JSON, get text
				data = {'text': await response.text(), 'status': status}

			# Check for errors
			if status >= 400:
				error_msg = data.get('error', data.get('message', f'HTTP {status}'))

				# If there are detailed validation errors, include them
				detailed_error = error_msg
				fix_suggestion = ""

				if 'errors' in data and data['errors']:
					# Format validation errors for the LLM
					validation_details = []
					missing_fields = []

					for err in data['errors']:
						field = err.get('field', 'unknown')
						message = err.get('message', 'validation failed')
						validation_details.append(f"{field}: {message}")

						# Track missing required fields
						if 'required' in message.lower():
							missing_fields.append(field)

					detailed_error = f"{error_msg}. Details: {'; '.join(validation_details)}"

					# Add explicit fix suggestion for missing fields
					if missing_fields:
						if missing_fields:
							# Generate schema-driven example
							example_fields = {field: f"<{field}_value>" for field in missing_fields}
							fix_suggestion = f"FIX: Include required fields: {example_fields}"
						else:
							example_body = {field: f"<{field}_value>" for field in missing_fields}
							fix_suggestion = f"\n\n💡 FIX: Include these required fields in your body parameter: {example_body}"

				elif 'details' in data and data['details']:
					# Alternative format (errorsByField)
					validation_details = []
					for field, messages in data['details'].items():
						# Handle both list and string messages
						if isinstance(messages, (list, tuple)):
							validation_details.append(f"{field}: {', '.join(messages)}")
						else:
							validation_details.append(f"{field}: {messages}")
					detailed_error = f"{error_msg}. Details: {'; '.join(validation_details)}"

				logger.error(f"❌ AWI Execute failed: {detailed_error}")
				return ActionResult(
					error=f"API call failed ({status}): {detailed_error}{fix_suggestion}"
				)

			# Format successful response for agent
			formatted = f"✅ API Call Successful ({status} {params.method} {params.endpoint})\n\n"
			formatted += f"Operation: {params.operation}\n"

			# Detect potential task completion
			suggests_completion = False
			completion_reason = None

			# Format response data readably with summary
			if isinstance(data, dict):
				# Add a summary line for the agent to understand what happened
				if params.operation == 'list' and 'posts' in data:
					post_count = len(data['posts'])
					formatted += f"\n📊 Retrieved {post_count} posts successfully.\n"
					if post_count > 0:
						formatted += f"First post: {data['posts'][0].get('title', 'Untitled')} (ID: {data['posts'][0].get('_id', 'unknown')})\n"

					# Suggest completion for simple list-only tasks
					if 'list' in params.endpoint.lower() and post_count > 0:
						suggests_completion = True
						completion_reason = f"Successfully listed {post_count} items"

				elif params.operation == 'create' and status == 201:
					formatted += f"\n✅ {params.operation.capitalize()} operation completed successfully.\n"
					if 'comment' in data:
						formatted += f"Comment created: \"{data['comment'].get('content', '')}\" by {data['comment'].get('authorName', 'Unknown')}\n"
						suggests_completion = True
						completion_reason = "Comment successfully created"
					elif 'post' in data:
						formatted += f"Post created: \"{data['post'].get('title', '')}\" (ID: {data['post'].get('_id', 'unknown')})\n"
						suggests_completion = True
						completion_reason = "Post successfully created"

				elif params.operation == 'search' and 'results' in data:
					result_count = len(data.get('results', []))
					formatted += f"\n🔍 Search completed: {result_count} results found.\n"
					suggests_completion = True
					completion_reason = f"Search completed with {result_count} results"

				# Pretty print the full response
				formatted += "\nFull Response:\n"
				formatted += json.dumps(data, indent=2, ensure_ascii=False)[:1000]  # Limit size
				if len(json.dumps(data)) > 1000:
					formatted += "\n... (response truncated, full data in metadata)"
			else:
				formatted += f"\nResponse: {data}\n"

			# Add clear completion note for common task patterns
			if suggests_completion:
				formatted += f"\n\n💡 COMPLETION CHECK: {completion_reason}. "
				formatted += "If this completes your task, call the 'done' action now to finish."

			logger.info(f"✅ AWI Execute successful: {status} {params.method} {params.endpoint}")

			return ActionResult(
				extracted_content=formatted,
				include_in_memory=True,  # Make sure this gets into agent memory
				metadata={
					'response': data,
					'status': status,
					'operation': params.operation,
					'endpoint': params.endpoint,
					'method': params.method,
					'success': True,
					'suggests_completion': suggests_completion,  # Hint for potential completion
					'completion_reason': completion_reason  # Why this might complete the task
				}
			)

	except Exception as e:
		import traceback
		logger.error(f"❌ AWI Execute exception: {type(e).__name__}: {e}")
		logger.error(f"   Traceback: {traceback.format_exc()}")
		return ActionResult(
			error=f"Failed to execute AWI call ({type(e).__name__}): {str(e)}"
		)
