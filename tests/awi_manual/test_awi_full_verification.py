#!/usr/bin/env python3
"""
Full AWI Mode Test with Verification

This test:
1. Automatically provides permission dialog responses
2. Runs the agent to submit reviews on top 3 popular posts
3. Verifies that comments were actually added by querying the backend
4. Checks that comments were made by the registered agent
"""

import asyncio
import sys
import os
import requests
from pathlib import Path
from unittest.mock import patch
import json

sys.path.insert(0, str(Path(__file__).parent))

from browser_use import Agent, Browser
from browser_use.llm import get_default_llm
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:5000"
API_BASE = f"{BACKEND_URL}/api/agent"


def get_top_posts_by_views(limit=3):
    """Get top posts by view count from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/posts", params={"sort": "views", "limit": limit})
        response.raise_for_status()
        data = response.json()
        # API returns {success: true, data: [...]}
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data
    except Exception as e:
        print(f"❌ Failed to fetch posts: {e}")
        return None


def get_post_comments(post_id):
    """Get all comments for a specific post."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/comments/post/{post_id}")
        response.raise_for_status()
        data = response.json()
        # API returns {success: true, data: [...]}
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data
    except Exception as e:
        print(f"❌ Failed to fetch comments for post {post_id}: {e}")
        return None


def verify_agent_comments(agent_id, expected_post_ids):
    """
    Verify that the agent added 'Great post!' comments to the expected posts.

    Returns:
        dict: Verification results with success status and details
    """
    results = {
        'success': True,
        'posts_checked': 0,
        'comments_found': 0,
        'missing_comments': [],
        'details': []
    }

    print("\n" + "=" * 80)
    print("🔍 VERIFICATION: Checking for Agent Comments")
    print("=" * 80)

    for post_id in expected_post_ids:
        results['posts_checked'] += 1

        comments = get_post_comments(post_id)
        if comments is None:
            results['success'] = False
            results['missing_comments'].append(post_id)
            results['details'].append({
                'post_id': post_id,
                'status': 'failed_to_fetch',
                'message': 'Could not fetch comments'
            })
            print(f"\n❌ Post {post_id}: Failed to fetch comments")
            continue

        # Find comment with "Great post!" from this agent
        agent_comment = None
        for comment in comments:
            # Check if comment content contains "Great post!" (case-insensitive)
            content = comment.get('content', '').lower()
            if 'great post' in content:
                # Check if it's from our agent (check agentId if available)
                if comment.get('agentId') == agent_id or comment.get('_agentId') == agent_id:
                    agent_comment = comment
                    break
                # If no agentId field, check authorName or metadata
                elif 'agent' in comment.get('authorName', '').lower():
                    agent_comment = comment
                    break

        if agent_comment:
            results['comments_found'] += 1
            results['details'].append({
                'post_id': post_id,
                'status': 'success',
                'comment_id': agent_comment.get('_id'),
                'content': agent_comment.get('content'),
                'author': agent_comment.get('authorName')
            })
            print(f"\n✅ Post {post_id}: Comment found!")
            print(f"   Comment ID: {agent_comment.get('_id')}")
            print(f"   Content: {agent_comment.get('content')[:50]}...")
            print(f"   Author: {agent_comment.get('authorName')}")
        else:
            results['success'] = False
            results['missing_comments'].append(post_id)
            results['details'].append({
                'post_id': post_id,
                'status': 'missing',
                'message': f'No "Great post!" comment from agent found (found {len(comments)} total comments)'
            })
            print(f"\n❌ Post {post_id}: No agent comment found")
            print(f"   Total comments on post: {len(comments)}")
            if comments:
                print(f"   Existing comments:")
                for c in comments[:3]:
                    print(f"     - {c.get('content', '')[:40]}... by {c.get('authorName', 'Unknown')}")

    return results


async def main():
    """Run the full automated test with verification."""

    print("\n" + "=" * 80)
    print("🧪 AUTOMATED AWI MODE TEST WITH VERIFICATION")
    print("=" * 80)

    # Check backend is running
    print("\n📋 Pre-flight checks:")
    try:
        response = requests.get(f"{BACKEND_URL}/.well-known/llm-text", timeout=5)
        response.raise_for_status()
        print("   ✅ Backend is running and AWI is discoverable")
    except Exception as e:
        print(f"   ❌ Backend is not accessible: {e}")
        print(f"   💡 Make sure backend is running: cd backend && npm run dev")
        return False

    # Get initial top 3 posts for reference
    print("\n📊 Fetching top 3 posts by view count...")
    top_posts = get_top_posts_by_views(3)
    if not top_posts:
        print("   ❌ Could not fetch posts from backend")
        return False

    print(f"   ✅ Found {len(top_posts)} posts")
    for i, post in enumerate(top_posts, 1):
        print(f"   {i}. {post.get('title', 'Untitled')} (ID: {post['_id']}, Views: {post.get('views', 0)})")

    expected_post_ids = [post['_id'] for post in top_posts]

    task = "Go to http://localhost:5000 and submit reviews saying 'Great post!' on the three most popular blog posts"

    print(f"\n🎯 Task: {task}")
    print("\n🔧 Configuration:")
    print("   • Model: gpt-4o")
    print("   • AWI Mode: ENABLED")
    print("   • Headless: TRUE")
    print("   • Max Steps: 15")
    print("   • Permissions: read,write")

    print("\n🔄 Mocking permission dialog inputs...")

    # Mock input responses: approve, default name, read,write permissions, confirm
    responses = iter(['y', '', 'read,write', 'y'])

    def mock_input(prompt=''):
        """Mock input function that returns pre-defined responses."""
        response = next(responses, '')
        print(f"{prompt}{response}")
        return response

    agent = None
    agent_id = None
    history = None

    try:
        # Create agent with AWI mode enabled
        print("\n📦 Creating agent...")

        agent = Agent(
            task=task,
            llm=get_default_llm(),
            browser=Browser(headless=True),
            awi_mode=True,
        )

        print("✅ Agent created")

        # Run agent with mocked input (permission dialog happens during run())
        print("\n🚀 Starting agent execution...")
        print("=" * 80)

        with patch('builtins.input', side_effect=mock_input):
            history = await agent.run(max_steps=15)

        # Capture agent ID after registration
        if hasattr(agent, 'awi_manager') and agent.awi_manager:
            agent_id = agent.awi_manager.agent_info.get('id')
            print(f"✅ Agent registered with ID: {agent_id}")
        else:
            print("⚠️  Warning: No AWI manager found, verification may fail")

        print("\n" + "=" * 80)
        print("✅ AGENT EXECUTION COMPLETED")
        print("=" * 80)

        # Print execution summary
        result = history.final_result()
        print(f"\n📊 Execution Summary:")
        print(f"   • Steps taken: {len(history)}")
        print(f"   • Final result: {result}")

        # Check if AWI was used
        if hasattr(agent, 'awi_manager') and agent.awi_manager:
            print(f"\n✅ AWI Mode was active")
            print(f"   • Base URL: {agent.awi_manager.base_url}")
            print(f"   • Agent ID: {agent.awi_manager.agent_info.get('id')}")

            # Count action types
            awi_actions = 0
            browser_actions = 0
            action_details = []

            for item in history:
                if hasattr(item, 'action') and item.action:
                    action_name = type(item.action).__name__
                    if 'awi_execute' in str(action_name).lower():
                        awi_actions += 1
                        # Get action details
                        if hasattr(item.action, '__dict__'):
                            action_details.append({
                                'type': 'awi_execute',
                                'operation': getattr(item.action, 'operation', 'unknown'),
                                'endpoint': getattr(item.action, 'endpoint', 'unknown'),
                                'method': getattr(item.action, 'method', 'unknown')
                            })
                    elif action_name in ['NavigateAction', 'ClickAction', 'TypeAction', 'ScrollAction']:
                        browser_actions += 1

            print(f"\n📈 Action Statistics:")
            print(f"   • AWI API calls: {awi_actions}")
            print(f"   • Browser actions: {browser_actions}")

            if action_details:
                print(f"\n📋 AWI Actions Taken:")
                for i, action in enumerate(action_details, 1):
                    print(f"   {i}. {action['operation']}: {action['method']} {action['endpoint']}")

            if awi_actions > 0 and browser_actions == 0:
                print(f"\n✅ PERFECT! Agent used ONLY AWI API calls")
            elif awi_actions > 0:
                print(f"\n⚠️  Mixed: Agent used both AWI and browser actions")
            else:
                print(f"\n❌ Problem: Agent didn't use AWI execute action")
        else:
            print(f"\n❌ AWI MODE WAS NOT ACTIVATED")
            return False

        # Wait a moment for backend to process
        print("\n⏳ Waiting 2 seconds for backend to process...")
        await asyncio.sleep(2)

        # NOW VERIFY THE RESULTS
        verification_results = verify_agent_comments(agent_id, expected_post_ids)

        # Print verification summary
        print("\n" + "=" * 80)
        print("📊 VERIFICATION RESULTS")
        print("=" * 80)
        print(f"\n✓ Posts checked: {verification_results['posts_checked']}")
        print(f"✓ Comments found: {verification_results['comments_found']}")
        print(f"✓ Missing comments: {len(verification_results['missing_comments'])}")

        if verification_results['success']:
            print(f"\n🎉 SUCCESS! All {verification_results['posts_checked']} posts have agent comments!")
            return True
        else:
            print(f"\n❌ VERIFICATION FAILED!")
            print(f"\nPosts missing comments:")
            for post_id in verification_results['missing_comments']:
                print(f"   • {post_id}")

            # Debug information
            print(f"\n🔍 Debug Information:")
            print(f"   • Agent ID: {agent_id}")
            print(f"   • Expected post IDs: {expected_post_ids}")
            print(f"\n💡 Possible reasons:")
            print(f"   1. Agent didn't complete the task successfully")
            print(f"   2. Agent used wrong post IDs")
            print(f"   3. Comments failed validation on backend")
            print(f"   4. Agent sent empty body in POST request")

            # Show what the agent actually did
            print(f"\n📋 Agent Actions (for debugging):")
            for detail in verification_results['details']:
                print(f"   Post {detail['post_id']}: {detail['status']}")
                if 'message' in detail:
                    print(f"      → {detail['message']}")

            return False

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 BROWSER-USE AWI MODE - FULL TEST WITH VERIFICATION")
    print("=" * 80)

    print("\n📋 Prerequisites:")
    if not os.getenv("OPENAI_API_KEY"):
        print("   ❌ OPENAI_API_KEY not set")
        sys.exit(1)
    print("   ✅ OPENAI_API_KEY is set")
    print("   ℹ️  Backend must be running on http://localhost:5000")
    print("   ℹ️  MongoDB must be running")

    print("\n" + "=" * 80)

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
