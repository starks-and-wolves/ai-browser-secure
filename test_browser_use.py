#!/usr/bin/env python3
"""
Browser-Use Test Script

This script demonstrates all three modes of browser-use:
1. Traditional Mode - Standard browser automation
2. Permission Mode - IDE-like security prompts
3. AWI Mode - Fast API-based automation

Usage:
    python test_browser_use.py [mode]

    Modes:
        traditional  - Standard browser automation (default)
        permission   - With user approval prompts
        awi          - AWI mode (requires AWI backend)
        all          - Run all three modes sequentially
"""

# from dotenv import load_dotenv
import asyncio
import os
import sys
from pathlib import Path

# project_root = Path(__file__).parent.absolute()
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))


# Check for .env file
env_file = Path('.env')
if not env_file.exists():
    print("⚠️  No .env file found. Creating one...")
    with open('.env', 'w') as f:
        f.write("# Browser-Use Environment Variables\n")
        f.write("# Get your API key from: https://cloud.browser-use.com/new-api-key\n")
        f.write("#BROWSER_USE_API_KEY=your-key-here\n\n")
        f.write("# Or use OpenAI\n")
        f.write("#OPENAI_API_KEY=your-openai-key-here\n\n")
        f.write("# Or use Anthropic\n")
        f.write("#ANTHROPIC_API_KEY=your-anthropic-key-here\n\n")
        f.write("# Default LLM model\n")
        f.write("DEFAULT_LLM_MODEL=gpt-4o\n")
    print("✅ Created .env file. Please add your API keys and run again.")
    sys.exit(0)

# Import browser-use
try:
    from browser_use import Agent, Browser, BrowserProfile
    from browser_use.llm import get_default_llm
except ImportError:
    print("❌ browser-use not installed")
    print("\nInstall with:")
    print("  uv add browser-use && uv sync")
    print("  # or")
    print("  pip install browser-use")
    sys.exit(1)

# Check for API keys
# load_dotenv()

has_browser_use_key = bool(os.getenv('BROWSER_USE_API_KEY'))
has_openai_key = bool(os.getenv('OPENAI_API_KEY'))
has_anthropic_key = bool(os.getenv('ANTHROPIC_API_KEY'))

if not (has_browser_use_key or has_openai_key or has_anthropic_key):
    print("❌ No API keys found in .env file")
    print("\nPlease add one of:")
    print("  BROWSER_USE_API_KEY=your-key  (get from https://cloud.browser-use.com/new-api-key)")
    print("  OPENAI_API_KEY=your-key")
    print("  ANTHROPIC_API_KEY=your-key")
    sys.exit(1)


def print_section(title: str, emoji: str = "📝"):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"{emoji} {title}")
    print('=' * 70)


async def test_traditional_mode():
    """Test traditional browser automation mode."""
    print_section("Test 1: Traditional Mode", "🎯")
    print("Task: Find the number of stars of the browser-use repo")
    print("Mode: Standard browser automation (DOM parsing, clicking, typing)")

    browser = Browser(headless=False)

    try:
        llm = get_default_llm()
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
        return

    agent = Agent(
        task="Go to github.com/browser-use/browser-use and find the number of stars",
        llm=llm,
        browser=browser,
        max_steps=5,
    )

    print("\n▶️  Starting agent...")
    try:
        history = await agent.run()
        print("\n✅ Traditional mode test completed!")
        print(f"   Steps taken: {len(history.history)}")
        return history
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    finally:
        await browser.kill()


async def test_permission_mode():
    """Test permission mode with user approval prompts."""
    print_section("Test 2: Permission Mode", "🛡️")
    print("Task: Find the number of stars of the browser-use repo (SAME as traditional)")
    print("Mode: User approval required for sensitive actions")
    print("\n⚠️  You will be prompted to approve actions!")
    print("    Type 'yes' to approve, 'no' to deny, 'all-session' to approve all")
    print("\n💡 This test does the SAME task as traditional mode, but with security prompts.")
    print("   Notice how you get approval dialogs before navigation.")

    # Create profile with permission mode enabled
    profile = BrowserProfile(
        require_user_approval=True,
        user_approval_for_navigation=True,
        user_approval_for_sensitive_data=True,
        user_approval_for_file_operations=True,
    )

    browser = Browser(browser_profile=profile, headless=False)

    try:
        llm = get_default_llm()
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
        return

    agent = Agent(
        task="Go to github.com/browser-use/browser-use and find the number of stars",
        llm=llm,
        browser=browser,
        max_steps=5,
    )

    print("\n▶️  Starting agent...")
    try:
        history = await agent.run()
        print("\n✅ Permission mode test completed!")
        print(f"   Steps taken: {len(history.history)}")
        print("\n📊 Delta from traditional mode:")
        print("   • Same task, same steps")
        print("   • BUT: You had to approve each navigation")
        print("   • Perfect for auditing and testing sensitive tasks")
        return history
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    finally:
        await browser.kill()


async def test_permission_mode_advanced():
    """Test permission mode with domain blocking - showcasing extra capabilities."""
    print_section("Test 2b: Permission Mode (Advanced)", "🔒")
    print("Task: Try to visit multiple domains including blocked ones")
    print("Mode: Permission mode + Domain blocking")
    print("\n💡 This showcases permission mode's extra security capabilities:")
    print("   • Block specific domains (e.g., social media)")
    print("   • Pre-approve safe domains")
    print("   • Require approval for everything else")

    # Create profile with advanced security settings
    profile = BrowserProfile(
        require_user_approval=True,
        user_approval_for_navigation=True,
        user_approval_pre_approved_domains=[
            '*.google.com',  # Pre-approve Google
            '*.github.com',  # Pre-approve GitHub
        ],
        prohibited_domains=[
            'facebook.com',  # Block Facebook
            '*.meta.com',    # Block all Meta properties
            'x.com',         # Block X (Twitter)
        ]
    )

    browser = Browser(browser_profile=profile, headless=False)

    try:
        llm = get_default_llm()
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
        return

    agent = Agent(
        task="Try to visit these sites and tell me which ones you could access: google.com, github.com, facebook.com, and example.com",
        llm=llm,
        browser=browser,
        max_steps=8,
    )

    print("\n▶️  Starting agent...")
    print("   Expected behavior:")
    print("   ✅ google.com - Pre-approved (no prompt)")
    print("   ✅ github.com - Pre-approved (no prompt)")
    print("   ❌ facebook.com - BLOCKED (automatic rejection)")
    print("   ⚠️  example.com - Requires approval (not in pre-approved list)")

    try:
        history = await agent.run()
        print("\n✅ Advanced permission mode test completed!")
        print(f"   Steps taken: {len(history.history)}")
        print("\n🎯 Key Security Features Demonstrated:")
        print("   ✓ Domain whitelisting (pre-approved)")
        print("   ✓ Domain blacklisting (blocked)")
        print("   ✓ User approval for unknown domains")
        return history
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    finally:
        await browser.kill()


async def test_awi_mode():
    """Test AWI mode with structured API calls."""
    print_section("Test 3: AWI Mode", "⚡")
    print("Task: Interact with AWI-enabled backend")
    print("Mode: Structured API calls instead of DOM parsing")
    print("\n🌐 Using deployed AWI backend at:")
    print("   https://ai-browser-security.onrender.com")

    # Use deployed backend
    awi_urls = [
        'https://ai-browser-security.onrender.com',
    ]

    awi_url = None
    import aiohttp

    for url in awi_urls:
        try:
            print(f"\n🔍 Checking AWI backend at {url}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{url}/.well-known/llm-text', timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        manifest = await response.json()
                        awi_url = url
                        print(
                            f"✅ AWI backend detected: {manifest.get('awi', {}).get('name', 'Unknown')}")
                        print(
                            f"   Version: {manifest.get('awi', {}).get('version', 'Unknown')}")
                        break
                    else:
                        print(
                            f"   ⚠️  Backend returned status {response.status}")
        except Exception as e:
            print(f"   ⚠️  Not available: {str(e)[:50]}")

    if not awi_url:
        print("\n❌ No AWI backend available")
        print("\n" + "=" * 70)
        print("💡 AWI BACKEND OPTIONS")
        print("=" * 70)
        print("\n🌐 AWI Backend Status:")
        print("   The deployed backend at https://ai-browser-security.onrender.com")
        print("   should be available. If it's not responding:")
        print("   • It may be in sleep mode (first request takes ~1 minute to wake)")
        print("   • Try running the test again in a minute")
        print("   • Check status at: https://ai-browser-security.onrender.com/health")
        print("\n💡 For local development:")
        print("   See TESTING.md for instructions on setting up a local AWI backend")
        print("\n" + "=" * 70)
        return None

    print(f"\n🎯 Using AWI backend: {awi_url}")
    browser = Browser(headless=True)

    try:
        llm = get_default_llm()
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
        return

    agent = Agent(
        task=f"Go to {awi_url} and list the top 3 blog posts, then add a comment to the first one",
        llm=llm,
        browser=browser,
        awi_mode=True,
        max_steps=10,
    )

    print("\n▶️  Starting agent...")
    print("    (First run will show permission dialog)")
    try:
        history = await agent.run()
        print("\n✅ AWI mode test completed!")
        print(f"   Steps taken: {len(history.history)}")

        # Show AWI credentials info
        from browser_use.agent_registry import agent_registry
        creds = agent_registry.list_credentials()
        if creds:
            print(f"\n📋 Registered AWI agents: {len(creds)}")
            print("    Manage with: python -m browser_use.cli_agent_registry list")

        return history
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    finally:
        await browser.kill()


async def main():
    """Main test runner."""
    print_section("Browser-Use Test Script", "🤖")

    # Determine which mode to test
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'traditional'

    valid_modes = ['traditional', 'permission', 'awi', 'all']
    if mode not in valid_modes:
        print(f"❌ Invalid mode: {mode}")
        print(f"   Valid modes: {', '.join(valid_modes)}")
        sys.exit(1)

    print(f"\nRunning mode: {mode}")

    # Show API key status
    print("\n🔑 API Key Status:")
    if has_browser_use_key:
        print("   ✅ BROWSER_USE_API_KEY: Set")
    if has_openai_key:
        print("   ✅ OPENAI_API_KEY: Set")
    if has_anthropic_key:
        print("   ✅ ANTHROPIC_API_KEY: Set")

    try:
        llm = get_default_llm()
        print(
            f"   ✅ Using LLM: {llm.model_name if hasattr(llm, 'model_name') else llm.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ LLM configuration error: {e}")
        sys.exit(1)

    # Run tests
    results = {}

    if mode == 'all':
        modes_to_test = ['traditional', 'permission', 'awi']
    else:
        modes_to_test = [mode]

    for test_mode in modes_to_test:
        if test_mode == 'traditional':
            results['traditional'] = await test_traditional_mode()
        elif test_mode == 'permission':
            results['permission'] = await test_permission_mode()
            results['permission_advanced'] = await test_permission_mode_advanced()
        elif test_mode == 'awi':
            results['awi'] = await test_awi_mode()

    # Print summary
    print_section("Test Summary", "📊")
    for test_name, result in results.items():
        if result is not None:
            display_name = test_name.replace('_', ' ').capitalize()
            print(f"✅ {display_name}: PASSED")
        elif test_name == 'awi' and result is None:
            print(f"⚠️  {test_name.upper()}: SKIPPED (backend not available)")
        else:
            display_name = test_name.replace('_', ' ').capitalize()
            print(f"❌ {display_name}: FAILED")

    print("\n" + "=" * 70)
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("  • Explore examples: examples/")
    print("  • Read docs: docs/awi/")
    print("  • Manage AWI agents: python -m browser_use.cli_agent_registry list")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
