"""
Pydantic models for API responses
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class DemoMetadata(BaseModel):
	"""Metadata for a demo"""
	id: str
	title: str
	description: str
	mode: str  # traditional, permission, awi
	task: str
	metrics: Dict[str, Any]
	thumbnail: Optional[str] = None
	trajectory_url: str
	video_url: Optional[str] = None

class DemoListResponse(BaseModel):
	"""Response containing list of available demos"""
	demos: List[DemoMetadata]

class SessionStartResponse(BaseModel):
	"""Response when starting a live execution session"""
	session_id: str
	status: str  # "starting", "running", "completed", "failed"
	message: Optional[str] = None

class SessionStatusResponse(BaseModel):
	"""Response for session status polling"""
	session_id: str
	status: str
	current_step: int
	max_steps: int
	current_url: Optional[str] = None
	last_action: Optional[str] = None
	error: Optional[str] = None

class ValidationResponse(BaseModel):
	"""Response for domain validation"""
	valid: bool
	reason: Optional[str] = None
