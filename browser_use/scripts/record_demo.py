"""
Demo Recording Script

Records browser-use agent execution trajectories for the demo UI.
Creates trajectory JSON, screenshots, and metadata for each demo.

Usage:
    python browser_use/scripts/record_demo.py \
        --task "Find posts about browser-use on r/programming" \
        --output ./demos/reddit-search-traditional \
        --mode traditional \
        --max-steps 30
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
from typing import Literal
import sys

# Add parent directory to path to import browser_use
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import get_default_llm

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def record_demo(
	task: str,
	output_dir: Path,
	mode: Literal["traditional", "awi", "permission"] = "traditional",
	max_steps: int = 30,
	headless: bool = False,
) -> dict:
	"""
	Record a demo execution and save trajectory.

	Args:
		task: Task for the agent to perform
		output_dir: Directory to save outputs
		mode: Execution mode (traditional, awi, permission)
		max_steps: Maximum steps for execution
		headless: Run browser in headless mode

	Returns:
		Dictionary with recording metadata
	"""
	logger.info(f"Recording demo: {mode} mode")
	logger.info(f"Task: {task}")
	logger.info(f"Output: {output_dir}")

	# Create output directory
	output_dir.mkdir(parents=True, exist_ok=True)

	# Configure browser profile with video recording
	video_output_dir = output_dir / "videos"
	video_output_dir.mkdir(parents=True, exist_ok=True)

	profile_kwargs = {
		"headless": headless,
		"video_output_dir": video_output_dir,  # Enable video recording
		"video_framerate": 2,  # 2 FPS for smaller file size
	}

	# Add mode-specific configuration
	if mode == "permission":
		profile_kwargs.update({
			"require_user_approval": True,
			"user_approval_for_navigation": True,
			"user_approval_pre_approved_domains": ['*.google.com', '*.github.com', '*.reddit.com'],
		})

	profile = BrowserProfile(**profile_kwargs)
	browser = Browser(browser_profile=profile)

	# Get LLM
	try:
		llm = get_default_llm()
		logger.info(f"Using LLM: {llm}")
	except Exception as e:
		logger.error(f"Failed to get LLM: {e}")
		logger.error("Make sure OPENAI_API_KEY or ANTHROPIC_API_KEY is set in environment")
		return {"error": str(e)}

	# Create agent
	agent_kwargs = {
		"task": task,
		"llm": llm,
		"browser": browser,
		"max_steps": max_steps,
	}

	if mode == "awi":
		agent_kwargs["awi_mode"] = True

	agent = Agent(**agent_kwargs)

	# Run agent
	logger.info(f"Starting agent execution (max {max_steps} steps)...")
	try:
		history = await agent.run()
		logger.info(f"✅ Execution completed: {len(history.history)} steps")
	except Exception as e:
		logger.error(f"❌ Execution failed: {e}")
		await browser.kill()
		return {"error": str(e)}
	finally:
		await browser.kill()

	# Save trajectory JSON
	trajectory_path = output_dir / "trajectory.json"
	logger.info(f"Saving trajectory to {trajectory_path}")

	# Convert history to dict (using model_dump)
	trajectory_data = {
		"history": [item.model_dump() for item in history.history],
		"final_result": history.final_result.model_dump() if history.final_result else None,
		"errors": history.errors if hasattr(history, 'errors') else [],
	}

	with open(trajectory_path, 'w', encoding='utf-8') as f:
		json.dump(trajectory_data, f, indent=2, ensure_ascii=False)

	logger.info(f"✅ Trajectory saved: {trajectory_path}")

	# Calculate metrics
	total_steps = len(history.history)
	total_duration = 0
	total_tokens = 0

	for item in history.history:
		if item.metadata:
			total_duration += item.metadata.duration_seconds

		# Estimate tokens (rough approximation)
		if item.model_output:
			# Count characters in model output and divide by 4 (rough token estimate)
			model_output_str = json.dumps(item.model_output.model_dump())
			total_tokens += len(model_output_str) // 4

	# Rough cost estimate (assumes GPT-4 pricing: ~$0.01/1K tokens)
	estimated_cost = (total_tokens / 1000) * 0.01

	# Find video file (if recorded)
	video_url = None
	video_dir = output_dir / "videos"
	if video_dir.exists():
		video_files = list(video_dir.glob("*.webm"))
		if video_files:
			video_url = f"/demos/{output_dir.name}/videos/{video_files[0].name}"
			logger.info(f"✅ Video recorded: {video_files[0]}")

	metadata = {
		"id": output_dir.name,
		"title": f"{task[:50]}... - {mode.capitalize()} Mode",
		"description": f"Recorded demo: {task}",
		"mode": mode,
		"task": task,
		"metrics": {
			"steps": total_steps,
			"tokens": total_tokens,
			"cost": round(estimated_cost, 3),
			"duration": round(total_duration, 1)
		},
		"trajectory_url": f"/demos/{output_dir.name}/trajectory.json",
		"video_url": video_url,  # Include video URL if available
		"recording_date": str(Path(trajectory_path).stat().st_mtime),
	}

	# Save metadata
	metadata_path = output_dir / "metadata.json"
	with open(metadata_path, 'w', encoding='utf-8') as f:
		json.dump(metadata, f, indent=2)

	logger.info(f"✅ Metadata saved: {metadata_path}")
	logger.info(f"📊 Metrics: {total_steps} steps, {total_tokens} tokens, ${estimated_cost:.3f}, {total_duration:.1f}s")

	return metadata


async def main():
	parser = argparse.ArgumentParser(description="Record browser-use demo")
	parser.add_argument("--task", required=True, help="Task for the agent")
	parser.add_argument("--output", required=True, help="Output directory")
	parser.add_argument(
		"--mode",
		choices=["traditional", "awi", "permission"],
		default="traditional",
		help="Execution mode"
	)
	parser.add_argument("--max-steps", type=int, default=30, help="Max steps")
	parser.add_argument("--headless", action="store_true", help="Run headless")

	args = parser.parse_args()

	output_dir = Path(args.output)

	metadata = await record_demo(
		task=args.task,
		output_dir=output_dir,
		mode=args.mode,
		max_steps=args.max_steps,
		headless=args.headless,
	)

	if "error" in metadata:
		logger.error(f"Recording failed: {metadata['error']}")
		sys.exit(1)
	else:
		logger.info("✅ Recording complete!")
		logger.info(f"Output: {output_dir}")


if __name__ == "__main__":
	asyncio.run(main())
