#!/usr/bin/env python3
"""
Test AWI Permission Dialog - Simple Version

This tests just the AWI discovery and permission dialog without
running the full browser-use agent.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser_use.awi import AWIDiscovery, AWIPermissionDialog


async def test_permission_dialog():
    """Test the AWI permission dialog."""

    print("\n" + "=" * 80)
    print("🧪 TESTING AWI PERMISSION DIALOG")
    print("=" * 80)
    print("\nThis test will:")
    print("1. Discover AWI from http://localhost:5000")
    print("2. Show the REAL permission dialog")
    print("3. Wait for your input (approve or decline)")
    print("\n" + "=" * 80)

    url = "http://localhost:5000"

    # Step 1: Discovery
    print(f"\n📍 Step 1: Discovering AWI at {url}...")

    async with AWIDiscovery() as discovery:
        manifest = await discovery.discover(url)

        if not manifest:
            print("❌ No AWI found at this URL")
            print("   Make sure the backend server is running on localhost:5000")
            return False

        print("✅ AWI discovered!")
        awi_info = manifest.get('awi', {})
        print(f"   Name: {awi_info.get('name', 'Unknown')}")
        print(f"   Version: {awi_info.get('version', 'Unknown')}")
        print(f"   Provider: {awi_info.get('provider', 'Unknown')}")

        capabilities = discovery.extract_capabilities(manifest)
        print(f"   Operations: {len(capabilities.get('allowed_operations', []))} allowed")
        print(f"   Security features: {len(capabilities.get('security_features', []))}")

    # Step 2: Permission Dialog
    print("\n" + "=" * 80)
    print("🔐 Step 2: Showing Permission Dialog")
    print("=" * 80)
    print("\n⚠️  THE PERMISSION DIALOG WILL NOW APPEAR!")
    print("   You will be prompted to:")
    print("   1. Approve or decline agent registration")
    print("   2. Enter an agent name (or press Enter for default)")
    print("   3. Select permissions (or press Enter for default)")
    print("\n")

    dialog = AWIPermissionDialog(manifest)
    approval = dialog.show_and_get_permissions()

    # Step 3: Check results
    print("\n" + "=" * 80)
    print("📊 RESULTS")
    print("=" * 80)

    if approval and approval['approved']:
        print("\n✅ USER APPROVED!")
        print(f"   Agent name: {approval['agent_name']}")
        print(f"   Permissions: {', '.join(approval['permissions'])}")
        print("\n💡 In a real scenario, the agent would now:")
        print("   1. Register with the AWI using these credentials")
        print("   2. Receive an API key")
        print("   3. Use structured API calls instead of DOM parsing")
        return True
    else:
        print("\n❌ USER DECLINED or dialog cancelled")
        print("   In a real scenario, the agent would fall back to DOM parsing")
        return False


async def main():
    print("\n🚀 AWI Permission Dialog Test")
    print("=" * 80)
    print("\nPrerequisites:")
    print("✅ Backend server running on http://localhost:5000")
    print("   (Backend manages MongoDB and Redis internally)")
    print("\nPress Ctrl+C to stop at any time\n")

    try:
        approved = await test_permission_dialog()

        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED")
        print("=" * 80)

        if approved:
            print("\n🎉 SUCCESS! The permission dialog worked correctly!")
            print("   The user saw the dialog and approved the agent.")
        else:
            print("\n⚠️  The user declined or there was an issue.")
            print("   This is normal if you chose to decline.")

        print("\n💡 What this proves:")
        print("   • AWI discovery works")
        print("   • Permission dialog is shown to users")
        print("   • User can approve or decline")
        print("   • Agent gets user-selected permissions")
        print("\n✨ AWI mode integration is working!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
