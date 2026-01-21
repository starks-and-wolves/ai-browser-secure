# AWI Mode Integration Guide for Browser-Use

## Overview

This guide explains how to integrate AWI (Agent Web Interface) mode into the browser-use Agent class.

AWI mode enables browser-use to automatically discover and use structured APIs instead of DOM parsing, resulting in:
- **500x token reduction**
- Server-side session state management
- Trajectory tracking for RL training
- Explicit security policies
- Structured responses with semantic metadata

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser-Use Agent                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  User requests navigation to URL                   │ │
│  └────────────────────────────────────────────────────┘ │
│                          ↓                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Check if awi_mode=True                            │ │
│  └────────────────────────────────────────────────────┘ │
│          ↙ No                    Yes ↘                   │
│  ┌──────────────┐         ┌──────────────────────────┐  │
│  │ Traditional  │         │ AWI Discovery             │  │
│  │ DOM Parsing  │         │ (/.well-known/llm-text)   │  │
│  └──────────────┘         └──────────────────────────┘  │
│                                     ↓                     │
│                           ┌──────────────────────────┐  │
│                           │ AWI Found?               │  │
│                           └──────────────────────────┘  │
│                         ↙ No            Yes ↘            │
│                 ┌──────────────┐  ┌─────────────────┐   │
│                 │ Fall back to │  │ Show Permission │   │
│                 │ DOM Parsing  │  │ Dialog to User  │   │
│                 └──────────────┘  └─────────────────┘   │
│                                            ↓              │
│                                   ┌─────────────────┐    │
│                                   │ User Approves?  │    │
│                                   └─────────────────┘    │
│                                 ↙ No         Yes ↘       │
│                         ┌──────────────┐  ┌───────────┐ │
│                         │ Fall back to │  │ Register  │ │
│                         │ DOM Parsing  │  │ Agent     │ │
│                         └──────────────┘  └───────────┘ │
│                                                  ↓        │
│                                         ┌────────────┐   │
│                                         │ Use AWI    │   │
│                                         │ API Calls  │   │
│                                         └────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Steps

### Step 1: Add AWI Mode Parameter to Agent

**File: `browser_use/agent/service.py`**

Add `awi_mode` parameter to the Agent class initialization:

```python
from browser_use.awi import AWIDiscovery, AWIManager, AWIPermissionDialog

class Agent:
    def __init__(
        self,
        task: str,
        llm: BaseChatModel,
        browser: Optional[Browser] = None,
        awi_mode: bool = False,  # NEW PARAMETER
        **kwargs
    ):
        self.task = task
        self.llm = llm
        self.browser = browser
        self.awi_mode = awi_mode  # NEW
        self.awi_manager: Optional[AWIManager] = None  # NEW
        # ... existing code
```

### Step 2: Add AWI Discovery on Navigation

**File: `browser_use/agent/service.py`**

Modify the `run()` or navigation method to check for AWI when `awi_mode=True`:

```python
async def run(self):
    """Execute the agent task."""

    # Get initial URL from task
    url = self._extract_url_from_task(self.task)

    # If AWI mode enabled, try to discover AWI
    if self.awi_mode and url:
        await self._try_awi_discovery(url)

    # Continue with normal execution
    # ... existing code


async def _try_awi_discovery(self, url: str):
    """
    Try to discover and set up AWI for the given URL.

    This runs BEFORE navigation to check if AWI is available.
    If found, shows permission dialog and registers agent.
    """
    logger.info(f"🔍 AWI Mode: Checking for AWI at {url}")

    # Step 1: Discovery
    async with AWIDiscovery() as discovery:
        manifest = await discovery.discover(url)

        if not manifest:
            logger.info("No AWI found, using traditional DOM parsing")
            return

        logger.info(f"✅ AWI discovered: {manifest.get('awi', {}).get('name')}")

    # Step 2: Permission Dialog (BEFORE navigation)
    dialog = AWIPermissionDialog(manifest)
    approval = dialog.show_and_get_permissions()

    if not approval or not approval['approved']:
        logger.info("User declined AWI registration, using traditional DOM parsing")
        return

    # Step 3: Register Agent
    self.awi_manager = AWIManager(manifest)
    try:
        agent_info = await self.awi_manager.register_agent(
            agent_name=approval['agent_name'],
            permissions=approval['permissions'],
            description=f"Browser-use agent: {self.task[:100]}",
            agent_type="browser-use",
            framework="python"
        )

        AWIPermissionDialog.show_registration_success(agent_info)
        AWIPermissionDialog.show_awi_mode_banner()

        logger.info(f"✅ AWI Mode activated for {url}")

    except Exception as e:
        logger.error(f"❌ AWI registration failed: {e}")
        logger.info("Falling back to traditional DOM parsing")
        self.awi_manager = None
```

### Step 3: Modify Task Execution to Use AWI

**File: `browser_use/agent/service.py`**

Modify the action execution logic to use AWI API when available:

```python
async def _execute_action(self, action: AgentAction):
    """Execute an action using AWI or traditional DOM method."""

    # If AWI is available, try to use it first
    if self.awi_manager and self.awi_manager.is_registered():
        awi_result = await self._try_awi_action(action)
        if awi_result is not None:
            return awi_result

    # Fall back to traditional DOM-based execution
    return await self._execute_dom_action(action)


async def _try_awi_action(self, action: AgentAction) -> Optional[Any]:
    """
    Try to execute action using AWI API.

    Returns:
        Action result if AWI handles it, None to fall back to DOM
    """
    action_type = action.action_type

    try:
        # Map common actions to AWI API calls
        if action_type == "list_posts":
            response = await self.awi_manager.list_posts(
                page=action.params.get('page', 1),
                limit=action.params.get('limit', 10),
                search=action.params.get('search')
            )
            return response

        elif action_type == "get_post":
            post_id = action.params.get('post_id')
            response = await self.awi_manager.get_post(post_id)
            return response

        elif action_type == "create_post":
            response = await self.awi_manager.create_post(
                title=action.params.get('title'),
                content=action.params.get('content'),
                author_name=action.params.get('author_name'),
                category=action.params.get('category'),
                tags=action.params.get('tags')
            )
            return response

        elif action_type == "search":
            response = await self.awi_manager.search(
                query=action.params.get('query'),
                intent=action.params.get('intent')
            )
            return response

        # Add more action mappings as needed...

    except Exception as e:
        logger.warning(f"AWI action failed, falling back to DOM: {e}")
        return None

    # Action not handled by AWI
    return None


async def _execute_dom_action(self, action: AgentAction):
    """Execute action using traditional DOM methods."""
    # ... existing DOM-based execution code
    pass
```

### Step 4: Add State Query Methods

Add convenience methods to query AWI session state:

```python
async def get_session_state(self) -> Optional[Dict[str, Any]]:
    """Get current AWI session state (if AWI mode is active)."""
    if self.awi_manager and self.awi_manager.is_registered():
        try:
            return await self.awi_manager.get_session_state()
        except Exception as e:
            logger.warning(f"Failed to get session state: {e}")
    return None


async def get_action_history(self, limit: int = 20) -> Optional[Dict[str, Any]]:
    """Get action history/trajectory (if AWI mode is active)."""
    if self.awi_manager and self.awi_manager.is_registered():
        try:
            return await self.awi_manager.get_action_history(limit=limit)
        except Exception as e:
            logger.warning(f"Failed to get action history: {e}")
    return None
```

---

## Usage Examples

### Basic Usage

```python
from browser_use import Agent, Browser

# Enable AWI mode
agent = Agent(
    task="List all blog posts and create a summary",
    llm=ChatOpenAI(model="gpt-4"),
    browser=Browser(),
    awi_mode=True  # Enable AWI mode
)

result = await agent.run()
```

### With Session State Query

```python
agent = Agent(
    task="Find posts about AI and create a comment",
    llm=ChatOpenAI(model="gpt-4"),
    browser=Browser(),
    awi_mode=True
)

result = await agent.run()

# Query session state after execution
state = await agent.get_session_state()
print(f"Total actions: {state['statistics']['totalActions']}")

# Get trajectory for RL training
trajectory = await agent.get_action_history()
print(f"Action sequence: {len(trajectory['trajectory'])} steps")
```

### Fallback Behavior

```python
# If AWI is not found or user declines, automatically falls back to DOM
agent = Agent(
    task="Navigate to example.com and extract data",
    llm=ChatOpenAI(model="gpt-4"),
    browser=Browser(),
    awi_mode=True  # Will fall back to DOM if no AWI found
)

result = await agent.run()  # Uses DOM parsing if AWI unavailable
```

---

## Permission Dialog Flow

When AWI is discovered, the user sees:

```
┌────────────────────────────────────────────────────┐
│ 🤖 AWI Mode - Agent Registration Required          │
├────────────────────────────────────────────────────┤
│                                                     │
│ 🌐 AWI Information                                 │
│ ┌──────────────────────────────────────────────┐  │
│ │ Name:         Blog AWI                        │  │
│ │ Description:  Agent Web Interface...          │  │
│ │ Version:      1.0                             │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ 🔒 Security Features                               │
│ ┌──────────────────────────────────────────────┐  │
│ │ sanitize-html: strict                         │  │
│ │ detect-prompt-injection: true                 │  │
│ │ detect-xss: true                              │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ ⚙️  Operations                                     │
│ ┌──────────────────────────────────────────────┐  │
│ │ Allowed ✅         │ Disallowed 🚫            │  │
│ │ read              │ delete                    │  │
│ │ write             │ admin                     │  │
│ │ search            │ bulk-operations           │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ ❓ Do you want to register an agent with this AWI? │
│    [y/N]:                                          │
│                                                     │
│ 🏷️  Agent name [BrowserUseAgent]:                 │
│                                                     │
│ 🔑 Available Permissions:                          │
│ • read - View posts, comments, and content        │
│ • write - Create posts and comments               │
│ • delete - Delete content (if allowed)            │
│                                                     │
│ Permissions [read,write]:                          │
│                                                     │
│ 📋 Registration Summary                            │
│ ┌──────────────────────────────────────────────┐  │
│ │ Agent Name: BrowserUseAgent                   │  │
│ │ Permissions: read, write                      │  │
│ │ AWI: Blog AWI                                 │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ ✅ Proceed with registration? [Y/n]:               │
└────────────────────────────────────────────────────┘
```

---

## Benefits of AWI Mode

| Aspect | Traditional DOM | AWI Mode |
|--------|----------------|----------|
| Tokens per page | 100,000+ | ~200 (500x reduction) |
| State management | None | Server-side sessions |
| Metadata | Must parse HTML | Structured semantic data |
| Available actions | Must guess from UI | Explicitly declared |
| Trajectory tracking | Manual | Built-in |
| Security validation | Client-side | Server-enforced |
| Stability | Brittle (CSS changes break it) | Stable (API contract) |

---

## Testing

Use the provided example script:

```bash
python examples/awi_mode_example.py
```

This demonstrates:
1. ✅ AWI discovery
2. ✅ Permission dialog
3. ✅ Agent registration
4. ✅ API interactions (list, create, search)
5. ✅ Session state queries
6. ✅ Trajectory tracking

---

## Configuration

### Environment Variables

```bash
# Enable AWI mode by default
BROWSER_USE_AWI_MODE=true

# Skip permission dialog (use defaults - NOT RECOMMENDED)
BROWSER_USE_AWI_AUTO_APPROVE=false

# Default permissions if auto-approve is enabled
BROWSER_USE_AWI_DEFAULT_PERMISSIONS=read,write
```

### Programmatic Configuration

```python
# Global AWI mode
from browser_use import config
config.awi_mode = True

# Per-agent AWI mode
agent = Agent(
    task="...",
    llm=...,
    browser=...,
    awi_mode=True,
    awi_auto_approve=False,  # Require user confirmation
    awi_default_permissions=['read', 'write']
)
```

---

## Error Handling

AWI mode includes robust fallback mechanisms:

```python
try:
    # Try AWI mode
    if awi_mode:
        result = await use_awi_api()
except AWINotAvailableError:
    # Fall back to DOM
    result = await use_dom_parsing()
except AWIPermissionDeniedError:
    # User declined or insufficient permissions
    result = await use_dom_parsing()
except AWIRegistrationError as e:
    # Registration failed
    logger.error(f"AWI registration failed: {e}")
    result = await use_dom_parsing()
```

---

## Future Enhancements

1. **Persistent API Keys**: Store approved API keys for reuse
2. **Multi-Site AWI**: Manage multiple AWI registrations
3. **AWI Session Resumption**: Resume interrupted AWI sessions
4. **Custom Action Mappings**: User-defined AWI action mappings
5. **AWI Discovery Cache**: Cache manifests to reduce lookups

---

## Support

For questions or issues:
- Check the AWI discovery example: `examples/awi_mode_example.py`
- Read the AWI discovery documentation: `backend/docs/AWI_DISCOVERY.md`
- View the implementation guide: `browser_use/awi/integration_guide.md`
