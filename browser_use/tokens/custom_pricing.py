"""
Custom model pricing for models not available in LiteLLM's pricing data.

Prices are per token (not per 1M tokens).
"""

from typing import Any

# Custom model pricing data
# Format matches LiteLLM's model_prices_and_context_window.json structure
CUSTOM_MODEL_PRICING: dict[str, dict[str, Any]] = {
	'bu-1-0': {
		'input_cost_per_token': 0.2 / 1_000_000,  # $0.50 per 1M tokens
		'output_cost_per_token': 2.00 / 1_000_000,  # $3.00 per 1M tokens
		'cache_read_input_token_cost': 0.02 / 1_000_000,  # $0.10 per 1M tokens
		'cache_creation_input_token_cost': None,  # Not specified
		'max_tokens': None,  # Not specified
		'max_input_tokens': None,  # Not specified
		'max_output_tokens': None,  # Not specified
	}
}
CUSTOM_MODEL_PRICING['bu-latest'] = CUSTOM_MODEL_PRICING['bu-1-0']

CUSTOM_MODEL_PRICING['smart'] = CUSTOM_MODEL_PRICING['bu-1-0']

# GPT-5-nano (test/development model - using similar pricing to gpt-3.5-turbo)
CUSTOM_MODEL_PRICING['gpt-5-nano'] = {
	'input_cost_per_token': 0.50 / 1_000_000,  # $0.50 per 1M input tokens
	'output_cost_per_token': 1.50 / 1_000_000,  # $1.50 per 1M output tokens
	'cache_read_input_token_cost': None,
	'cache_creation_input_token_cost': None,
	'max_tokens': 4096,
	'max_input_tokens': 16385,
	'max_output_tokens': 4096,
}
