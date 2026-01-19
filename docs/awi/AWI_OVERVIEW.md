# AWI (Agent Web Interface) - Overview

## What is AWI?

**AWI (Agent Web Interface)** is a protocol that enables AI agents to interact with websites through structured APIs instead of traditional DOM parsing and browser automation. It provides a standardized way for websites to expose their functionality to AI agents.

## Key Concepts

### Traditional Browser Automation vs AWI

**Traditional Approach:**
```
Agent → Parse HTML → Find elements → Click/Type → Wait → Parse response
```
- Slow and fragile
- Breaks with UI changes
- Requires visual rendering
- High error rates

**AWI Approach:**
```
Agent → Make API call → Get structured response
```
- Fast and reliable
- UI-independent
- No rendering needed
- Low error rates

### How It Works

```
┌─────────────┐
│   Website   │
│             │
│  /.well-    │
│   known/    │◄────── 1. Discovery
│   llm-text  │
│             │
│  Manifest   │
│   - Name    │
│   - Version │
│   - Auth    │
│   - Ops     │
└──────┬──────┘
       │
       │ 2. Registration
       ▼
┌─────────────┐
│  AWI Agent  │
│  Registry   │◄────── 3. Store Credentials
└──────┬──────┘
       │
       │ 4. API Calls
       ▼
┌─────────────┐
│   AWI API   │
│  Endpoints  │
│             │
│  /posts     │
│  /comments  │
│  /search    │
└─────────────┘
```

## Architecture

### Core Components

#### 1. **AWI Discovery** (`browser_use/awi/discovery.py`)

Discovers AWI manifest at `/.well-known/llm-text`:

```python
from browser_use.awi import AWIDiscovery

async with AWIDiscovery() as discovery:
    manifest = await discovery.discover('http://localhost:5000')
    # Returns manifest with endpoints, authentication, operations
```

**Manifest Structure:**
```json
{
  "awi": {
    "name": "Blog AWI",
    "version": "1.0.0",
    "description": "API for blog automation"
  },
  "authentication": {
    "type": "apiKey",
    "headerName": "X-Agent-API-Key",
    "registration": {
      "endpoint": "http://localhost:5000/api/agent/register"
    }
  },
  "endpoints": {
    "base": "http://localhost:5000/api/agent",
    "operations": {
      "list_posts": {
        "endpoint": "/posts",
        "method": "GET",
        "description": "List all blog posts"
      },
      "create_comment": {
        "endpoint": "/posts/{postId}/comments",
        "method": "POST",
        "description": "Add comment to post"
      }
    }
  }
}
```

#### 2. **Permission Dialog** (`browser_use/awi/permission_dialog.py`)

Shows user-approval dialog for agent registration:

```python
from browser_use.awi import AWIPermissionDialog

dialog = AWIPermissionDialog(manifest)
approval = dialog.show_and_get_permissions()

if approval and approval['approved']:
    agent_name = approval['agent_name']
    permissions = approval['permissions']
    # Proceed with registration
```

**Security Features:**
- User must explicitly approve
- Permission scope selection (read, write, admin)
- Agent name customization
- Manifest transparency

#### 3. **AWI Manager** (`browser_use/awi/manager.py`)

Manages agent lifecycle and API calls:

```python
from browser_use.awi import AWIManager

async with AWIManager(manifest) as manager:
    # Register agent
    agent_info = await manager.register_agent(
        agent_name='MyAgent',
        permissions=['read', 'write']
    )

    # Make API calls
    posts = await manager.list_posts()
    comment = await manager.create_comment(
        post_id='123',
        content='Great post!'
    )
```

#### 4. **Agent Registry** (`browser_use/agent_registry.py`)

Persistent credential storage for agent reuse:

```python
from browser_use.agent_registry import agent_registry

# First run: Credentials stored automatically after registration
# Second run: Credentials reused, permission dialog skipped

cred = agent_registry.get_credentials('localhost:5000')
if cred:
    # Reuse existing agent
    api_key = cred.api_key
    permissions = cred.permissions
```

**See [AGENT_REGISTRY.md](./AGENT_REGISTRY.md) for details.**

#### 5. **Generic AWI Tool** (`browser_use/awi/generic_tool.py`)

LLM-driven tool for making any AWI API call:

```python
from browser_use.awi import awi_execute, AWIExecuteAction

result = await awi_execute(
    params=AWIExecuteAction(
        operation='create',
        endpoint='/posts/123/comments',
        method='POST',
        body={'content': 'Great post!', 'authorName': 'Agent'}
    ),
    awi_manager=manager
)
```

**Key Features:**
- Task-agnostic (works for any AWI site)
- LLM decides all parameters
- Automatic error handling
- Structured response formatting

### Integration with Agent

#### Agent Service (`browser_use/agent/service.py`)

**AWI Discovery Flow:**
```python
async def _try_awi_discovery(self, url: str) -> bool:
    """
    1. Discover AWI at URL
    2. Check agent_registry for existing credentials
    3a. If found: Reuse credentials (skip dialog)
    3b. If not: Show dialog, register, store credentials
    4. Register generic AWI tool
    5. Inject AWI context message
    """
```

**When AWI is active:**
- Agent skips initial browser navigation
- Uses `awi_execute` tool instead of browser actions
- No DOM parsing or element interaction
- Faster and more reliable execution

## AWI vs Traditional Browser Automation

| Aspect | Traditional | AWI |
|--------|-------------|-----|
| **Speed** | Slow (render + parse) | Fast (direct API) |
| **Reliability** | Fragile (UI changes break) | Robust (API stable) |
| **Resource Usage** | High (browser rendering) | Low (HTTP requests) |
| **Error Handling** | Complex (DOM quirks) | Simple (HTTP errors) |
| **Maintainability** | Poor (selectors break) | Good (API versioned) |
| **Headless** | Possible but slower | Natural |
| **Permissions** | None (full access) | Scoped (read/write/admin) |

## AWI Manifest Specification

### Required Fields

```json
{
  "awi": {
    "name": "Service Name",
    "version": "1.0.0",
    "description": "Service description"
  },
  "authentication": {
    "type": "apiKey",
    "headerName": "X-Agent-API-Key",
    "registration": {
      "endpoint": "https://example.com/api/agent/register"
    }
  },
  "endpoints": {
    "base": "https://example.com/api/agent",
    "operations": {
      "operation_name": {
        "endpoint": "/resource",
        "method": "GET|POST|PUT|DELETE",
        "description": "What this operation does"
      }
    }
  }
}
```

### Optional Fields

```json
{
  "rateLimit": {
    "requestsPerMinute": 60,
    "requestsPerHour": 1000
  },
  "documentation": "https://example.com/awi-docs",
  "support": {
    "email": "support@example.com",
    "url": "https://example.com/support"
  }
}
```

## Security Considerations

### Permission Model

**Three permission levels:**
- `read`: View data, no modifications
- `write`: Create/update data
- `admin`: Full access including delete

**Best Practices:**
1. Request minimal permissions needed
2. User must explicitly approve
3. Credentials stored locally only
4. API keys can be rotated or revoked

### Rate Limiting

AWI backends enforce rate limits to prevent abuse:

```json
{
  "limits": {
    "hourly": 300,
    "minute": 30,
    "burst": 9,
    "cooldown": 5
  },
  "reputation": "normal"
}
```

**Reputation tiers:**
- `new`: Restricted limits (first 24h)
- `normal`: Standard limits
- `trusted`: Higher limits (good behavior)
- `throttled`: Reduced limits (violations)

**See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#rate-limiting) for handling rate limits.**

## Benefits of AWI

### For Agents
- **Faster execution**: No DOM rendering/parsing
- **More reliable**: APIs don't break with UI changes
- **Better errors**: Structured error responses
- **Credential reuse**: No repeated registration

### For Websites
- **Control**: Define what agents can do
- **Security**: Scoped permissions, rate limits
- **Analytics**: Track agent usage
- **Versioning**: Update APIs without breaking agents

### For Users
- **Transparency**: See what permissions are granted
- **Control**: Approve/revoke access
- **Privacy**: No credential sharing with AI providers
- **Convenience**: One-time approval per site

## Example: Blog Automation

**Without AWI:**
```python
# Navigate to blog
await agent.navigate('http://blog.com')
# Find post links (fragile selectors)
posts = await agent.find_elements('.post-link')
# Click first post
await posts[0].click()
# Find comment box (fragile)
comment_box = await agent.find_element('#comment-input')
# Type comment
await comment_box.type('Great post!')
# Find submit button (fragile)
submit = await agent.find_element('button[type="submit"]')
await submit.click()
```

**With AWI:**
```python
# List posts
posts = await awi_execute(
    operation='list',
    endpoint='/posts',
    method='GET'
)

# Create comment
result = await awi_execute(
    operation='create',
    endpoint=f'/posts/{posts[0]["id"]}/comments',
    method='POST',
    body={'content': 'Great post!', 'authorName': 'Agent'}
)
```

## Next Steps

- **[QUICKSTART.md](./QUICKSTART.md)** - Get started with AWI mode
- **[AGENT_REGISTRY.md](./AGENT_REGISTRY.md)** - Credential management
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions

## Resources

- **Implementation**: `browser_use/awi/` directory
- **Integration**: `browser_use/agent/service.py` (`_try_awi_discovery`)
- **Examples**: `examples/awi_mode_*.py`
- **Tests**: `tests/awi_manual/`
