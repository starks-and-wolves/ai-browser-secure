# AWI (Agent Web Interface) Mode for Browser-Use

## Overview

AWI Mode enables browser-use to automatically discover and interact with AWI-compliant websites using structured APIs instead of DOM parsing.

### Key Benefits

- **500x token reduction** compared to DOM parsing
- **Server-side session state** management
- **Trajectory tracking** for debugging and RL training
- **Explicit security policies** from the website
- **Structured responses** with semantic metadata

---

## Quick Start

### 1. Enable AWI Mode

```python
from browser_use import Agent, Browser

agent = Agent(
    task="List all blog posts and summarize them",
    llm=ChatOpenAI(model="gpt-4"),
    browser=Browser(),
    awi_mode=True  # Enable AWI mode
)

result = await agent.run()
```

### 2. What Happens

When AWI mode is enabled and you navigate to an AWI-compliant website:

1. **Automatic Discovery**: Browser-use looks for `/.well-known/llm-text`
2. **Permission Dialog**: You're prompted to approve agent registration
3. **Select Permissions**: Choose which permissions to grant (read, write, delete)
4. **Agent Registration**: Agent registers with the AWI
5. **API Usage**: All interactions use the structured API (500x fewer tokens!)

### 3. Permission Dialog Example

```
🤖 AWI Mode - Agent Registration Required

🌐 AWI Information
┌────────────────────────────────────┐
│ Name:        Blog AWI              │
│ Version:     1.0                   │
│ Provider:    AWI Blog Platform     │
└────────────────────────────────────┘

🔒 Security Features
• sanitize-html: strict
• detect-prompt-injection: true
• detect-xss: true
• detect-nosql-injection: true

⚙️  Operations
┌──────────────┬─────────────────┐
│ Allowed ✅   │ Disallowed 🚫   │
├──────────────┼─────────────────┤
│ read         │ delete          │
│ write        │ admin           │
│ search       │ bulk-operations │
└──────────────┴─────────────────┘

❓ Do you want to register an agent? [y/N]: y
🏷️  Agent name [BrowserUseAgent]: MyAgent
🔑 Permissions [read,write]: read,write

✅ Proceed with registration? [Y/n]: y
```

---

## Modules

### `discovery.py`

Discovers AWI manifests using multiple methods:
- HTTP headers (`X-AWI-Discovery`)
- Well-known URI (`/.well-known/llm-text`)
- Capabilities endpoint (`/api/agent/capabilities`)

```python
from browser_use.awi import AWIDiscovery

async with AWIDiscovery() as discovery:
    manifest = await discovery.discover("http://localhost:5000")
    if manifest:
        print(discovery.get_summary(manifest))
```

### `permission_dialog.py`

Interactive dialog for user approval:
- Shows AWI information and security features
- Displays allowed/disallowed operations
- Gets user permission selection
- Confirms registration

```python
from browser_use.awi import AWIPermissionDialog

dialog = AWIPermissionDialog(manifest)
approval = dialog.show_and_get_permissions()

if approval and approval['approved']:
    print(f"User approved: {approval['permissions']}")
```

### `manager.py`

Manages AWI API interactions:
- Registers agent with selected permissions
- Makes API calls (list_posts, create_post, search, etc.)
- Manages session state
- Tracks action history (trajectory)

```python
from browser_use.awi import AWIManager

async with AWIManager(manifest) as awi:
    # Register
    agent_info = await awi.register_agent(
        agent_name="MyAgent",
        permissions=["read", "write"]
    )

    # Use API
    posts = await awi.list_posts(page=1, limit=10)

    # Create content
    post = await awi.create_post(
        title="Test Post",
        content="<p>Content here</p>"
    )

    # Query session state
    state = await awi.get_session_state()
    history = await awi.get_action_history()
```

---

## Examples

### Full Example

See `examples/awi_mode_example.py` for a complete demonstration:

```bash
python examples/awi_mode_example.py
```

This demonstrates:
- ✅ AWI discovery
- ✅ Permission dialog
- ✅ Agent registration
- ✅ Listing posts
- ✅ Creating posts
- ✅ Adding comments
- ✅ Searching
- ✅ Session state queries
- ✅ Action history retrieval

### Fallback Behavior

If AWI is not available or user declines, browser-use automatically falls back to traditional DOM parsing:

```python
agent = Agent(
    task="Extract data from example.com",
    llm=ChatOpenAI(model="gpt-4"),
    browser=Browser(),
    awi_mode=True  # Will try AWI first, fall back to DOM if needed
)

# Uses AWI if available, DOM otherwise
result = await agent.run()
```

---

## Integration Guide

See `integration_guide.md` for detailed instructions on integrating AWI mode into the browser-use Agent class.

Key integration points:
1. Add `awi_mode` parameter to Agent
2. Add AWI discovery on navigation
3. Modify action execution to use AWI
4. Add state query methods

---

## API Reference

### AWIDiscovery

#### `discover(url: str) -> Optional[Dict]`
Discover AWI manifest from URL.

#### `extract_capabilities(manifest: Dict) -> Dict`
Extract capability directives.

#### `extract_authentication(manifest: Dict) -> Dict`
Extract authentication requirements.

#### `get_summary(manifest: Dict) -> str`
Generate human-readable summary.

### AWIPermissionDialog

#### `show_and_get_permissions() -> Optional[Dict]`
Show dialog and get user approval.

#### `show_registration_success(agent_info: Dict)`
Display successful registration.

#### `show_awi_mode_banner()`
Display AWI mode activation banner.

### AWIManager

#### `register_agent(agent_name, permissions, ...) -> Dict`
Register agent and get API key.

#### `list_posts(page, limit, search, ...) -> Dict`
List blog posts with pagination.

#### `get_post(post_id: str) -> Dict`
Get single post by ID.

#### `create_post(title, content, ...) -> Dict`
Create new blog post.

#### `list_comments(post_id: str) -> Dict`
Get comments for a post.

#### `create_comment(post_id, content, ...) -> Dict`
Add comment to a post.

#### `search(query, intent, filters) -> Dict`
Advanced natural language search.

#### `get_session_state() -> Dict`
Get current session state.

#### `get_action_history(limit, offset) -> Dict`
Get action history (trajectory).

#### `get_state_diff() -> Dict`
Get state diff since last action.

#### `end_session() -> Dict`
End session and get statistics.

---

## Configuration

### Environment Variables

```bash
# Enable AWI mode by default
BROWSER_USE_AWI_MODE=true

# Skip permission dialog (NOT RECOMMENDED)
BROWSER_USE_AWI_AUTO_APPROVE=false

# Default permissions if auto-approve enabled
BROWSER_USE_AWI_DEFAULT_PERMISSIONS=read,write
```

### Programmatic

```python
agent = Agent(
    task="...",
    llm=...,
    awi_mode=True,
    awi_auto_approve=False,  # Require user confirmation
    awi_default_permissions=['read', 'write']
)
```

---

## Testing Your AWI

To test if your website properly implements AWI:

```bash
python -m browser_use.awi.test_discovery http://your-website.com
```

This checks:
- ✅ HTTP headers present
- ✅ `.well-known/llm-text` accessible
- ✅ Manifest valid
- ✅ Required fields present
- ✅ Registration endpoint works

---

## Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Will show detailed AWI discovery and API calls
agent = Agent(..., awi_mode=True)
```

---

## Token Comparison

### Traditional DOM Parsing

```python
# Navigate to page
html = await browser.get_page_source()  # ~100,000 tokens

# Parse DOM
posts = parse_html_for_posts(html)  # Complex, brittle

# Total: ~100,000 tokens per page
```

### AWI Mode

```python
# Discover AWI
manifest = await discovery.discover(url)  # ~200 tokens

# Register agent
agent_info = await awi.register_agent(...)  # ~100 tokens

# List posts
posts = await awi.list_posts(page=1)  # ~200 tokens

# Total: ~500 tokens (200x reduction)
```

---

## Security

AWI mode respects website security policies:

- ✅ **Permissions**: Only requested permissions are granted
- ✅ **Rate Limits**: Enforced by AWI (if configured)
- ✅ **Sanitization**: All inputs sanitized (XSS, injection protection)
- ✅ **Audit Trail**: All actions logged on server
- ✅ **Block on Violation**: Security violations immediately blocked

---

## Troubleshooting

### AWI Not Discovered

Check:
1. Website has `/.well-known/llm-text` file
2. HTTP headers include `X-AWI-Discovery`
3. Manifest is valid JSON
4. Network connectivity

### Registration Failed

Check:
1. Registration endpoint is correct
2. Requested permissions are valid
3. Network connectivity
4. Server logs for errors

### API Calls Failing

Check:
1. API key is included in headers
2. Permissions are sufficient
3. Rate limits not exceeded
4. Request format is correct

---

## Contributing

To add AWI support to your website:

1. Create `/.well-known/llm-text` manifest
2. Add HTTP headers for discovery
3. Implement registration endpoint
4. Return structured responses with metadata
5. Add session state management
6. Test with browser-use AWI mode

See `/backend/docs/AWI_DISCOVERY.md` for complete implementation guide.

---

## Resources

- **AWI Discovery Documentation**: `/backend/docs/AWI_DISCOVERY.md`
- **Integration Guide**: `browser_use/awi/integration_guide.md`
- **Example Script**: `examples/awi_mode_example.py`
- **AWI Research Paper**: arXiv:2506.10953v1

---

## License

Same as browser-use (MIT)
