#!/usr/bin/env python3
"""
Automated AWI Mode Test with Verification

This script:
1. Automatically registers with AWI (no manual dialog)
2. Runs the agent to add comments to top 3 posts
3. Verifies that comments were actually added
4. Provides a detailed report
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

import aiohttp
from browser_use import Agent, Browser
from browser_use.llm import get_default_llm
from browser_use.awi.discovery import AWIDiscovery
from browser_use.awi.manager import AWIManager
from dotenv import load_dotenv

load_dotenv()


async def get_top_posts(base_url: str, api_key: str) -> List[Dict[str, Any]]:
	"""Get the top 3 most popular posts."""
	async with aiohttp.ClientSession() as session:
		# Construct URL properly
		url = f"{base_url}/posts" if not base_url.endswith('/') else f"{base_url}posts"

		async with session.get(
			url,
			params={'limit': 100},  # Get enough posts
			headers={'X-Agent-API-Key': api_key}
		) as response:
			if response.status != 200:
				text = await response.text()
				raise Exception(f"Failed to get posts: {response.status} - {text}")

			data = await response.json()
			posts = data.get('posts', [])

			# Sort by views (most popular)
			sorted_posts = sorted(posts, key=lambda p: p.get('views', 0), reverse=True)

			return sorted_posts[:3]


async def verify_comments_added(
	base_url: str,
	api_key: str,
	post_ids: List[str],
	expected_content: str = "Great post!"
) -> Dict[str, Any]:
	"""
	Verify that comments were added to the specified posts.

	Returns:
		Dictionary with verification results
	"""
	results = {
		'total_posts': len(post_ids),
		'posts_with_comments': 0,
		'posts_without_comments': 0,
		'details': []
	}

	async with aiohttp.ClientSession() as session:
		for post_id in post_ids:
			try:
				# Construct URL properly
				url = f"{base_url}/posts/{post_id}/comments" if not base_url.endswith('/') else f"{base_url}posts/{post_id}/comments"

				async with session.get(
					url,
					headers={'X-Agent-API-Key': api_key}
				) as response:
					if response.status != 200:
						results['details'].append({
							'post_id': post_id,
							'status': 'error',
							'message': f"Failed to fetch comments: {response.status}"
						})
						continue

					data = await response.json()
					comments = data.get('comments', [])

					# Check if any comment contains the expected content
					matching_comments = [
						c for c in comments
						if expected_content.lower() in c.get('content', '').lower()
					]

					if matching_comments:
						results['posts_with_comments'] += 1
						results['details'].append({
							'post_id': post_id,
							'status': 'success',
							'comment_count': len(comments),
							'matching_comments': len(matching_comments),
							'latest_comment': matching_comments[-1]
						})
					else:
						results['posts_without_comments'] += 1
						results['details'].append({
							'post_id': post_id,
							'status': 'missing',
							'comment_count': len(comments),
							'message': f"No comments containing '{expected_content}' found"
						})

			except Exception as e:
				results['details'].append({
					'post_id': post_id,
					'status': 'error',
					'message': str(e)
				})

	return results


async def main():
	"""Run the automated AWI test."""

	print("\n" + "=" * 80)
	print("🤖 AUTOMATED AWI MODE TEST WITH VERIFICATION")
	print("=" * 80)

	base_url = "http://localhost:5000"
	task = "Go to http://localhost:5000 and submit reviews saying 'Great post!' on the three most popular blog posts"

	print(f"\n📋 Configuration:")
	print(f"   • Target: {base_url}")
	print(f"   • Task: {task}")
	print(f"   • AWI Mode: ENABLED (automated)")
	print(f"   • Headless: True")
	print(f"   • Model: gpt-4o-mini")

	# Step 1: Discover AWI
	print("\n" + "=" * 80)
	print("Step 1: Discovering AWI")
	print("=" * 80)

	try:
		async with AWIDiscovery() as discovery:
			manifest = await discovery.discover(base_url)
			if not manifest:
				print("❌ No AWI found at target URL")
				return

			print(f"✅ AWI discovered: {manifest.get('awi', {}).get('name', 'Unknown')}")
			print(f"   Version: {manifest.get('awi', {}).get('version', 'Unknown')}")
	except Exception as e:
		print(f"❌ AWI discovery failed: {e}")
		return

	# Step 2: Register agent programmatically
	print("\n" + "=" * 80)
	print("Step 2: Registering Agent (Automated)")
	print("=" * 80)

	# Get API base URL from manifest
	api_base_url = manifest.get('endpoints', {}).get('base', base_url)
	print(f"   API Base URL: {api_base_url}")

	try:
		async with aiohttp.ClientSession() as session:
			awi_manager = AWIManager(manifest=manifest, session=session)

			agent_info = await awi_manager.register_agent(
				agent_name="AutomatedTestAgent",
				permissions=["read", "write"],
				description="Automated test agent for verifying AWI mode"
			)

			api_key = awi_manager.api_key

			print(f"✅ Agent registered successfully")
			print(f"   Agent ID: {agent_info.get('id')}")
			print(f"   API Key: {api_key[:20]}...")
			print(f"   Permissions: {agent_info.get('permissions')}")
	except Exception as e:
		print(f"❌ Agent registration failed: {e}")
		return

	# Step 3: Get top 3 posts before running agent
	print("\n" + "=" * 80)
	print("Step 3: Getting Top 3 Posts")
	print("=" * 80)

	try:
		top_posts = await get_top_posts(api_base_url, api_key)

		if len(top_posts) < 3:
			print(f"⚠️  Only {len(top_posts)} posts found (expected 3)")
		else:
			print(f"✅ Found top 3 posts:")

		post_ids = []
		for i, post in enumerate(top_posts, 1):
			post_id = post.get('_id')
			post_ids.append(post_id)
			print(f"   {i}. {post.get('title', 'Untitled')[:50]}")
			print(f"      ID: {post_id}")
			print(f"      Views: {post.get('views', 0)}")
			print(f"      Comments: {post.get('commentCount', 0)}")
	except Exception as e:
		print(f"❌ Failed to get top posts: {e}")
		return

	# Step 4: Run the agent
	print("\n" + "=" * 80)
	print("Step 4: Running Agent with AWI Mode")
	print("=" * 80)

	try:
		# Monkeypatch the permission dialog to auto-approve
		from browser_use.awi import permission_dialog

		original_show_dialog = permission_dialog.show_permission_dialog

		async def auto_approve_dialog(manifest, base_url):
			"""Auto-approve the permission dialog."""
			print("🤖 Auto-approving AWI registration...")
			return {
				'approved': True,
				'agent_name': 'AutomatedTestAgent',
				'permissions': ['read', 'write']
			}

		permission_dialog.show_permission_dialog = auto_approve_dialog

		# Create and run agent
		agent = Agent(
			task=task,
			llm=get_default_llm(),
			browser=Browser(headless=True),
			awi_mode=True,
			max_actions_per_step=3,
		)

		print("✅ Agent created")
		print("🚀 Starting agent execution...")

		result = await agent.run(max_steps=15)

		# Restore original dialog
		permission_dialog.show_permission_dialog = original_show_dialog

		print(f"\n✅ Agent execution completed")
		print(f"   Status: {'DONE' if result.is_done() else 'NOT COMPLETE'}")
		print(f"   Steps taken: {len(result.history)}")

		# Check if AWI was used
		if agent.awi_manager:
			print(f"   AWI Mode: ✅ Active")
		else:
			print(f"   AWI Mode: ⚠️  Not activated")

	except Exception as e:
		print(f"❌ Agent execution failed: {e}")
		import traceback
		traceback.print_exc()
		return

	# Step 5: Verify comments were added
	print("\n" + "=" * 80)
	print("Step 5: Verifying Comments Added")
	print("=" * 80)

	try:
		verification = await verify_comments_added(api_base_url, api_key, post_ids)

		print(f"\n📊 Verification Results:")
		print(f"   Total posts checked: {verification['total_posts']}")
		print(f"   ✅ Posts with comments: {verification['posts_with_comments']}")
		print(f"   ❌ Posts without comments: {verification['posts_without_comments']}")

		print(f"\n📝 Detailed Results:")
		for i, detail in enumerate(verification['details'], 1):
			status_icon = {
				'success': '✅',
				'missing': '❌',
				'error': '⚠️'
			}.get(detail['status'], '❓')

			print(f"\n   Post {i}: {status_icon} {detail['status'].upper()}")
			print(f"      ID: {detail['post_id']}")

			if detail['status'] == 'success':
				print(f"      Total comments: {detail['comment_count']}")
				print(f"      Matching comments: {detail['matching_comments']}")
				latest = detail['latest_comment']
				print(f"      Latest: \"{latest.get('content', '')[:60]}...\"")
				print(f"      Author: {latest.get('authorName', 'Unknown')}")
			elif detail['status'] == 'missing':
				print(f"      Total comments: {detail['comment_count']}")
				print(f"      Issue: {detail['message']}")
			else:
				print(f"      Error: {detail['message']}")

		# Final verdict
		print("\n" + "=" * 80)
		print("🎯 FINAL VERDICT")
		print("=" * 80)

		success_rate = (verification['posts_with_comments'] / verification['total_posts']) * 100

		if verification['posts_with_comments'] == verification['total_posts']:
			print("\n✅ TEST PASSED!")
			print(f"   All {verification['total_posts']} posts have comments added.")
			print(f"   Success rate: 100%")
		elif verification['posts_with_comments'] > 0:
			print(f"\n⚠️  TEST PARTIALLY PASSED")
			print(f"   {verification['posts_with_comments']}/{verification['total_posts']} posts have comments.")
			print(f"   Success rate: {success_rate:.1f}%")
		else:
			print("\n❌ TEST FAILED")
			print(f"   No comments were added to any post.")
			print(f"   Success rate: 0%")

	except Exception as e:
		print(f"\n❌ Verification failed: {e}")
		import traceback
		traceback.print_exc()

	print("\n" + "=" * 80)


if __name__ == "__main__":
	print("\n" + "=" * 80)
	print("🧪 AUTOMATED AWI MODE TEST")
	print("=" * 80)

	# Check prerequisites
	print("\n📋 Prerequisites:")
	if os.getenv('OPENAI_API_KEY'):
		print("   ✅ OPENAI_API_KEY is set")
	else:
		print("   ❌ OPENAI_API_KEY not set")
		sys.exit(1)

	print("   ℹ️  Ensure backend is running on http://localhost:5000")
	print("   ℹ️  (Backend manages its own MongoDB and Redis internally)")

	print("\n🎯 This test will:")
	print("   1. Discover AWI at localhost:5000")
	print("   2. Register agent automatically (no dialog)")
	print("   3. Run agent to add comments to top 3 posts")
	print("   4. Verify comments were actually added")
	print("   5. Provide detailed success/failure report")

	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\n\n⚠️  Test interrupted by user")
		sys.exit(1)
