#!/usr/bin/env python3
"""
Full AWI Mode Test with Browser-Use (FIXED VERSION)

This version includes explicit task completion criteria to prevent infinite looping.

Key fixes:
1. Explicit task instructions with numbered steps
2. Clear completion criteria
3. Reduced max_steps to prevent runaway execution
4. Better model (gpt-4o instead of gpt-4o-mini)
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser_use import Agent, Browser
from browser_use.llm import get_default_llm
from dotenv import load_dotenv

load_dotenv()


async def main():
	"""Run the full AWI mode test."""

	print("\n" + "=" * 80)
	print("🚀 FULL AWI MODE TEST - FIXED VERSION")
	print("=" * 80)

	# FIXED: More explicit task with clear completion criteria
	task = """Go to http://localhost:5000 and complete this task step by step:

STEPS:
1. Get the list of blog posts (use AWI API)
2. Identify the 3 most popular posts (sort by views/viewCount)
3. Add exactly ONE comment containing 'Great post!' to each of these 3 posts
4. After successfully adding all 3 comments, call the 'done' action with a summary

IMPORTANT RULES:
- Add only ONE comment per post (no duplicates)
- Only comment on exactly 3 posts (the top 3 by popularity)
- Use the AWI API (awi_execute) for all operations
- Call 'done' action after completing all 3 comments
- DO NOT continue after calling 'done'
"""

	print(f"\n📋 Task: Add comments to top 3 posts")
	print("\n🔧 Configuration:")
	print("   • AWI Mode: ENABLED")
	print("   • Target: http://localhost:5000")
	print("   • Browser: Non-headless")
	print("   • Max Steps: 10 (prevents runaway)")
	print("   • Model: Using DEFAULT_LLM_MODEL from .env")

	print("\n⚠️  IMPORTANT:")
	print("   When the permission dialog appears:")
	print("   1. Type 'y' and press Enter to approve")
	print("   2. Press Enter for default agent name")
	print("   3. Press Enter for default permissions (read,write)")
	print("   4. Type 'y' and press Enter to confirm")

	print("\n" + "=" * 80)
	print("\nStarting test now...")
	print()

	try:
		# Use default LLM from .env configuration
		llm = get_default_llm()

		# Create agent with LLM
		agent = Agent(
			task=task,
			llm=llm,
			browser=Browser(headless=False),
			awi_mode=True,
			max_actions_per_step=3,
			use_vision=True,
		)

		print("✅ Agent created successfully")
		print("🚀 Starting agent run...\n")
		print("=" * 80)
		print("⚠️  WATCH FOR PERMISSION DIALOG!")
		print("=" * 80)
		print()

		# FIXED: Reduced max_steps to prevent infinite execution
		result = await agent.run(max_steps=10)

		# Display results
		print("\n" + "=" * 80)
		print("📊 EXECUTION COMPLETED")
		print("=" * 80)

		print(f"\n✅ Task Status: {'DONE' if result.is_done() else 'NOT COMPLETE'}")
		print(f"📝 Steps Taken: {len(result.history)}")

		# Check if AWI was used
		if agent.awi_manager:
			print("\n" + "=" * 80)
			print("🎉 AWI MODE WAS ACTIVE!")
			print("=" * 80)
			print("\n   The agent used structured API instead of DOM parsing!")

			# Get AWI session statistics
			try:
				state = await agent.get_awi_session_state()
				if state and state.get('success'):
					stats = state.get('statistics', {})
					print(f"\n📊 AWI Session Statistics:")
					print(f"   • Session ID: {state.get('sessionId')}")
					print(f"   • Total Actions: {stats.get('totalActions', 0)}")
					print(f"   • Successful: {stats.get('successfulActions', 0)}")
					print(f"   • Failed: {stats.get('failedActions', 0)}")

					if stats.get('totalActions', 0) > 0:
						success_rate = (stats.get('successfulActions', 0) / stats.get('totalActions', 1)) * 100
						print(f"   • Success Rate: {success_rate:.1f}%")

				# Get action trajectory
				history = await agent.get_awi_action_history(limit=20)
				if history and history.get('success'):
					trajectory = history.get('trajectory', [])
					print(f"\n📜 Action Trajectory ({len(trajectory)} actions):")
					for i, action in enumerate(trajectory, 1):
						status = "✅" if action.get('success') else "❌"
						endpoint = action.get('endpoint', 'N/A')
						method = action.get('method', 'N/A')
						act = action.get('action', 'N/A')
						print(f"   {i:2d}. {status} {act:20s} {method:6s} {endpoint}")

					# Count comment creation actions
					comment_actions = [a for a in trajectory if '/comments' in a.get('endpoint', '')]
					print(f"\n📝 Comments Added: {len(comment_actions)}")

					if len(comment_actions) > 3:
						print(f"   ⚠️  WARNING: More than 3 comments were added!")
					elif len(comment_actions) == 3:
						print(f"   ✅ Perfect! Exactly 3 comments added.")
					else:
						print(f"   ⚠️  Only {len(comment_actions)} comments added (expected 3)")

			except Exception as e:
				print(f"\n⚠️  Could not fetch AWI session details: {e}")

		else:
			print("\n" + "=" * 80)
			print("⚠️  AWI MODE WAS NOT ACTIVATED")
			print("=" * 80)
			print("\n   Possible reasons:")
			print("   • No AWI found at the URL")
			print("   • User declined permission")
			print("   • AWI discovery failed")

		# Show final result
		if result.final_result():
			print(f"\n📄 Final Output:")
			print(f"   {result.final_result()}")

	except KeyboardInterrupt:
		print("\n\n⚠️  Test interrupted by user")
		sys.exit(1)
	except Exception as e:
		print(f"\n\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
		sys.exit(1)

	print("\n" + "=" * 80)
	print("✅ TEST COMPLETED")
	print("=" * 80)

	if agent.awi_manager:
		print("\n🎉 AWI MODE WORKED!")
		print("   Check the statistics above to verify correct behavior.")
	else:
		print("\n⚠️  AWI mode was not activated")

	print()


if __name__ == "__main__":
	print("\n" + "=" * 80)
	print("🧪 BROWSER-USE AWI MODE - FIXED TEST")
	print("=" * 80)

	print("\n📋 Prerequisites Check:")

	# Check OpenAI API key
	if os.getenv('OPENAI_API_KEY'):
		print("   ✅ OPENAI_API_KEY is set")
	else:
		print("   ❌ OPENAI_API_KEY not found - this is required!")
		sys.exit(1)

	print("   ℹ️  Backend server should be running on http://localhost:5000")
	print("   ℹ️  MongoDB should be running")
	print("   ℹ️  Redis should be running")

	print("\n" + "=" * 80)
	print("🔧 Improvements in This Version:")
	print("=" * 80)
	print("""
1. ✅ Explicit task instructions with numbered steps
2. ✅ Clear completion criteria (stop after 3 comments)
3. ✅ Reduced max_steps (10 instead of 20) to prevent runaway
4. ✅ Better model (gpt-4o instead of gpt-4o-mini)
5. ✅ Post-execution verification of comment count
""")

	print("⚠️  IMPORTANT: This requires user interaction!")
	print("   You MUST respond to the permission dialog prompts.")
	print()

	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\n\n⚠️  Test cancelled by user")
		sys.exit(1)
