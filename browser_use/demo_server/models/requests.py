"""
Pydantic models for API requests
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class LiveExecutionRequest(BaseModel):
	"""Request to start a live agent execution"""
	task: str = Field(..., description="Task for the agent to perform", max_length=1000)
	llm_provider: str = Field(..., description="LLM provider (openai, anthropic)")
	api_key: str = Field(..., description="API key for the LLM provider (not stored)")
	allowed_domains: List[str] = Field(
		default_factory=list,
		description="Domains the agent is allowed to access"
	)
	max_steps: int = Field(default=30, description="Maximum steps for execution", ge=1, le=50)

class DomainValidationRequest(BaseModel):
	"""Request to validate a domain"""
	domain: str = Field(..., description="Domain to validate")
	task: str = Field(..., description="Task context")
