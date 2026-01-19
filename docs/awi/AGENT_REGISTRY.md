# AWI Agent Registry

The Agent Registry provides persistent storage and management of AWI agent credentials, enabling agent reuse across sessions without re-registration.

## Overview

When an agent registers with an AWI-enabled website for the first time, the credentials are automatically stored in the registry. On subsequent runs, these credentials are automatically reused, eliminating the need for repeated permission dialogs and registration flows.

## Features

### Core Capabilities
- **Persistent Credential Storage**: Credentials saved to `~/.config/browseruse/config.json`
- **Automatic Reuse**: Stored credentials automatically detected and used
- **Multi-Agent Support**: Multiple agents per domain supported
- **Session Tracking**: Track usage statistics (last_used, session_count)
- **Credential Lifecycle**: Support for expiration and deactivation
- **Credential Rotation**: Update API keys without losing history

### Security Features
- Credentials stored locally on your machine
- Per-domain isolation
- Expiration timestamp support
- Active/inactive status management
- No cloud storage or transmission of credentials

## How It Works

### First Run (New Agent)
```
1. Agent starts with awi_mode=True
2. AWI discovered at target URL
3. No credentials found in registry
4. Permission dialog shown to user
5. New agent registered with AWI
6. Credentials stored in registry ✅
```

### Subsequent Runs (Existing Agent)
```
1. Agent starts with awi_mode=True
2. AWI discovered at target URL
3. Credentials found in registry ✅
4. Permission dialog SKIPPED
5. Credentials reused automatically
6. Last_used timestamp updated
```

## Configuration

### Storage Location

Credentials are stored in the browser-use config file:
```
~/.config/browseruse/config.json
```

### Config Structure

```json
{
  "agent_credentials": {
    "agent_123abc": {
      "id": "unique-uuid",
      "agent_id": "agent_123abc",
      "agent_name": "MyAgent",
      "domain": "localhost:5000",
      "awi_name": "Blog AWI",
      "api_key": "key_xyz789",
      "permissions": ["read", "write"],
      "description": "Browser-use agent for blog automation",
      "agent_type": "browser-use",
      "framework": "python",
      "created_at": "2024-01-17T10:00:00",
      "last_used": "2024-01-17T15:30:00",
      "session_count": 5,
      "is_active": true,
      "expires_at": null,
      "manifest_version": "1.0",
      "notes": null
    }
  }
}
```

## Usage

### Programmatic Access

```python
from browser_use.agent_registry import agent_registry

# Check if credentials exist
if agent_registry.has_credentials('localhost:5000'):
    print('Credentials found!')

# Get credentials for a domain
cred = agent_registry.get_credentials('localhost:5000')
if cred:
    print(f'Agent: {cred.agent_name}')
    print(f'API Key: {cred.api_key}')

# Store new credentials
agent_registry.store_credentials(
    agent_id='agent_123',
    agent_name='MyAgent',
    domain='localhost:5000',
    api_key='key_xyz789',
    permissions=['read', 'write'],
    awi_name='Blog AWI'
)

# List all credentials
all_creds = agent_registry.list_credentials()
for cred in all_creds:
    print(f'{cred.agent_name} @ {cred.domain}')

# Delete credentials
agent_registry.delete_credentials('agent_123')
```

### CLI Management

#### List All Agents
```bash
python -m browser_use.cli_agent_registry list
```

Output:
```
📋 Registered AWI Agents:
┌────────────────┬──────────┬────────────────┬─────────────────┬────────────┬──────────┬────────┐
│ Agent ID       │ Name     │ Domain         │ Permissions     │ Last Used  │ Sessions │ Status │
├────────────────┼──────────┼────────────────┼─────────────────┼────────────┼──────────┼────────┤
│ agent_123ab... │ MyAgent  │ localhost:5000 │ read, write     │ 2h ago     │ 5        │ ✅     │
└────────────────┴──────────┴────────────────┴─────────────────┴────────────┴──────────┴────────┘

Total: 1 agent(s)
```

#### Show Agent Details
```bash
python -m browser_use.cli_agent_registry show agent_123abc
```

#### Delete Agent
```bash
# Interactive (asks for confirmation)
python -m browser_use.cli_agent_registry delete agent_123abc

# Skip confirmation
python -m browser_use.cli_agent_registry delete agent_123abc --yes
```

#### Deactivate Agent
```bash
# Mark as inactive (preserves credentials)
python -m browser_use.cli_agent_registry deactivate agent_123abc
```

#### Cleanup Expired Credentials
```bash
python -m browser_use.cli_agent_registry cleanup
```

## Integration with Agent Flow

The registry integrates seamlessly with the AWI discovery flow in `browser_use/agent/service.py`:

```python
# In agent initialization
agent = Agent(
    task="Your task",
    llm=llm,
    browser=browser,
    awi_mode=True,  # Enable AWI mode
)

# First run:
# 1. AWI discovered
# 2. No credentials in registry
# 3. Permission dialog shown
# 4. Agent registered
# 5. Credentials stored ✅

# Second run (same domain):
# 1. AWI discovered
# 2. Credentials found in registry ✅
# 3. Dialog skipped
# 4. Credentials reused
# 5. Session count incremented
```

## Advanced Features

### Credential Rotation

```python
from browser_use.agent_registry import agent_registry

# Rotate API key for an agent
agent_registry.rotate_credentials(
    agent_id='agent_123',
    new_api_key='new_key_xyz',
    new_permissions=['read', 'write', 'admin']
)
```

### Expiration Management

```python
from datetime import datetime, timedelta

# Set expiration (30 days from now)
expiration = (datetime.utcnow() + timedelta(days=30)).isoformat()

agent_registry.store_credentials(
    agent_id='agent_123',
    agent_name='MyAgent',
    domain='localhost:5000',
    api_key='key_xyz',
    permissions=['read'],
    expires_at=expiration
)

# Check if expired
cred = agent_registry.get_credentials_by_id('agent_123')
if cred and cred.is_expired():
    print('Credentials expired!')
```

### Multi-Agent Support

```python
# Register multiple agents for the same domain
agent_registry.store_credentials(
    agent_id='agent_read',
    agent_name='ReadOnlyAgent',
    domain='localhost:5000',
    api_key='key_read',
    permissions=['read']
)

agent_registry.store_credentials(
    agent_id='agent_write',
    agent_name='AdminAgent',
    domain='localhost:5000',
    api_key='key_admin',
    permissions=['read', 'write', 'admin']
)

# Get specific agent by name
cred = agent_registry.get_credentials('localhost:5000', agent_name='AdminAgent')
```

### Domain Normalization

The registry automatically normalizes URLs for consistent lookup:

```python
# All of these map to the same domain: "localhost:5000"
agent_registry.get_credentials('http://localhost:5000')
agent_registry.get_credentials('http://localhost:5000/')
agent_registry.get_credentials('localhost:5000')
agent_registry.get_credentials('http://localhost:5000/api')
```

## Security Considerations

### Storage Security
- Credentials stored in plain text in local config file
- File located at `~/.config/browseruse/config.json`
- Permissions: Readable only by file owner (standard Unix permissions)
- **Recommendation**: Secure your config directory appropriately

### API Key Protection
- API keys are full-length in storage
- CLI shows truncated keys (`key_abc...xyz`)
- Never log or print full API keys in production
- Consider encrypting config file for sensitive environments

### Best Practices
1. **Rotate credentials regularly**: Use `rotate_credentials()`
2. **Set expiration dates**: Use `expires_at` parameter
3. **Cleanup old credentials**: Run `cleanup_expired()` periodically
4. **Use minimal permissions**: Only grant necessary permissions
5. **Deactivate unused agents**: Use `deactivate_credentials()`

## Rate Limiting and Reputation

### Understanding Rate Limits

AWI backends enforce rate limits to prevent abuse. Agents are tracked by their API key (stored in agent registry):

```json
{
  "limits": {
    "hourly": 300,      // Max 300 operations per hour
    "minute": 30,       // Max 30 operations per minute
    "burst": 9,         // Max 9 rapid-fire operations
    "cooldown": 5       // Min 5 seconds between requests
  },
  "reputation": "normal"
}
```

### Reputation System

Agent reputation affects rate limits:

| Reputation | Hourly Limit | Cooldown | Status |
|------------|--------------|----------|--------|
| `new` | 150 (50% of normal) | 10s | First 24 hours |
| `normal` | 300 (standard) | 5s | Good standing |
| `trusted` | 900 (3x normal) | 2s | Consistent good behavior |
| `throttled` | 75 (25% of normal) | 20s | Recent violations |

### Building Reputation

To improve your agent's reputation:

1. **Consistent usage**: Use agent regularly over days/weeks
2. **Respect retryAfter**: Never ignore rate limit retry hints
3. **Low error rates**: Validate requests before sending
4. **Graceful failures**: Implement proper error handling
5. **Exponential backoff**: Use intelligent retry logic

### Handling Rate Limits

When rate limited, the error contains retry information:

```python
ERROR [generic_tool] ❌ AWI Execute failed: Rate limit exceeded.
Details: operation: create_comment; reason: cooldown period; retryAfter: 5;
limits: {'hourly': 300, 'minute': 30, 'burst': 9, 'cooldown': 5};
reputation: normal
```

**Best practices:**
- Wait `retryAfter` seconds before retry
- Implement exponential backoff for multiple retries
- Add delays between batch operations
- Monitor session_count to track usage patterns

**Example retry logic:**
```python
import asyncio

async def execute_with_retry(operation, max_retries=3):
    base_delay = 1.0
    for attempt in range(max_retries + 1):
        result = await execute_operation(operation)

        if 'Rate limit exceeded' in result.error:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                continue
        return result
```

**See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#rate-limiting) for detailed rate limit handling.**

## Troubleshooting

### Credentials Not Found

**Problem**: Agent shows permission dialog every time

**Solution**:
```bash
# Check if credentials exist
python -m browser_use.cli_agent_registry list

# Verify domain format matches
python -m browser_use.cli_agent_registry list localhost:5000
```

### Expired Credentials

**Problem**: "Credentials expired" error

**Solution**:
```bash
# Remove expired credentials
python -m browser_use.cli_agent_registry cleanup

# Re-register agent (will prompt for permission)
```

### Multiple Agents Conflict

**Problem**: Wrong agent credentials used

**Solution**:
```python
# Specify agent name explicitly
cred = agent_registry.get_credentials(
    domain='localhost:5000',
    agent_name='MySpecificAgent'
)
```

### Config File Corruption

**Problem**: "Failed to load config" error

**Solution**:
```bash
# Backup current config
cp ~/.config/browseruse/config.json ~/.config/browseruse/config.json.bak

# Reset to defaults (will delete all credentials!)
rm ~/.config/browseruse/config.json

# Or manually fix JSON syntax in config file
```

## API Reference

### AgentRegistry Methods

#### `store_credentials(...) -> AgentCredentialEntry`
Store new agent credentials in registry.

#### `get_credentials(domain, agent_name=None) -> Optional[AgentCredentialEntry]`
Get credentials for a domain, optionally filtered by agent name.

#### `get_credentials_by_id(agent_id) -> Optional[AgentCredentialEntry]`
Get credentials by agent ID.

#### `update_last_used(agent_id) -> bool`
Update the last used timestamp.

#### `deactivate_credentials(agent_id) -> bool`
Mark credentials as inactive.

#### `delete_credentials(agent_id) -> bool`
Permanently delete credentials.

#### `list_credentials(domain=None, active_only=True) -> list[AgentCredentialEntry]`
List all credentials, optionally filtered.

#### `cleanup_expired() -> int`
Remove expired credentials.

#### `rotate_credentials(agent_id, new_api_key, new_permissions=None) -> bool`
Rotate credentials for an agent.

#### `has_credentials(domain) -> bool`
Check if credentials exist for a domain.

### AgentCredentialEntry Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique UUID |
| `agent_id` | str | Agent ID from AWI |
| `agent_name` | str | Human-readable name |
| `domain` | str | Normalized domain |
| `awi_name` | str | AWI service name |
| `api_key` | str | Authentication key |
| `permissions` | list[str] | Granted permissions |
| `description` | str \| None | Optional description |
| `agent_type` | str | Agent type |
| `framework` | str | Framework used |
| `created_at` | str | Creation timestamp |
| `last_used` | str \| None | Last usage timestamp |
| `session_count` | int | Number of sessions |
| `expires_at` | str \| None | Expiration timestamp |
| `is_active` | bool | Active status |
| `manifest_version` | str \| None | AWI manifest version |
| `notes` | str \| None | User notes |

## Examples

### Example 1: Basic Usage

```python
from browser_use import Agent, Browser
from browser_use.llm import get_default_llm

# First run - will show permission dialog
agent = Agent(
    task="Add a comment to the top blog post",
    llm=get_default_llm(),
    browser=Browser(headless=False),
    awi_mode=True  # Enable AWI
)

result = await agent.run()
# Credentials automatically stored ✅

# Second run - no permission dialog!
agent2 = Agent(
    task="Add another comment",
    llm=get_default_llm(),
    browser=Browser(headless=False),
    awi_mode=True
)

result2 = await agent2.run()
# Credentials automatically reused ✅
```

### Example 2: Manual Credential Management

```python
from browser_use.agent_registry import agent_registry

# Store credentials manually
agent_registry.store_credentials(
    agent_id='my_agent_123',
    agent_name='BlogBot',
    domain='myblog.com',
    api_key='secret_key_xyz',
    permissions=['read', 'write'],
    awi_name='My Blog API',
    notes='Production bot for blog automation'
)

# Later, retrieve and use
cred = agent_registry.get_credentials('myblog.com')
print(f'Using agent: {cred.agent_name}')
print(f'Sessions: {cred.session_count}')
```

### Example 3: Credential Lifecycle

```python
from datetime import datetime, timedelta
from browser_use.agent_registry import agent_registry

# Create credential with 30-day expiration
expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()

agent_registry.store_credentials(
    agent_id='temp_agent',
    agent_name='TemporaryAgent',
    domain='test.com',
    api_key='temp_key',
    permissions=['read'],
    expires_at=expiry
)

# ... time passes ...

# Check expiration
cred = agent_registry.get_credentials_by_id('temp_agent')
if cred and cred.is_expired():
    print('Expired! Deleting...')
    agent_registry.delete_credentials('temp_agent')
else:
    print(f'Still valid, {cred.session_count} sessions used')
```

## Migration from Previous Versions

If you were using browser-use before the agent registry was added, no migration is needed. The system will:

1. Continue to work normally
2. Show permission dialogs as before (first time only)
3. Automatically start storing credentials on first registration
4. Reuse credentials on subsequent runs

## Future Enhancements

Planned features for future releases:

- [ ] Encrypted credential storage
- [ ] Integration with system keychain (macOS Keychain, Windows Credential Manager)
- [ ] Credential sharing across machines (opt-in)
- [ ] Automatic credential refresh/renewal
- [ ] Audit logging for credential access
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant support

## Contributing

To contribute to the agent registry:

1. Read the source code: `browser_use/agent_registry.py`
2. Read the config system: `browser_use/config.py` (AgentCredentialEntry)
3. Integration point: `browser_use/agent/service.py` (_try_awi_discovery)

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Documentation: `/docs/awi/` directory
- Examples: `/examples/awi_mode_*.py`
