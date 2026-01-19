# AWI Mode - Troubleshooting Guide

Common issues and solutions when using AWI mode.

## Table of Contents

- [AWI Discovery Issues](#awi-discovery-issues)
- [Registration Problems](#registration-problems)
- [Rate Limiting](#rate-limiting)
- [Request Body Issues](#request-body-issues)
- [Credential Management](#credential-management)
- [Agent Behavior](#agent-behavior)
- [Backend Issues](#backend-issues)

## AWI Discovery Issues

### Issue: "No AWI found, using traditional DOM parsing"

**Symptoms:**
```
INFO [Agent] No AWI found, using traditional DOM parsing
INFO [Agent]   ▶️  navigate: url: http://localhost:5000
```

**Causes:**
1. Backend not running
2. AWI manifest not accessible
3. Wrong URL format
4. Network connectivity issues

**Solutions:**

**Check 1: Verify backend is running**
```bash
# Check if backend process is active
curl http://localhost:5000

# Should return a response (not connection error)
```

**Check 2: Verify AWI manifest exists**
```bash
curl http://localhost:5000/.well-known/llm-text

# Should return JSON manifest like:
# {"awi": {"name": "...", "version": "..."}, ...}
```

**Check 3: Verify URL format**
```python
# ✅ Correct
agent = Agent(task="...", awi_mode=True)
result = await agent.run()  # URL from task or explicit navigate

# ❌ Incorrect - missing protocol
agent = Agent(task="Go to localhost:5000", ...)  # Add http://
```

**Check 4: Enable debug logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue: "AWI discovery timed out"

**Cause:** Network latency or backend performance issues.

**Solution:**
```python
# Increase timeout in AWIDiscovery
from browser_use.awi.discovery import AWIDiscovery

discovery = AWIDiscovery(timeout=60)  # 60 second timeout
manifest = await discovery.discover(url)
```

## Registration Problems

### Issue: "Agent registration failed: EOF when reading a line"

**Symptoms:**
```
ERROR [Agent] ❌ AWI registration failed: EOF when reading a line
INFO [Agent] Falling back to traditional DOM parsing
```

**Cause:** Permission dialog cannot get user input (automated/headless environment).

**Solution 1: Mock the permission dialog**
```python
from unittest.mock import patch

approval_data = {
    'approved': True,
    'agent_name': 'MyAgent',
    'permissions': ['read', 'write']
}

with patch('browser_use.awi.permission_dialog.AWIPermissionDialog.show_and_get_permissions', return_value=approval_data):
    agent = Agent(task="...", llm=llm, browser=browser, awi_mode=True)
    result = await agent.run()
```

**Solution 2: Use pre-registered credentials**
```python
from browser_use.agent_registry import agent_registry

# Register once manually
agent_registry.store_credentials(
    agent_id='my_agent_123',
    agent_name='MyAgent',
    domain='localhost:5000',
    api_key='your_api_key',
    permissions=['read', 'write'],
    awi_name='Service Name'
)

# Subsequent runs will reuse credentials
```

### Issue: "Registration failed (401): Unauthorized"

**Cause:** Backend requires authentication token or validation.

**Solution:** Check backend logs for specific error. May need to configure backend to accept agent registrations.

### Issue: "No API key returned from registration"

**Cause:** Backend response missing `apiKey` field.

**Solution:**
```bash
# Test registration manually
curl -X POST http://localhost:5000/api/agent/register \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "TestAgent",
    "permissions": ["read", "write"],
    "agentType": "browser-use",
    "framework": "python"
  }'

# Response should include: {"agent": {"apiKey": "..."}}
```

## Rate Limiting

### Issue: "Rate limit exceeded. Details: operation: create_comment; reason: cooldown period"

**Full Error:**
```
ERROR [generic_tool] ❌ AWI Execute failed: Rate limit exceeded.
Details: operation: create_comment; reason: cooldown period; retryAfter: 5;
limits: {'hourly': 300, 'minute': 30, 'burst': 9, 'cooldown': 5};
reputation: normal; message: You have exceeded the cooldown period.
Please retry after 5 seconds.
```

**Cause:** Agent made requests too quickly, violating backend rate limits.

**Rate Limit Tiers:**
- `hourly: 300` - Max 300 operations per hour
- `minute: 30` - Max 30 operations per minute
- `burst: 9` - Max 9 rapid-fire operations
- `cooldown: 5` - Min 5 seconds between individual requests

**Solution 1: Respect retryAfter (immediate)**
```python
# Wait the specified time and retry
import asyncio

# Error says "retryAfter: 5"
await asyncio.sleep(5)

# Retry the operation
result = await awi_execute(...)
```

**Solution 2: Implement exponential backoff**
```python
import asyncio
from browser_use.awi import awi_execute

async def awi_execute_with_retry(params, awi_manager, max_retries=3):
    """Execute AWI call with automatic retry on rate limit."""
    base_delay = 1.0

    for attempt in range(max_retries + 1):
        result = await awi_execute(params, awi_manager)

        # Check if rate limited
        if result.error and 'Rate limit exceeded' in result.error:
            if attempt < max_retries:
                # Extract retryAfter from error or use exponential backoff
                delay = base_delay * (2 ** attempt)
                logger.warning(f"⏳ Rate limited, retrying in {delay}s")
                await asyncio.sleep(delay)
                continue
            else:
                # Max retries exceeded
                return result

        # Success or non-retriable error
        return result

    return result
```

**Solution 3: Add delays between operations**
```python
# In your agent task
agent = Agent(
    task="""
    1. List blog posts
    2. Wait 2 seconds
    3. Add comment to first post
    4. Wait 2 seconds
    5. Add comment to second post
    """,
    llm=llm,
    browser=browser,
    awi_mode=True
)
```

**Solution 4: Batch operations**
```python
# Instead of multiple individual requests
# BAD: 10 separate create requests (triggers cooldown)
for post in posts:
    await create_comment(post.id, "Comment")

# GOOD: Batch create or space out requests
for i, post in enumerate(posts):
    await create_comment(post.id, "Comment")
    if i < len(posts) - 1:
        await asyncio.sleep(5)  # Respect cooldown
```

### Understanding Reputation Levels

Rate limits adjust based on agent reputation:

| Reputation | Hourly Limit | Cooldown | Status |
|------------|--------------|----------|--------|
| `new` | 150 (50% of normal) | 10s | First 24 hours |
| `normal` | 300 (standard) | 5s | Good standing |
| `trusted` | 900 (3x normal) | 2s | Consistent good behavior |
| `throttled` | 75 (25% of normal) | 20s | Recent violations |

**How to build reputation:**
1. Use the agent consistently over days/weeks
2. Respect `retryAfter` values (never ignore)
3. Keep error rates low
4. Implement proper retry logic with exponential backoff
5. Handle rate limits gracefully

**How to avoid throttling:**
1. Never rapid-fire retry on failures
2. Validate requests client-side before sending
3. Implement circuit breakers for repeated failures
4. Honor cooldown periods

## Request Body Issues

### Issue: "Validation failed. Details: content: Comment content is required"

**Symptoms:**
```
ERROR [generic_tool] ❌ AWI Execute failed: Validation failed.
Details: content: Comment content is required
```

**Cause:** LLM sent empty body `{}` or missing required fields.

**Solution 1: Use better LLM (recommended)**
```python
# ❌ May struggle with request bodies
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o-mini')

# ✅ Better at filling request bodies
from browser_use.llm.anthropic import ChatAnthropic
llm = ChatAnthropic(model='claude-3-5-sonnet-20241022')

# ✅ Also good
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o')
```

**Solution 2: Add explicit body requirements to task**
```python
# ❌ Vague
task = "Add a comment to the first post"

# ✅ Explicit
task = """
Add a comment to the first post with:
- content: "Great post! Very informative."
- authorName: "AI Agent"
"""
```

**Solution 3: Use structured prompting**
```python
task = """
1. List all blog posts
2. Get the first post ID
3. Create a comment with body:
   {
     "content": "Insightful article! Thanks for sharing.",
     "authorName": "Browser-Use Agent"
   }
"""
```

### Issue: "Field type mismatch"

**Symptoms:**
```
ERROR [generic_tool] ❌ AWI Execute failed: Validation failed.
Details: tags: expected array, got string
```

**Cause:** LLM sent wrong data type for field.

**Solution:** Be explicit about types in task description:
```python
task = """
Create a blog post with:
- title: string
- content: string
- tags: array of strings like ["ai", "automation"]
- category: string (one of: "tech", "science", "news")
"""
```

## Credential Management

### Issue: "Credentials not found" (dialog shows every time)

**Symptoms:** Permission dialog appears on every run despite previous approval.

**Cause:** Credentials not stored or stored under different domain.

**Solution 1: Check stored credentials**
```bash
# List all registered agents
python -m browser_use.cli_agent_registry list

# Should show your agent with domain matching target URL
```

**Solution 2: Verify domain normalization**
```python
# All these should map to same domain: "localhost:5000"
agent_registry.get_credentials('http://localhost:5000')
agent_registry.get_credentials('http://localhost:5000/')
agent_registry.get_credentials('localhost:5000')
agent_registry.get_credentials('http://localhost:5000/api')

# If not matching, check agent_registry._normalize_domain()
```

**Solution 3: Manually store credentials**
```python
from browser_use.agent_registry import agent_registry

agent_registry.store_credentials(
    agent_id='my_agent_123',
    agent_name='MyAgent',
    domain='localhost:5000',  # Normalized format
    api_key='your_api_key',
    permissions=['read', 'write'],
    awi_name='Service Name'
)
```

### Issue: "Credentials expired"

**Symptoms:**
```
ERROR [agent_registry] ❌ Credentials expired
```

**Cause:** Credentials have `expires_at` timestamp in the past.

**Solution:**
```bash
# Remove expired credentials
python -m browser_use.cli_agent_registry cleanup

# Re-register agent (will prompt for permission)
python your_script.py
```

### Issue: "Wrong agent credentials used"

**Symptoms:** Agent uses credentials for different service.

**Cause:** Multiple agents registered for same domain.

**Solution 1: Delete old agents**
```bash
# List agents
python -m browser_use.cli_agent_registry list

# Delete specific agent
python -m browser_use.cli_agent_registry delete agent_123abc
```

**Solution 2: Specify agent name explicitly**
```python
from browser_use.agent_registry import agent_registry

cred = agent_registry.get_credentials(
    domain='localhost:5000',
    agent_name='MySpecificAgent'  # Filter by name
)
```

## Agent Behavior

### Issue: Agent uses browser actions instead of AWI

**Symptoms:**
```
INFO [Agent]   ▶️  navigate: url: http://localhost:5000
INFO [Agent]   ▶️  click: element: <button>
```

**Cause:** AWI mode not activated (discovery failed or disabled).

**Solution 1: Verify awi_mode=True**
```python
agent = Agent(
    task="...",
    llm=llm,
    browser=browser,
    awi_mode=True  # ← Must be True
)
```

**Solution 2: Check discovery logs**
```python
import logging
logging.basicConfig(level=logging.INFO)

# Look for these logs:
# ✅ "🔍 AWI Mode: Checking for AWI at http://..."
# ✅ "✅ AWI discovered: Service Name"
# ✅ "🚀 AWI Mode active"

# ❌ If you see: "No AWI found, using traditional DOM parsing"
# → Check backend and manifest
```

### Issue: Agent mixes AWI and browser actions

**Symptoms:**
```
INFO [Agent]   ▶️  awi_execute: operation: list, endpoint: /posts, method: GET
INFO [Agent]   ▶️  navigate: url: http://localhost:5000/post/123
INFO [Agent]   ▶️  click: element: <button>
```

**Cause:** Agent falls back to browser actions when AWI operations fail.

**Solution:** Check why AWI operations are failing:
1. Rate limiting → Add delays
2. Validation errors → Fix request bodies
3. Missing operations → Check manifest for supported operations

## Backend Issues

### Issue: "Connection refused" / "Network error"

**Cause:** Backend not running on expected port.

**Solution:**
```bash
# Check what's running on port
lsof -i :5000

# Start backend
cd /path/to/backend
npm run dev  # or your backend start command

# Verify it's accessible
curl http://localhost:5000
```

### Issue: "CORS error" in browser console

**Cause:** Backend CORS configuration blocking requests.

**Solution:** Configure backend to allow agent origin:
```javascript
// Express.js example
const cors = require('cors');
app.use(cors({
  origin: '*',  // or specific origin
  credentials: true
}));
```

### Issue: "Manifest format invalid"

**Symptoms:**
```
ERROR [discovery] Failed to parse AWI manifest
```

**Cause:** Manifest JSON is malformed or missing required fields.

**Solution:**
```bash
# Validate manifest JSON
curl http://localhost:5000/.well-known/llm-text | jq .

# Check required fields exist:
# - awi.name
# - awi.version
# - authentication.type
# - authentication.registration.endpoint
# - endpoints.base
```

## Debugging Tips

### Enable Debug Logging

```python
import logging

# Enable all logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or specific loggers
logging.getLogger('browser_use.awi').setLevel(logging.DEBUG)
logging.getLogger('browser_use.agent').setLevel(logging.DEBUG)
```

### Inspect Agent Registry

```python
from browser_use.agent_registry import agent_registry

# List all credentials
creds = agent_registry.list_credentials()
for cred in creds:
    print(f"{cred.agent_name} @ {cred.domain}")
    print(f"  API Key: {cred.api_key[:20]}...")
    print(f"  Permissions: {cred.permissions}")
    print(f"  Sessions: {cred.session_count}")
    print(f"  Last Used: {cred.last_used}")
```

### Test AWI Manually

```python
# Test discovery
from browser_use.awi import AWIDiscovery

async with AWIDiscovery() as discovery:
    manifest = await discovery.discover('http://localhost:5000')
    print(f"Manifest: {manifest}")

# Test registration
from browser_use.awi import AWIManager

async with AWIManager(manifest) as manager:
    agent_info = await manager.register_agent(
        agent_name='TestAgent',
        permissions=['read']
    )
    print(f"Agent Info: {agent_info}")

# Test API call
from browser_use.awi import awi_execute, AWIExecuteAction

result = await awi_execute(
    params=AWIExecuteAction(
        operation='list',
        endpoint='/posts',
        method='GET'
    ),
    awi_manager=manager
)
print(f"Result: {result}")
```

### Check Config File

```bash
# View config file
cat ~/.config/browseruse/config.json

# Verify agent_credentials section exists and has entries
cat ~/.config/browseruse/config.json | jq '.agent_credentials'
```

## Getting Help

### Check Logs

Always include full logs when reporting issues:
```bash
python your_script.py 2>&1 | tee awi_debug.log
```

### Verify Environment

```python
# Check versions
import browser_use
print(f"browser-use version: {browser_use.__version__}")

# Check config
from browser_use.config import CONFIG
print(f"Config path: {CONFIG.BROWSER_USE_CONFIG_PATH}")
```

### Common Log Patterns

**✅ Successful AWI activation:**
```
INFO [Agent] 🔍 AWI Mode: Checking for AWI at http://localhost:5000
INFO [Agent] ✅ AWI discovered: Service Name
INFO [agent_registry] ✅ Found credentials for agent MyAgent at localhost:5000
INFO [Agent] 🚀 AWI Mode active - will use structured API
INFO [Agent] ⏭️  Skipping initial browser navigation (AWI mode active)
```

**❌ AWI discovery failure:**
```
INFO [Agent] 🔍 AWI Mode: Checking for AWI at http://localhost:5000
ERROR [discovery] Failed to discover AWI: Connection refused
INFO [Agent] No AWI found, using traditional DOM parsing
```

**❌ Rate limiting:**
```
INFO [Agent]   ▶️  awi_execute: operation: create, endpoint: /posts/123/comments
ERROR [generic_tool] ❌ AWI Execute failed: Rate limit exceeded
```

## Resources

- **[AWI_OVERVIEW.md](./AWI_OVERVIEW.md)** - Architecture and concepts
- **[QUICKSTART.md](./QUICKSTART.md)** - Getting started guide
- **[AGENT_REGISTRY.md](./AGENT_REGISTRY.md)** - Credential management
- **GitHub Issues**: https://github.com/browser-use/browser-use/issues
