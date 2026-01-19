# AWI Mode - Quick Start Guide

Get started with AWI (Agent Web Interface) mode in minutes.

## Prerequisites

1. **Python 3.11+** with browser-use installed
2. **AWI-enabled website** or backend
3. **LLM API key** (OpenAI, Anthropic, Google, etc.)

## Installation

```bash
# Install browser-use with all dependencies
pip install browser-use

# Or with uv
uv pip install browser-use
```

## Basic Usage

### 1. Set Up Environment

```bash
# Set your LLM API key
export OPENAI_API_KEY='your-openai-key'
# Or
export ANTHROPIC_API_KEY='your-anthropic-key'

# Optional: Set default model
export DEFAULT_LLM_MODEL='gpt-4o'
```

### 2. Create Your First AWI Agent

```python
import asyncio
from browser_use import Agent, Browser
from browser_use.llm import get_default_llm

async def main():
    # Create browser instance
    browser = Browser(headless=False)

    # Create agent with AWI mode enabled
    agent = Agent(
        task="List the top 3 blog posts and add a comment to the first one",
        llm=get_default_llm(),
        browser=browser,
        awi_mode=True  # ← Enable AWI mode
    )

    # Run the agent
    result = await agent.run()
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Run Your Agent

```bash
python your_script.py
```

**What happens:**
1. Agent discovers AWI at target URL
2. Permission dialog appears (first run only)
3. You approve and select permissions
4. Agent uses structured API calls instead of DOM parsing
5. Credentials stored for future reuse

## Permission Dialog

On first run, you'll see:

```
╔════════════════════════════════════════════════════════╗
║           🤖 AWI Agent Registration                    ║
╠════════════════════════════════════════════════════════╣
║ Service: Blog AWI                                       ║
║ URL: http://localhost:5000                             ║
║ Version: 1.0.0                                         ║
╠════════════════════════════════════════════════════════╣
║ Permissions Requested:                                 ║
║  • read  - View blog posts and comments                ║
║  • write - Create comments and posts                   ║
╠════════════════════════════════════════════════════════╣
║ Approve this agent? (yes/no):                          ║
╚════════════════════════════════════════════════════════╝
```

**Type `yes` and press Enter.**

The agent will be registered and credentials stored in `~/.config/browseruse/config.json`.

**On subsequent runs:** No dialog appears - credentials are reused automatically.

## Configuration Options

### Using Different LLMs

```python
# OpenAI (recommended for general use)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o', temperature=0)

# Anthropic Claude (best for complex tool use)
from browser_use.llm.anthropic import ChatAnthropic
llm = ChatAnthropic(model='claude-3-5-sonnet-20241022', temperature=0)

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', temperature=0)

# Or use the default from environment
from browser_use.llm import get_default_llm
llm = get_default_llm()  # Uses DEFAULT_LLM_MODEL from .env
```

### Browser Configuration

```python
from browser_use import Browser

# Visible browser (good for debugging)
browser = Browser(headless=False)

# Headless browser (good for production)
browser = Browser(headless=True)

# Custom window size
browser = Browser(
    headless=False,
    window_width=1920,
    window_height=1080
)
```

### Agent Configuration

```python
agent = Agent(
    task="Your task description",
    llm=llm,
    browser=browser,
    awi_mode=True,               # Enable AWI
    max_steps=10,                # Max action steps
    use_vision=True,             # Enable vision for screenshots
    max_actions_per_step=5,      # Actions per step
)
```

## Verifying AWI Mode is Active

### Success Indicators

**In logs:**
```
INFO [Agent] 🚀 AWI Mode active - will use structured API instead of DOM parsing
INFO [Agent] ⏭️  Skipping initial browser navigation (AWI mode active)
INFO [Agent]   ▶️  awi_execute: operation: list, endpoint: /posts, method: GET
INFO [generic_tool] ✅ AWI Execute successful: 200 GET /posts
```

**Key signs:**
- ✅ "AWI Mode active" message
- ✅ Agent uses `awi_execute` actions
- ✅ Browser window stays mostly blank (no page loading)
- ✅ No `navigate`, `click`, or `type` actions

### Failure Indicators

**In logs:**
```
INFO [Agent] No AWI found, using traditional DOM parsing
INFO [Agent]   ▶️  navigate: url: http://localhost:5000
INFO [Agent]   ▶️  click: element: <button>
```

**Key signs:**
- ❌ "No AWI found" message
- ❌ Agent uses browser actions (navigate, click, type)
- ❌ Browser loads and displays the website
- ❌ Agent talks about "HTML elements" or "buttons"

## Managing Agent Credentials

### List Registered Agents

```bash
python -m browser_use.cli_agent_registry list
```

**Output:**
```
📋 Registered AWI Agents:
┌────────────────┬──────────┬────────────────┬─────────────┬───────────┬──────────┬────────┐
│ Agent ID       │ Name     │ Domain         │ Permissions │ Last Used │ Sessions │ Status │
├────────────────┼──────────┼────────────────┼─────────────┼───────────┼──────────┼────────┤
│ agent_123ab... │ MyAgent  │ localhost:5000 │ read, write │ 2h ago    │ 5        │ ✅     │
└────────────────┴──────────┴────────────────┴─────────────┴───────────┴──────────┴────────┘
```

### Show Agent Details

```bash
python -m browser_use.cli_agent_registry show agent_123abc
```

### Delete Agent

```bash
python -m browser_use.cli_agent_registry delete agent_123abc
```

### Cleanup Expired Credentials

```bash
python -m browser_use.cli_agent_registry cleanup
```

**See [AGENT_REGISTRY.md](./AGENT_REGISTRY.md) for complete credential management guide.**

## Example Tasks

### List and Read

```python
agent = Agent(
    task="List all blog posts and summarize the top 3",
    llm=get_default_llm(),
    browser=Browser(headless=True),
    awi_mode=True
)
```

### Create Content

```python
agent = Agent(
    task="Add a thoughtful comment to the most popular blog post",
    llm=get_default_llm(),
    browser=Browser(headless=True),
    awi_mode=True
)
```

### Search and Filter

```python
agent = Agent(
    task="Find all posts about 'AI' and list their titles",
    llm=get_default_llm(),
    browser=Browser(headless=True),
    awi_mode=True
)
```

### Complex Workflows

```python
agent = Agent(
    task="""
    1. Find the 3 most recent blog posts
    2. Read each post and summarize it in one sentence
    3. Add a comment to each post with your summary
    """,
    llm=get_default_llm(),
    browser=Browser(headless=True),
    awi_mode=True
)
```

## Best Practices

### 1. Use Specific Tasks

❌ **Too vague:**
```python
task="Do something with the blog"
```

✅ **Specific:**
```python
task="List the top 5 blog posts by view count and add a comment to each"
```

### 2. Handle Rate Limits

AWI backends enforce rate limits. If you get rate limit errors:

```python
# Add delays between operations
import asyncio

agent = Agent(
    task="Add comments to 10 posts",
    llm=get_default_llm(),
    browser=browser,
    awi_mode=True
)

# Run with delay between steps
result = await agent.run()
await asyncio.sleep(1)  # Wait 1s between operations
```

**See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#rate-limiting) for handling rate limits.**

### 3. Choose the Right Model

**For complex operations (create, update):**
- ✅ `claude-3-5-sonnet-20241022` (best)
- ✅ `gpt-4o` (good)
- ⚠️ `gpt-4o-mini` (may struggle with request bodies)

**For simple operations (list, read):**
- ✅ `gpt-4o-mini` (fast and cheap)
- ✅ `claude-3-5-haiku` (fast and cheap)

### 4. Use Headless for Production

```python
# Development: visible browser
browser = Browser(headless=False)

# Production: headless browser
browser = Browser(headless=True)
```

### 5. Monitor Session Count

```bash
# Check how many times agent was used
python -m browser_use.cli_agent_registry list
```

High session counts indicate successful credential reuse.

## Troubleshooting

### "No AWI found"

**Cause:** Backend not running or no AWI manifest at URL.

**Solution:**
```bash
# Verify AWI manifest exists
curl http://localhost:5000/.well-known/llm-text

# Should return JSON manifest
```

### "Rate limit exceeded"

**Cause:** Too many requests in short time.

**Solution:** Wait for `retryAfter` seconds and retry. Implement exponential backoff.

**See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more issues.**

## Next Steps

- **[AWI_OVERVIEW.md](./AWI_OVERVIEW.md)** - Understand AWI architecture
- **[AGENT_REGISTRY.md](./AGENT_REGISTRY.md)** - Manage agent credentials
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Solve common issues

## Resources

- **Examples**: `examples/awi_mode_*.py`
- **Tests**: `tests/awi_manual/`
- **CLI Tool**: `python -m browser_use.cli_agent_registry --help`
