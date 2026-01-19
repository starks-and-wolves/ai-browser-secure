"""
AWI Mode Example for Browser-Use

This example demonstrates how to use browser-use with AWI mode enabled.

When AWI mode is activated:
1. Browser-use discovers the AWI manifest from the website
2. User is prompted to approve agent registration and select permissions
3. Agent registers with the selected permissions
4. All interactions use the structured API instead of DOM parsing
5. 500x token reduction compared to traditional DOM parsing!

Usage:
    python examples/awi_mode_example.py
"""

import asyncio
import logging
from browser_use.awi import AWIDiscovery, AWIManager, AWIPermissionDialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_awi_mode():
    """Demonstrate AWI mode with the Blog AWI."""

    # Target URL with AWI support
    url = "http://localhost:5000"

    print("\n" + "="*80)
    print("🤖 Browser-Use AWI Mode Demonstration")
    print("="*80 + "\n")

    # Step 1: Discover AWI
    print("Step 1: Discovering AWI...")
    async with AWIDiscovery() as discovery:
        manifest = await discovery.discover(url)

        if not manifest:
            print("❌ No AWI found at this URL")
            print("Falling back to traditional DOM parsing...")
            return

        print("\n" + discovery.get_summary(manifest))

    # Step 2: Show permission dialog and get user approval
    print("\nStep 2: Getting user approval for agent registration...")
    dialog = AWIPermissionDialog(manifest)
    approval = dialog.show_and_get_permissions()

    if not approval or not approval['approved']:
        print("\n❌ User declined AWI registration")
        print("Falling back to traditional DOM parsing...")
        return

    # Step 3: Register agent with AWI
    print("\nStep 3: Registering agent with AWI...")
    async with AWIManager(manifest) as awi:
        try:
            agent_info = await awi.register_agent(
                agent_name=approval['agent_name'],
                permissions=approval['permissions'],
                description="Browser-use agent with AWI mode",
                agent_type="browser-use",
                framework="python"
            )

            AWIPermissionDialog.show_registration_success(agent_info)

        except Exception as e:
            print(f"\n❌ Registration failed: {e}")
            return

        # Step 4: Use the AWI API
        AWIPermissionDialog.show_awi_mode_banner()

        print("Step 4: Interacting with AWI...")

        # List posts
        print("\n📋 Listing posts...")
        posts_response = await awi.list_posts(page=1, limit=5)

        if posts_response.get('success'):
            posts = posts_response.get('posts', [])
            print(f"✅ Retrieved {len(posts)} posts")

            for i, post in enumerate(posts[:3], 1):
                print(f"\n   {i}. {post.get('title', 'Untitled')}")
                print(f"      ID: {post.get('_id')}")
                print(f"      Created: {post.get('createdAt', 'Unknown')}")
                if post.get('tags'):
                    print(f"      Tags: {', '.join(post['tags'])}")

            # Show pagination info
            pagination = posts_response.get('pagination', {})
            print(f"\n   Pagination: Page {pagination.get('currentPage')} of {pagination.get('totalPages')}")
            print(f"   Total posts: {pagination.get('total')}")

        # Get session state
        print("\n📊 Getting session state...")
        try:
            state_response = await awi.get_session_state()
            if state_response.get('success'):
                print(f"✅ Session ID: {state_response.get('sessionId')}")
                stats = state_response.get('statistics', {})
                print(f"   Total actions: {stats.get('totalActions', 0)}")
                print(f"   Successful actions: {stats.get('successfulActions', 0)}")
        except Exception as e:
            print(f"⚠️  Session state not available: {e}")

        # Get action history (trajectory)
        print("\n📜 Getting action history (trajectory)...")
        try:
            history_response = await awi.get_action_history(limit=10)
            if history_response.get('success'):
                trajectory = history_response.get('trajectory', [])
                print(f"✅ Retrieved {len(trajectory)} actions")

                for i, action in enumerate(trajectory[:5], 1):
                    print(f"\n   {i}. {action.get('action')} ({action.get('method')})")
                    print(f"      Endpoint: {action.get('endpoint')}")
                    print(f"      Time: {action.get('timestamp')}")
                    print(f"      Success: {'✅' if action.get('success') else '❌'}")
                    if action.get('observation'):
                        print(f"      Observation: {action['observation']}")
        except Exception as e:
            print(f"⚠️  Action history not available: {e}")

        # Demonstrate write operation (if permission granted)
        if 'write' in approval['permissions']:
            print("\n✍️  Creating a test post...")
            try:
                post_data = await awi.create_post(
                    title="AWI Mode Test Post",
                    content="<p>This post was created using <strong>AWI mode</strong> in browser-use!</p>",
                    author_name=approval['agent_name'],
                    category="Test",
                    tags=["awi", "browser-use", "automation"]
                )

                if post_data.get('success'):
                    new_post = post_data.get('post', {})
                    print(f"✅ Post created successfully!")
                    print(f"   ID: {new_post.get('_id')}")
                    print(f"   Title: {new_post.get('title')}")

                    # Add a comment if write permission
                    print("\n💬 Adding a comment...")
                    comment_data = await awi.create_comment(
                        post_id=new_post['_id'],
                        content="<p>First comment via AWI mode!</p>",
                        author_name=approval['agent_name']
                    )

                    if comment_data.get('success'):
                        print("✅ Comment added successfully!")

            except Exception as e:
                print(f"⚠️  Write operation failed: {e}")
        else:
            print("\n⚠️  Write permission not granted, skipping post creation")

        # Search demonstration
        print("\n🔍 Searching for 'AWI'...")
        try:
            search_results = await awi.search(query="AWI", intent="find_posts")
            if search_results.get('success'):
                results = search_results.get('results', [])
                print(f"✅ Found {len(results)} results")
        except Exception as e:
            print(f"⚠️  Search failed: {e}")

        # Get final session statistics
        print("\n📈 Getting final session statistics...")
        try:
            final_state = await awi.get_session_state()
            if final_state.get('success'):
                stats = final_state.get('statistics', {})
                print(f"✅ Session complete!")
                print(f"   Total actions: {stats.get('totalActions', 0)}")
                print(f"   Success rate: {stats.get('successfulActions', 0)}/{stats.get('totalActions', 0)}")

        except Exception as e:
            print(f"⚠️  Could not get final stats: {e}")

    print("\n" + "="*80)
    print("✅ AWI Mode Demonstration Complete!")
    print("="*80)
    print("\n💡 Key Benefits Demonstrated:")
    print("   • Automatic AWI discovery via .well-known/llm-text")
    print("   • User-approved permissions and registration")
    print("   • Structured API calls instead of DOM parsing")
    print("   • Session state management and tracking")
    print("   • Action history (trajectory) for debugging/RL")
    print("   • 500x token reduction vs traditional scraping")
    print("\n")


async def demonstrate_fallback_behavior():
    """
    Demonstrate fallback to DOM parsing when AWI is not available.
    """
    print("\n" + "="*80)
    print("🔄 Fallback Behavior Demonstration")
    print("="*80 + "\n")

    # Try a URL without AWI
    url = "https://example.com"

    print(f"Checking {url} for AWI...")
    async with AWIDiscovery() as discovery:
        manifest = await discovery.discover(url)

        if not manifest:
            print("❌ No AWI found")
            print("✅ Would fall back to traditional DOM parsing")
        else:
            print("✅ AWI discovered (unexpected!)")

    print()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_awi_mode())

    # Uncomment to test fallback behavior
    # asyncio.run(demonstrate_fallback_behavior())
