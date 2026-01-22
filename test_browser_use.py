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

import asyncio
import os
import sys
from pathlib import Path

# IMPORTANT: Add project directory to Python path (fixes Windows import issues)
# This ensures the local browser_use folder is found before any installed version
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))

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
    from browser_use.agent.service import Agent
    from browser_use import Browser, BrowserProfile
    from browser_use.llm import get_default_llm
except ImportError:
    print("❌ browser-use not installed")
    print("\n⚠️  IMPORTANT: You must install the LOCAL enhanced version, not PyPI!")
    print("\nCorrect installation steps:")
    print("  1. Activate virtual environment:")
    print("     source .venv/bin/activate   # macOS/Linux")
    print("     .venv\\Scripts\\Activate.ps1  # Windows PowerShell")
    print("\n  2. Install local package in editable mode:")
    print("     uv pip install -e .")
    print("     # or use pip directly:")
    print("     pip install -e .")
    print("\n  3. Verify installation:")
    print("     python -c \"import browser_use; print('✅ Installed')\"")
    print("\nFor more help, see README.md or docs/awi/TROUBLESHOOTING.md")
    sys.exit(1)

# Check for API keys
try:
    from dotenv import load_dotenv  # type: ignore[reportMissingImports]
    load_dotenv()
except ModuleNotFoundError:
    print("⚠️  python-dotenv not installed; skipping .env loading.")
    print("   Install with: uv add python-dotenv && uv sync")

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

    agent = Agent(  # type: ignore[reportGeneralTypeIssues]
        task="Go to github.com/browser-use/browser-use and find the number of stars",
        llm=llm,
        browser=browser,
        max_steps=5,
    )

    print("\n▶️  Starting agent...")
    try:
        history = await agent.run()  # type: ignore[reportGeneralTypeIssues]
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

    agent = Agent(  # type: ignore[reportGeneralTypeIssues]
        task="Go to github.com/browser-use/browser-use and find the number of stars",
        llm=llm,
        browser=browser,
        max_steps=5,
    )

    print("\n▶️  Starting agent...")
    try:
        history = await agent.run()  # type: ignore[reportGeneralTypeIssues]
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

    agent = Agent(  # type: ignore[reportGeneralTypeIssues]
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
        history = await agent.run()  # type: ignore[reportGeneralTypeIssues]
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


async def check_awi_backend_with_retry(url: str, max_retries: int = 12, retry_delay: int = 10):
    """
    Check if AWI backend is available, with retry logic for sleeping backends.

    Args:
        url: Backend URL to check
        max_retries: Maximum number of retry attempts (default: 12 = 2 minutes)
        retry_delay: Seconds to wait between retries (default: 10 seconds)

    Returns:
        tuple: (manifest_dict, success_bool)
    """
    try:
        import aiohttp  # type: ignore[reportMissingImports]
    except ModuleNotFoundError:
        aiohttp = None
    import time

    print(f"🔍 Checking AWI backend at {url}...")

    start_time = time.time()
    is_sleeping = False

    for attempt in range(1, max_retries + 1):
        try:
            timeout_seconds = 15 if attempt == 1 else 30  # Longer timeout after first attempt
            if aiohttp is None:
                print('❌ aiohttp not installed; cannot check AWI backend')
                return None, False
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{url}/.well-known/llm-text',
                    timeout=aiohttp.ClientTimeout(total=timeout_seconds)
                ) as response:
                    if response.status == 200:
                        manifest = await response.json()
                        elapsed = time.time() - start_time

                        if is_sleeping:
                            print(f"\n✅ Backend woke up! (took {elapsed:.1f} seconds)")
                        else:
                            print(f"✅ Backend is online!")

                        print(f"   AWI Name: {manifest.get('awi', {}).get('name', 'Unknown')}")
                        print(f"   Version: {manifest.get('awi', {}).get('version', 'Unknown')}")
                        return manifest, True
                    else:
                        print(f"   ⚠️  Backend returned status {response.status}")
                        return None, False

        except asyncio.TimeoutError:
            elapsed = time.time() - start_time

            if attempt == 1:
                print(f"   ⏰ Backend appears to be sleeping (timeout after {timeout_seconds}s)")
                print(f"   🔄 Waking up backend... (this may take up to 90 seconds)")
                is_sleeping = True

            if attempt < max_retries:
                remaining_time = (max_retries - attempt) * retry_delay
                print(f"   ⏳ Retry {attempt}/{max_retries} - Waiting {retry_delay}s... ({remaining_time}s remaining)")
                await asyncio.sleep(retry_delay)
            else:
                print(f"\n   ❌ Backend did not respond after {elapsed:.0f} seconds")
                return None, False

        except Exception as e:
            error_msg = str(e)
            if 'Cannot connect' in error_msg or 'Connection' in error_msg:
                if attempt == 1:
                    print(f"   ⏰ Connection refused - backend is sleeping")
                    print(f"   🔄 Waking up backend... (this may take up to 90 seconds)")
                    is_sleeping = True

                if attempt < max_retries:
                    remaining_time = (max_retries - attempt) * retry_delay
                    print(f"   ⏳ Retry {attempt}/{max_retries} - Waiting {retry_delay}s... ({remaining_time}s remaining)")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"\n   ❌ Could not connect after {max_retries} attempts")
                    return None, False
            else:
                print(f"   ❌ Unexpected error: {error_msg[:80]}")
                return None, False

    return None, False


async def test_awi_mode():
    """Test AWI mode with structured API calls."""
    print_section("Test 3: AWI Mode", "⚡")
    print("Task: Interact with AWI-enabled backend")
    print("Mode: Structured API calls instead of DOM parsing")
    print("\n🌐 Using deployed AWI backend at:")
    print("   https://ai-browser-security.onrender.com")
    print("\n💡 Note: If the backend is sleeping, it will automatically wake up.")
    print("   This may take up to 90 seconds on the first request.\n")

    # Use deployed backend
    awi_url = 'https://ai-browser-security.onrender.com'

    # Check backend with retry logic (up to 2 minutes)
    manifest, success = await check_awi_backend_with_retry(
        awi_url,
        max_retries=12,  # 12 attempts * 10 seconds = 2 minutes max
        retry_delay=10
    )

    if not success or not manifest:
        print("\n❌ AWI backend is not available")
        print("\n" + "=" * 70)
        print("💡 TROUBLESHOOTING")
        print("=" * 70)
        print("\n🔧 The backend did not respond after multiple retry attempts.")
        print("\n   Possible issues:")
        print("   • Backend service may be down (check https://ai-browser-security.onrender.com)")
        print("   • Network connectivity issues")
        print("   • Firewall blocking the connection")
        print("\n   Next steps:")
        print("   • Check your internet connection")
        print("   • Try accessing the backend URL in a browser")
        print("   • Wait a few minutes and try again")
        print("   • Check TESTING.md for local backend setup")
        print("\n" + "=" * 70)
        return None

    print(f"\n🎯 Using AWI backend: {awi_url}")
    browser = Browser(headless=True)

    try:
        llm = get_default_llm()
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
        return

    agent = Agent(  # type: ignore[reportGeneralTypeIssues]
        task=f"Go to {awi_url} and list the top 3 blog posts, then add a comment 'Great post!' to the first one. After adding the comment, end the process",
        llm=llm,
        browser=browser,
        awi_mode=True,
        max_steps=8,  # Reduced to catch infinite loops faster
    )

    print("\n▶️  Starting agent...")
    print("    (First run will show permission dialog)")
    try:
        history = await agent.run()  # type: ignore[reportGeneralTypeIssues]
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
        print(f"   ✅ Using LLM: {llm.model_name if hasattr(llm, 'model_name') else llm.__class__.__name__}")
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
    # Windows-specific fix: Set event loop policy to support subprocesses
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
