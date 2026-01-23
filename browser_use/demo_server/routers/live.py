"""
Live execution endpoints for browser-use demos
"""

import asyncio
import logging
from typing import Literal
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import get_default_llm
from browser_use.demo_server.replit_config import get_replit_browser_profile, should_use_remote_browser, get_remote_browser_url
import os

logger = logging.getLogger(__name__)

router = APIRouter()


class WebSocketLogHandler(logging.Handler):
	"""Custom log handler that streams logs to WebSocket"""

	def __init__(self, websocket: WebSocket):
		super().__init__()
		self.websocket = websocket
		self.loop = asyncio.get_event_loop()

	def emit(self, record: logging.LogRecord):
		"""Send log message through WebSocket"""
		try:
			log_entry = self.format(record)

			# Filter out watchdog and event bus logs
			if any(pattern in log_entry for pattern in ['Watchdog]', '🚌']):
				return
			if 'watchdog' in record.name.lower():
				return

			# Send as status message
			asyncio.create_task(self.websocket.send_json({
				"type": "log",
				"level": record.levelname,
				"message": log_entry,
				"timestamp": record.created
			}))
		except Exception:
			pass  # Silently ignore errors in log handler

# Active sessions storage
active_sessions: dict[str, dict] = {}


class AWIRegistrationConfig(BaseModel):
	"""Configuration for AWI agent registration (bypasses interactive prompts)"""
	agent_name: str = Field(default="BrowserUseAgent", description="Name for the registered agent")
	permissions: list[str] = Field(default=["read", "write"], description="Permissions to request")
	auto_approve: bool = Field(default=True, description="Auto-approve registration without prompts")


class LiveDemoRequest(BaseModel):
	"""Request model for starting a live demo"""
	task: str = Field(..., min_length=10, max_length=500, description="Task for the agent to complete")
	mode: Literal["awi", "permission"] = Field(..., description="Execution mode")
	target_url: str = Field(..., description="Target website URL")
	api_key: str = Field(..., min_length=20, description="LLM API key (never logged)")
	awi_config: AWIRegistrationConfig | None = Field(default=None, description="AWI registration config (for headless mode)")


class LiveDemoResponse(BaseModel):
	"""Response model for live demo initiation"""
	session_id: str
	websocket_url: str
	message: str


@router.post("/start", response_model=LiveDemoResponse)
async def start_live_demo(request: LiveDemoRequest):
	"""
	Start a live browser-use demo session

	Returns a session_id and WebSocket URL for real-time updates
	"""
	# Generate session ID
	session_id = str(uuid4())

	# Validate task (basic sanitization)
	if '<' in request.task or '>' in request.task or 'script' in request.task.lower():
		raise HTTPException(status_code=400, detail="Invalid task content")

	# Validate target URL
	if not request.target_url.startswith(('http://', 'https://')):
		raise HTTPException(status_code=400, detail="Invalid target URL")

	# Store session info (API key is NOT stored, only kept in memory during execution)
	active_sessions[session_id] = {
		"task": request.task,
		"mode": request.mode,
		"target_url": request.target_url,
		"status": "pending",
		"created_at": asyncio.get_event_loop().time(),
		"awi_config": request.awi_config.model_dump() if request.awi_config else None
	}

	logger.info(f"Created live demo session: {session_id} (mode={request.mode})")

	return LiveDemoResponse(
		session_id=session_id,
		websocket_url=f"/ws/live/{session_id}",
		message=f"Session created. Connect to WebSocket to start execution."
	)


@router.get("/sessions/{session_id}")
async def get_session_status(session_id: str):
	"""Get status of a live demo session"""
	if session_id not in active_sessions:
		raise HTTPException(status_code=404, detail="Session not found")

	return active_sessions[session_id]


@router.delete("/sessions/{session_id}")
async def stop_session(session_id: str):
	"""Stop and cleanup a live demo session"""
	if session_id in active_sessions:
		active_sessions[session_id]["status"] = "stopped"
		logger.info(f"Stopped session: {session_id}")
		return {"message": "Session stopped"}

	raise HTTPException(status_code=404, detail="Session not found")


@router.websocket("/ws/live/{session_id}")
async def websocket_live_demo(websocket: WebSocket, session_id: str):
	"""
	WebSocket endpoint for live demo execution
	Streams agent steps, screenshots, and metrics in real-time
	"""
	await websocket.accept()

	try:
		# Get session info
		if session_id not in active_sessions:
			await websocket.send_json({"error": "Session not found"})
			await websocket.close()
			return

		session = active_sessions[session_id]
		session["status"] = "running"

		# Wait for API key from client
		await websocket.send_json({
			"type": "ready",
			"message": "Send API key to start execution"
		})

		# Receive API key
		data = await websocket.receive_json()
		api_key = data.get("api_key")

		if not api_key:
			await websocket.send_json({"error": "API key required"})
			await websocket.close()
			return

		# Send starting message
		await websocket.send_json({
			"type": "status",
			"message": f"Starting {session['mode']} mode execution...",
			"task": session["task"]
		})

		# Create browser - match test_browser_use.py configuration
		if session["mode"] == "permission":
			# Permission mode needs headful browser with demo panel for user interaction
			profile = BrowserProfile(
				headless=False,  # Visible browser for user interaction
				demo_mode=True,  # Show demo panel in browser
				require_user_approval=True,  # Enable permission dialogs
				user_approval_for_navigation=True,  # Require approval for navigation
				user_approval_for_forms=True,  # Require approval for form input
				user_approval_for_sensitive_data=True,  # Require approval for sensitive data
				user_approval_for_file_operations=True,  # Require approval for file operations
			)
			browser = Browser(browser_profile=profile)
		elif session["mode"] == "awi":
			# AWI mode: Use optimized profile for Replit if deployed there
			if os.getenv('REPL_ID'):
				# Running on Replit - use optimized profile
				optimized_profile = get_replit_browser_profile()
				browser = Browser(browser_profile=optimized_profile)
			else:
				# Local/other deployment - simple headless browser
				browser = Browser(headless=True)
		else:
			# Traditional mode: Use optimized profile for Replit if deployed there
			if os.getenv('REPL_ID'):
				# Running on Replit - use optimized profile
				optimized_profile = get_replit_browser_profile()
				browser = Browser(browser_profile=optimized_profile)
			else:
				# Local/other deployment - simple headless browser
				browser = Browser(headless=True)

		try:
			# Set up LLM with user's API key
			os.environ["OPENAI_API_KEY"] = api_key
			os.environ["DEFAULT_LLM_MODEL"] = "gpt-5-nano"

			# Use get_default_llm() to match test_browser_use.py configuration
			try:
				llm = get_default_llm()
			except Exception as e:
				await websocket.send_json({
					"type": "error",
					"message": f"Failed to create LLM: {str(e)}"
				})
				return

			# Include target URL in the task
			target_url = session["target_url"]
			full_task = f"Go to {target_url} and then: {session['task']}"

			await websocket.send_json({
				"type": "status",
				"message": f"Task: {full_task}"
			})

			# Configure agent based on mode
			agent_kwargs = {
				"task": full_task,
				"browser": browser,
				"llm": llm,
				"max_steps": 15,  # Limit steps for live demo
				"calculate_cost": True,  # Enable cost calculation
			}

			if session["mode"] == "awi":
				agent_kwargs["awi_mode"] = True
				# Pass AWI registration config for headless mode (bypasses stdin prompts)
				if session.get("awi_config"):
					agent_kwargs["awi_registration_config"] = session["awi_config"]

			# Create agent
			agent = Agent(**agent_kwargs)

			# Set up log streaming to WebSocket
			ws_handler = WebSocketLogHandler(websocket)
			ws_handler.setLevel(logging.INFO)  # INFO level to avoid verbose DEBUG logs
			formatter = logging.Formatter('%(message)s')
			ws_handler.setFormatter(formatter)

			# Add handler to relevant loggers
			# Capture all browser_use logs by adding handler to root browser_use logger
			browser_use_logger = logging.getLogger('browser_use')
			browser_use_logger.setLevel(logging.INFO)  # INFO level to reduce noise
			browser_use_logger.addHandler(ws_handler)

			# Keep references for cleanup
			agent_logger = logging.getLogger('browser_use.agent')
			session_logger = logging.getLogger('browser_use.browser')
			awi_logger = logging.getLogger('browser_use.awi')

			# Stream execution
			await websocket.send_json({
				"type": "agent_started",
				"message": "Agent execution started"
			})

			# Run agent with step callbacks
			step_count = 0
			async def step_callback(step_data):
				nonlocal step_count
				step_count += 1

				await websocket.send_json({
					"type": "step",
					"step_number": step_count,
					"action": str(step_data.get("action", "Unknown")),
					"timestamp": asyncio.get_event_loop().time()
				})

			# Track execution time
			import time
			start_time = time.time()

			# Execute agent
			history = await agent.run()

			# Calculate duration
			end_time = time.time()
			duration_seconds = end_time - start_time

			# Send completion
			await websocket.send_json({
				"type": "completed",
				"success": history.is_done(),
				"total_steps": len(history.history),
				"result": history.final_result() if history.is_done() else None
			})

			# Also send completion as log message
			completion_status = "completed successfully" if history.is_done() else "failed"
			await websocket.send_json({
				"type": "log",
				"level": "INFO",
				"message": f"\n✅ Execution {completion_status} ({len(history.history)} steps)",
				"timestamp": asyncio.get_event_loop().time()
			})

			# Calculate and send metrics using proper token cost service
			# Get usage summary from the agent's token cost service
			usage_summary = await agent.token_cost_service.get_usage_summary()

			await websocket.send_json({
				"type": "metrics",
				"tokens": usage_summary.total_tokens,
				"prompt_tokens": usage_summary.total_prompt_tokens,
				"completion_tokens": usage_summary.total_completion_tokens,
				"steps": len(history.history),
				"cost": usage_summary.total_cost,
				"duration": duration_seconds,
				"mode": session["mode"]
			})

			# Also send metrics as log message
			cost_display = f"${usage_summary.total_cost:.4f}" if usage_summary.total_cost > 0 else "$0.0000"
			await websocket.send_json({
				"type": "log",
				"level": "INFO",
				"message": f"\n📊 Metrics: {usage_summary.total_tokens:,} tokens, {cost_display}",
				"timestamp": asyncio.get_event_loop().time()
			})
			if usage_summary.total_prompt_tokens or usage_summary.total_completion_tokens:
				await websocket.send_json({
					"type": "log",
					"level": "INFO",
					"message": f"   Input: {usage_summary.total_prompt_tokens:,} tokens | Output: {usage_summary.total_completion_tokens:,} tokens",
					"timestamp": asyncio.get_event_loop().time()
				})

			# Send agent registration info for AWI mode
			if session["mode"] == "awi":
				from browser_use.agent_registry import agent_registry

				# Get credentials for the target domain
				creds = agent_registry.list_credentials(domain=target_url)

				if creds:
					await websocket.send_json({
						"type": "agent_registry",
						"message": f"📋 Registered AWI agents: {len(creds)}",
						"agents": [{
							"agent_id": cred.agent_id,
							"agent_name": cred.agent_name,
							"domain": cred.domain,
							"awi_name": cred.awi_name,
							"permissions": cred.permissions,
							"created_at": cred.created_at,
							"last_used": cred.last_used,
						} for cred in creds],
						"cli_command": "python -m browser_use.cli_agent_registry list"
					})

					# Also send as log messages
					await websocket.send_json({
						"type": "log",
						"level": "INFO",
						"message": f"\n📋 Registered AWI agents: {len(creds)}",
						"timestamp": asyncio.get_event_loop().time()
					})
					for cred in creds:
						permissions_str = ", ".join(cred.permissions) if cred.permissions else "none"
						await websocket.send_json({
							"type": "log",
							"level": "INFO",
							"message": f"   • {cred.agent_name} ({cred.awi_name})",
							"timestamp": asyncio.get_event_loop().time()
						})
						await websocket.send_json({
							"type": "log",
							"level": "INFO",
							"message": f"     ID: {cred.agent_id}",
							"timestamp": asyncio.get_event_loop().time()
						})
						await websocket.send_json({
							"type": "log",
							"level": "INFO",
							"message": f"     Domain: {cred.domain}",
							"timestamp": asyncio.get_event_loop().time()
						})
						await websocket.send_json({
							"type": "log",
							"level": "INFO",
							"message": f"     Permissions: {permissions_str}",
							"timestamp": asyncio.get_event_loop().time()
						})
					await websocket.send_json({
						"type": "log",
						"level": "INFO",
						"message": f"\n💡 Manage agents: python -m browser_use.cli_agent_registry list",
						"timestamp": asyncio.get_event_loop().time()
					})

		finally:
			# Remove log handlers
			try:
				browser_use_logger.removeHandler(ws_handler)
			except:
				pass

			# Close browser
			try:
				if 'browser' in locals() and browser:
					await browser.kill()
					logger.info("✅ Browser killed")
			except Exception as e:
				logger.warning(f"Failed to kill browser: {e}")

		session["status"] = "completed"

	except WebSocketDisconnect:
		logger.info(f"WebSocket disconnected: {session_id}")
		if session_id in active_sessions:
			active_sessions[session_id]["status"] = "disconnected"

	except Exception as e:
		logger.error(f"Error in live demo {session_id}: {e}", exc_info=True)
		await websocket.send_json({
			"type": "error",
			"message": str(e)
		})

	finally:
		await websocket.close()


# Cleanup old sessions periodically
@router.on_event("startup")
async def cleanup_sessions():
	"""Cleanup sessions older than 30 minutes"""
	async def cleanup_loop():
		while True:
			await asyncio.sleep(300)  # Check every 5 minutes
			current_time = asyncio.get_event_loop().time()

			to_remove = []
			for session_id, session in active_sessions.items():
				if current_time - session.get("created_at", 0) > 1800:  # 30 minutes
					to_remove.append(session_id)

			for session_id in to_remove:
				del active_sessions[session_id]
				logger.info(f"Cleaned up old session: {session_id}")

	asyncio.create_task(cleanup_loop())
