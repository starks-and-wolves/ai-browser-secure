"""
Router for demo-related endpoints
Serves pre-recorded demo metadata and trajectory files
"""

from fastapi import APIRouter, HTTPException
from browser_use.demo_server.models.responses import DemoListResponse, DemoMetadata
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=DemoListResponse)
async def list_demos():
	"""
	Get list of all available demos
	Returns metadata for each demo including metrics
	"""
	try:
		# In production, this would load from S3/R2 or local storage
		# For now, return a placeholder
		demos = [
			DemoMetadata(
				id="reddit-search-traditional",
				title="Reddit Search - Traditional Mode",
				description="Find posts about browser automation using DOM parsing",
				mode="traditional",
				task="Find top 5 posts about 'browser automation' on r/programming",
				metrics={
					"steps": 28,
					"tokens": 45230,
					"cost": 0.47,
					"duration": 28.3
				},
				trajectory_url="/demos/reddit-search-traditional.json",
			),
			DemoMetadata(
				id="reddit-search-awi",
				title="Reddit Search - AWI Mode",
				description="Same task using AWI structured API",
				mode="awi",
				task="Find top 5 posts about 'browser automation' on r/programming",
				metrics={
					"steps": 3,
					"tokens": 89,
					"cost": 0.001,
					"duration": 1.2
				},
				trajectory_url="/demos/reddit-search-awi.json",
			),
		]

		return DemoListResponse(demos=demos)

	except Exception as e:
		logger.error(f"Error listing demos: {e}")
		raise HTTPException(status_code=500, detail=f"Failed to list demos: {str(e)}")

@router.get("/{demo_id}")
async def get_demo(demo_id: str):
	"""
	Get a specific demo trajectory by ID
	Returns the full AgentHistory JSON
	"""
	try:
		# In production, this would load from S3/R2 or local storage
		# For now, return a simple response
		return {
			"message": f"Demo {demo_id} would be returned here",
			"note": "This will load the full trajectory JSON in Phase 2"
		}

	except Exception as e:
		logger.error(f"Error loading demo {demo_id}: {e}")
		raise HTTPException(
			status_code=404,
			detail=f"Demo {demo_id} not found"
		)
