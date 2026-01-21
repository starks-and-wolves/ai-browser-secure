# Enhanced Browser-Use Testing Guide

This guide explains how to test all features of the enhanced browser-use version using the included test script.

> **Note:** This is for the enhanced browser-use version with AWI support. For the official package, visit [browser-use/browser-use](https://github.com/browser-use/browser-use).

## Quick Start

```bash
# Run the test script
python test_browser_use.py

# Or specify a mode
python test_browser_use.py traditional    # Standard browser automation
python test_browser_use.py permission     # With user approval prompts
python test_browser_use.py awi            # AWI mode (fast API calls)
python test_browser_use.py all            # Run all tests
```

## First Time Setup

### 1. Check Python Version

```bash
python --version
# Should be Python 3.11 or higher
```

### 2. Install the Enhanced Version

```bash
# Install local package in editable mode (REQUIRED for enhanced version)
uv pip install -e .

# Or with all optional dependencies
uv pip install -e ".[all]"
```

**⚠️ Critical:** Do NOT run `uv add browser-use` or `pip install browser-use` - this will install the original package from PyPI instead of the enhanced version!

### 3. Install Chromium

```bash
uv run browser-use install
```

### 4. Configure API Keys

The test script will create a `.env` file for you on first run. Edit it and add your API key:

```bash
# Choose one of these LLM providers:
OPENAI_API_KEY=your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here
# BROWSER_USE_API_KEY=your-browseruse-cloud-key-here

# Set default model (optional)
DEFAULT_LLM_MODEL=gpt-4o
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Browser Use Cloud: https://cloud.browser-use.com/new-api-key (free credits available)

### 5. Run First Test

```bash
python test_browser_use.py
```

## Test Modes

### Traditional Mode (Default)

**What it tests:** Standard browser automation with DOM parsing

```bash
python test_browser_use.py traditional
```

**What happens:**
1. Opens a browser window
2. Navigates to GitHub
3. Finds the browser-use repository
4. Extracts the star count
5. Shows completion summary

**Duration:** ~30-60 seconds

---

### Permission Mode

**What it tests:** User approval prompts for sensitive actions

```bash
python test_browser_use.py permission
```

**What happens:**
1. Opens a browser window
2. **Shows approval prompt** before navigating to Google
3. You type `yes` to approve
4. Searches for "browser automation"
5. Shows completion summary

**Example prompt you'll see:**
```
🟡 SECURITY APPROVAL REQUIRED 🟡
Action Type: NAVIGATION
Description: Navigate to https://google.com
Risk Level: MEDIUM
Task: Go to google.com and search for 'browser automation'
Current Goal: Navigate to Google homepage
Why this step: Start the search task

Approve? (yes/no/all-session/all-domain): yes
```

**Duration:** ~30-60 seconds (plus time for your approvals)

**Tips:**
- Type `yes` to approve individual actions
- Type `all-session` to approve all similar actions this session
- Type `all-domain` to approve all actions for google.com
- Type `no` to deny (agent will try alternative approach)

---

### AWI Mode

**What it tests:** Fast API-based automation (500x fewer tokens than DOM parsing)

```bash
python test_browser_use.py awi
```

**🌐 Using the Deployed Backend**

The test uses the deployed AWI backend at `https://ai-browser-security.onrender.com`.

**No setup required!** Just run the test:
```bash
python test_browser_use.py awi
```

**Notes:**
- ✅ No Redis or MongoDB needed on your machine
- 🔄 **Automatic wake-up**: If backend is sleeping, test will automatically retry for up to 2 minutes
- ⏰ First request takes ~60-90 seconds if backend is asleep (subsequent requests are instant)
- 📊 After first registration, credentials are saved for reuse
- 🔐 Credentials stored in `~/.config/browseruse/config.json`
- 💡 You'll see retry progress with countdown timers

---

**🏠 Running a Local Backend (Optional)**

> **Important:** Browser-use does NOT require Redis or MongoDB. These are only needed if you want to run your own AWI backend server for testing purposes. The backend server manages these dependencies internally.

If you want to run your own local backend for development, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/starks-and-wolves/ai-browser-security.git
cd ai-browser-security/AWI/AWI/backend
```

**2. Install dependencies:**
```bash
npm install
```

**3. Set up MongoDB (choose one option):**

Option A - MongoDB Cloud (recommended):
```bash
# 1. Sign up at https://www.mongodb.com/cloud/atlas
# 2. Create a free cluster
# 3. Get your connection string
# Example: mongodb+srv://username:password@cluster.mongodb.net/awi_db
```

Option B - Local MongoDB:
```bash
# macOS
brew install mongodb-community@6
brew services start mongodb-community@6

# Ubuntu/Debian
sudo apt install mongodb-org
sudo systemctl start mongod

# Connection string: mongodb://localhost:27017/awi_db
```

**4. Set up Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

**5. Create .env file in backend/ directory:**
```bash
cat > .env << EOF
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/awi_db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
PORT=5000
NODE_ENV=development
EOF
```

**6. Start the backend:**
```bash
npm run dev
```

**7. Verify it's running:**
```bash
# Check AWI manifest
curl http://localhost:5000/.well-known/llm-text | jq

# Should return JSON with AWI capabilities
```

**8. Run the test:**
```bash
# Go back to browser-use directory
cd /path/to/browser-use
python test_browser_use.py awi
```

**What happens:**
1. Discovers AWI at the deployed backend
2. **Shows permission dialog** (first run only - requires interactive terminal)
3. Uses structured API calls instead of DOM parsing
4. Stores credentials locally for future runs
5. Shows completion summary with performance metrics

**First run permission dialog:**
```
────────────────── 🤖 AWI Mode - Agent Registration Required ──────────────────

                               🌐 AWI Information
╭───────────────┬──────────────────────────────────────────────────────────────╮
│ Name          │ Blog AWI                                                     │
│ Description   │ Agent Web Interface for a blog platform                     │
│ Version       │ 1.0                                                          │
│ Provider      │ AWI Blog Platform                                            │
╰───────────────┴──────────────────────────────────────────────────────────────╯

           ⚙️  Operations
╭───────────────┬─────────────────╮
│ Allowed ✅    │ Disallowed 🚫   │
├───────────────┼─────────────────┤
│ read          │ delete          │
│ write         │ admin           │
│ search        │ bulk-operations │
╰───────────────┴─────────────────╯

❓ Do you want to register an agent with this AWI? [y/n] (n): y
🏷️  Agent name [BrowserUseAgent]: MyAgent
🔑 Permissions [read,write]: read,write
✅ Proceed with registration? [Y/n]: y
```

**⚠️ Interactive Terminal Required:** The permission dialog requires stdin input. Run the test in a normal terminal, not as a background process.

**Second run:**
No dialog! Credentials reused automatically. Task completes 10-100x faster.

**Duration:**
- First run: ~20-30 seconds
- Subsequent runs: ~2-5 seconds (using cached credentials)

**If backend not available:**
The test will be skipped with a helpful message.

---

### All Modes

**Run all three tests sequentially:**

```bash
python test_browser_use.py all
```

**Duration:** ~2-3 minutes total

**What happens:**
1. Runs traditional mode test
2. Runs permission mode test (requires your input)
3. Runs AWI mode test (if backend available)
4. Shows summary of all results

---

## Expected Output

### Successful Test Output

```
======================================================================
🤖 Browser-Use Test Script
======================================================================

Running mode: traditional

🔑 API Key Status:
   ✅ OPENAI_API_KEY: Set
   ✅ Using LLM: gpt-4o

======================================================================
🎯 Test 1: Traditional Mode
======================================================================
Task: Find the number of stars of the browser-use repo
Mode: Standard browser automation (DOM parsing, clicking, typing)

▶️  Starting agent...
INFO [Agent] 🚀 Starting task: Go to github.com/browser-use/browser-use...
INFO [Agent] 📍 Step 1:
INFO [Agent]   ▶️  navigate: url: https://github.com/browser-use/browser-use
INFO [Agent] 📍 Step 2:
INFO [Agent]   ▶️  extract_content: xpath: //span[@id='repo-stars-counter-star']
INFO [Agent] ✅ Task completed!

✅ Traditional mode test completed!
   Steps taken: 2

======================================================================
📊 Test Summary
======================================================================
✅ Traditional mode: PASSED

======================================================================
🎉 All tests completed!

Next steps:
  • Explore examples: examples/
  • Read docs: docs/awi/
  • Manage AWI agents: python -m browser_use.cli_agent_registry list
======================================================================
```

### If API Keys Missing

```
❌ No API keys found in .env file

Please add one of:
  BROWSER_USE_API_KEY=your-key  (get from https://cloud.browser-use.com/new-api-key)
  OPENAI_API_KEY=your-key
  ANTHROPIC_API_KEY=your-key
```

**Solution:** Edit `.env` file and add your API key.

### If AWI Backend Not Running

```
⚠️  AWI backend not available at http://localhost:5000
    Error: Cannot connect to host localhost:5000
    Skipping AWI mode test.

💡 To test AWI mode, start an AWI-enabled backend:
    cd /path/to/awi/backend
    npm run dev
```

**Solution:** Start the AWI backend first.

---

## Troubleshooting

### Issue: "Python 3.11 or higher is required"

**Solution:**
```bash
# Install Python 3.11+
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt install python3.11
```

### Issue: "No module named 'browser_use'"

**Solution:**
```bash
# Install the enhanced version (NOT from PyPI!)
uv pip install -e .

# If you accidentally installed from PyPI, uninstall first:
uv pip uninstall browser-use
uv pip install -e .
```

**Windows-Specific Solution:**

If the editable install doesn't work on Windows, add this to the top of your scripts:

```python
import sys
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now imports will work
from browser_use import Agent, Browser
```

This fix is already applied in `test_browser_use.py` and `example_windows.py`.

**Diagnostic Tool:**

Run the diagnostic script to identify the exact issue:
```powershell
python diagnose_windows.py
```

### Issue: "Chromium not found"

**Solution:**
```bash
# Install Chromium
uv run browser-use install
```

### Issue: Browser window doesn't appear (Permission Mode)

**Solution:**
The test uses `headless=False` for traditional and permission modes. If you want headless:

Edit `test_browser_use.py` and change:
```python
browser = Browser(headless=False)
# to
browser = Browser(headless=True)
```

### Issue: Agent takes too long or gets stuck

**Solution:**
The test has `max_steps=5` or `max_steps=10`. The agent should complete within this limit. If stuck:

1. Press Ctrl+C to interrupt
2. Check your internet connection
3. Check if the target website is accessible
4. Try with a different LLM model (edit DEFAULT_LLM_MODEL in .env)
5. Check your API key has sufficient credits/quota

### Issue: "EOF when reading a line" in AWI mode

**Problem:** AWI permission dialog fails with `EOFError`

**Cause:** The permission dialog requires an interactive terminal with stdin

**Solutions:**
1. Run in an interactive terminal (not as a background process)
2. Use previously registered credentials (stored in `~/.config/browseruse/config.json`)
3. Check stored credentials: `python -m browser_use.cli_agent_registry list`

### Issue: AWI mode keeps asking for registration

**Cause:** Credentials are domain-specific for security

**Check your credentials:**
```bash
python -m browser_use.cli_agent_registry list
```

**Note:** If you have credentials for `localhost:5000` but are testing `ai-browser-security.onrender.com`, you need to register separately for the new domain.

---

## Managing AWI Credentials

After running AWI mode tests, credentials are stored automatically. Manage them with:

```bash
# List all registered agents
python -m browser_use.cli_agent_registry list

# Output:
# 📋 Registered AWI Agents:
# ┌────────────────┬──────────┬────────────────┬─────────────┬───────────┬──────────┬────────┐
# │ Agent ID       │ Name     │ Domain         │ Permissions │ Last Used │ Sessions │ Status │
# ├────────────────┼──────────┼────────────────┼─────────────┼───────────┼──────────┼────────┤
# │ agent_123ab... │ MyAgent  │ localhost:5000 │ read, write │ 2h ago    │ 5        │ ✅     │
# └────────────────┴──────────┴────────────────┴─────────────┴───────────┴──────────┴────────┘

# Show details for specific agent
python -m browser_use.cli_agent_registry show agent_123abc

# Delete agent credentials
python -m browser_use.cli_agent_registry delete agent_123abc

# Remove expired credentials
python -m browser_use.cli_agent_registry cleanup
```

---

## Writing Custom Tests

Use the test script as a template for your own tests:

### Basic Agent
```python
from browser_use import Agent, Browser
from browser_use.llm import get_default_llm
import asyncio

async def my_custom_test():
    """Your custom test."""
    browser = Browser(headless=False)

    agent = Agent(
        task="Your custom task here",
        llm=get_default_llm(),
        browser=browser,
        max_steps=10,
    )

    history = await agent.run()
    print(f"✅ Task completed in {len(history.history)} steps")

    await browser.close()

if __name__ == "__main__":
    asyncio.run(my_custom_test())
```

### With Permission Mode
```python
from browser_use import Agent, Browser, BrowserProfile

async def permission_test():
    """Test with security approval."""
    profile = BrowserProfile(
        user_approval_required=True,
        allowed_domains=['*.google.com', '*.github.com'],
        blocked_domains=['*.facebook.com'],
    )

    browser = Browser(browser_profile=profile)
    agent = Agent(
        task="Search for Python tutorials on Google",
        llm=get_default_llm(),
        browser=browser,
    )

    history = await agent.run()
    await browser.close()
```

### With AWI Mode
```python
async def awi_test():
    """Test with AWI mode."""
    browser = Browser(headless=True)
    agent = Agent(
        task="List blog posts and add a comment",
        llm=get_default_llm(),
        browser=browser,
        awi_mode=True,  # Enable AWI
    )

    history = await agent.run()

    # Check stored credentials
    from browser_use.agent_registry import agent_registry
    creds = agent_registry.list_credentials()
    print(f"📋 Stored credentials: {len(creds)}")

    await browser.close()
```

---

## Next Steps

After running the tests:

1. **Explore Examples**: Check `examples/` directory for more use cases
2. **Read Documentation**:
   - [README.md](README.md) - Enhanced version overview
   - [CLAUDE.md](CLAUDE.md) - Development guide
   - [AWI Overview](docs/awi/AWI_OVERVIEW.md) - AWI mode details
   - [AWI Troubleshooting](docs/awi/TROUBLESHOOTING.md)
   - [Official Docs](https://docs.browser-use.com) - Compatible with enhanced version
3. **Build Your Agent**: Use the test script as a starting point
4. **Manage Credentials**: `python -m browser_use.cli_agent_registry list`
5. **Join Community**:
   - [Discord](https://link.browser-use.com/discord)
   - [GitHub (Original)](https://github.com/browser-use/browser-use)

---

## Support

Having issues? Check:
- **This Troubleshooting section** (above)
- [README.md Troubleshooting](README.md#-troubleshooting)
- [AWI Troubleshooting Guide](docs/awi/TROUBLESHOOTING.md)
- [CLAUDE.md](CLAUDE.md) - Development setup
- [Official GitHub Issues](https://github.com/browser-use/browser-use/issues)
- [Discord Community](https://link.browser-use.com/discord)

## Key Differences from Official Browser-Use

This enhanced version includes:
- ✨ AWI mode for 500x faster automation
- 🛡️ Permission mode with security approval workflows
- 🔐 Domain whitelisting/blacklisting
- 💾 Agent credential registry for AWI
- 📊 Enhanced session state management

All official browser-use features remain fully compatible.
