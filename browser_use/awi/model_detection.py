"""
Model Capability Detection

Detects LLM model capabilities to choose appropriate manifest format
and context verbosity for AWI operations.
"""

from enum import Enum
from typing import Optional
import re


class ModelCapability(Enum):
	"""Model capability tiers for AWI operations."""
	PREMIUM = "premium"  # GPT-4+, Claude 3+, Gemini Pro - can handle full schema
	STANDARD = "standard"  # GPT-3.5, Claude Instant - needs quick reference
	WEAK = "weak"  # gpt-5-nano, lightweight models - needs extreme simplification


def detect_model_capability(model_name: Optional[str]) -> ModelCapability:
	"""
	Detect model capability tier based on model name.

	Args:
		model_name: The model identifier (e.g., "gpt-4o", "claude-3-opus")

	Returns:
		ModelCapability tier
	"""
	if not model_name:
		# Default to standard if unknown
		return ModelCapability.STANDARD

	model_lower = model_name.lower()

	# Premium tier models - can handle complex schemas
	premium_patterns = [
		r'gpt-4',  # GPT-4, GPT-4o, GPT-4-turbo, etc.
		r'claude-3',  # Claude 3 Opus, Sonnet, Haiku
		r'claude-opus',
		r'claude-sonnet',
		r'gemini-pro',
		r'gemini-1\.5',
		r'gemini-2',
		r'o1',  # OpenAI o1 models
		r'o3',  # OpenAI o3 models
	]

	for pattern in premium_patterns:
		if re.search(pattern, model_lower):
			return ModelCapability.PREMIUM

	# Weak tier models - need extreme simplification
	weak_patterns = [
		r'gpt-5-nano',
		r'gpt-3\.5-turbo-0125',  # Older GPT-3.5
		r'gpt-3\.5-turbo-0613',
		r'text-davinci',
		r'nano',
		r'tiny',
		r'mini',
	]

	for pattern in weak_patterns:
		if re.search(pattern, model_lower):
			return ModelCapability.WEAK

	# Standard tier - everything else (GPT-3.5, Claude Instant, etc.)
	return ModelCapability.STANDARD


def get_recommended_format(capability: ModelCapability) -> str:
	"""
	Get recommended manifest format for model capability.

	Args:
		capability: Model capability tier

	Returns:
		Format string for ?format= parameter
	"""
	format_map = {
		ModelCapability.PREMIUM: "enhanced",  # Default enhanced format
		ModelCapability.STANDARD: "summary",  # Simplified quick reference
		ModelCapability.WEAK: "summary",  # Extreme simplification needed
	}

	return format_map[capability]


def should_use_quick_reference(capability: ModelCapability) -> bool:
	"""
	Determine if llm_quick_reference should be prioritized over full schema.

	Args:
		capability: Model capability tier

	Returns:
		True if quick reference should be used
	"""
	# Standard and weak models benefit from quick reference
	return capability in (ModelCapability.STANDARD, ModelCapability.WEAK)


def get_context_verbosity(capability: ModelCapability) -> str:
	"""
	Get recommended context verbosity level.

	Args:
		capability: Model capability tier

	Returns:
		Verbosity level: "full", "moderate", "minimal"
	"""
	verbosity_map = {
		ModelCapability.PREMIUM: "full",  # Can handle detailed explanations
		ModelCapability.STANDARD: "moderate",  # Concise but complete
		ModelCapability.WEAK: "minimal",  # Bare essentials only
	}

	return verbosity_map[capability]
