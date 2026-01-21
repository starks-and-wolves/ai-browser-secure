# AWI (Agent Web Interface) Documentation

Complete documentation for AWI mode in browser-use.

## What is AWI?

AWI (Agent Web Interface) enables AI agents to interact with websites through structured APIs instead of traditional DOM parsing and browser automation. It provides faster, more reliable, and more secure agent-website interactions.

## Quick Links

### Getting Started
- **[QUICKSTART.md](./QUICKSTART.md)** - Get up and running with AWI mode in minutes
- **[AWI_OVERVIEW.md](./AWI_OVERVIEW.md)** - Understand AWI architecture and concepts

### Core Features
- **[AGENT_REGISTRY.md](./AGENT_REGISTRY.md)** - Manage agent credentials and enable seamless reuse
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Solve common issues and handle rate limits

### Advanced Topics: LLM Optimization
- **[LLM_OPTIMIZATION.md](./LLM_OPTIMIZATION.md)** - Comprehensive guide for optimizing AWI manifests for different LLM capabilities
- **[AWI_OPTIMIZATION_IMPLEMENTATION.md](./AWI_OPTIMIZATION_IMPLEMENTATION.md)** - Implementation details: model detection and adaptive manifest serving
- **[TWO_PHASE_IMPLEMENTATION_SUMMARY.md](./TWO_PHASE_IMPLEMENTATION_SUMMARY.md)** - Simplified body construction for weak models

## Documentation Structure

### 1. [AWI Overview](./AWI_OVERVIEW.md)

**What you'll learn:**
- What is AWI and how it works
- Architecture and core components
- AWI vs traditional browser automation
- Security considerations and rate limiting
- AWI manifest specification

**Start here if:** You're new to AWI or want to understand the system architecture.

### 2. [Quick Start Guide](./QUICKSTART.md)

**What you'll learn:**
- Installation and environment setup
- Creating your first AWI agent
- Permission dialog and approval flow
- Configuration options (LLM, browser, agent)
- Example tasks and best practices

**Start here if:** You want to start using AWI mode immediately.

### 3. [Agent Registry Guide](./AGENT_REGISTRY.md)

**What you'll learn:**
- Persistent credential storage
- Automatic credential reuse (no repeated permission dialogs)
- CLI tools for credential management
- Credential lifecycle (rotation, expiration, cleanup)
- Multi-agent support per domain
- Rate limiting and reputation system

**Start here if:** You want to manage agent credentials or understand credential reuse.

### 4. [Troubleshooting Guide](./TROUBLESHOOTING.md)

**What you'll learn:**
- Common issues and solutions
- Rate limiting and how to handle it
- Request body validation errors
- Credential management problems
- Agent behavior debugging
- Backend connectivity issues

**Start here if:** You're encountering errors or unexpected behavior.

### 5. [LLM Optimization Guide](./LLM_OPTIMIZATION.md)

**What you'll learn:**
- Optimizing AWI manifests for different model capabilities (GPT-4, GPT-3.5, weak models)
- Token usage reduction strategies (99.5% savings possible)
- Progressive disclosure and format parameters
- llm_quick_reference implementation
- Best practices for multi-tier model support

**Start here if:** You want to optimize your AWI backend for different LLM capabilities or reduce token costs.

### 6. [AWI Optimization Implementation](./AWI_OPTIMIZATION_IMPLEMENTATION.md)

**What you'll learn:**
- How browser-use detects model capabilities
- Automatic manifest format selection
- BodyConstructor quick reference prioritization
- Context message adaptation for different models
- Testing recommendations and backward compatibility

**Start here if:** You want to understand how browser-use client implements model-aware optimization.

### 7. [Two-Phase Body Construction](./TWO_PHASE_IMPLEMENTATION_SUMMARY.md)

**What you'll learn:**
- Simplified approach for constructing API request bodies
- Why weak models struggle with body construction
- field_values parameter usage
- Test results and recommendations

**Start here if:** You're working with weak models (gpt-5-nano, GPT-3.5) and encountering empty body issues.

## Key Concepts

### AWI Discovery
Agents automatically discover AWI capabilities at `/.well-known/llm-text`:
```python
agent = Agent(task="Your task", llm=llm, browser=browser, awi_mode=True)
result = await agent.run()  # Automatically discovers AWI if available
```

### Permission Model
Users approve agent registration once per domain:
- **read**: View data
- **write**: Create/update data
- **admin**: Full access

### Credential Reuse
Credentials stored after first registration:
- **First run**: Permission dialog → Register → Store credentials
- **Subsequent runs**: Load credentials → Skip dialog → Reuse

### Rate Limiting
AWI backends enforce rate limits with reputation-based tiers:
- **new**: 150 req/hr (first 24h)
- **normal**: 300 req/hr (standard)
- **trusted**: 900 req/hr (good behavior)
- **throttled**: 75 req/hr (violations)

## File Organization

### Core Documentation
```
docs/awi/
├── README.md                              # This file - documentation index
├── AWI_OVERVIEW.md                        # Architecture and concepts
├── QUICKSTART.md                          # Getting started guide
├── AGENT_REGISTRY.md                      # Credential management
├── TROUBLESHOOTING.md                     # Common issues and solutions
│
└── Advanced Optimization:
    ├── LLM_OPTIMIZATION.md                # Manifest optimization for different models
    ├── AWI_OPTIMIZATION_IMPLEMENTATION.md # Client-side model detection
    └── TWO_PHASE_IMPLEMENTATION_SUMMARY.md# Simplified body construction
```

### Implementation Files (Reference only)
```
browser_use/awi/
├── discovery.py           # AWI manifest discovery
├── permission_dialog.py   # User approval dialog
├── manager.py             # AWI session management
├── generic_tool.py        # LLM-driven API execution
└── __init__.py

browser_use/
├── agent_registry.py      # Credential storage and management
├── cli_agent_registry.py  # CLI tool for credential management
└── agent/service.py       # Agent integration (_try_awi_discovery)
```

### Examples
```
examples/
└── awi_mode_*.py          # Example scripts using AWI mode
```

### Tests
```
tests/awi_manual/
└── test_*.py              # Manual tests for AWI functionality
```

## Common Workflows

### First-Time Setup

1. **Install browser-use**
   ```bash
   pip install browser-use
   ```

2. **Set environment variables**
   ```bash
   export OPENAI_API_KEY='your-key'
   export DEFAULT_LLM_MODEL='gpt-4o'
   ```

3. **Create agent with AWI mode**
   ```python
   agent = Agent(task="Your task", llm=get_default_llm(), browser=Browser(), awi_mode=True)
   result = await agent.run()
   ```

4. **Approve permission dialog**
   - Review requested permissions
   - Type `yes` and press Enter
   - Credentials stored automatically

### Daily Usage

```python
# Credentials reused automatically - no dialog!
agent = Agent(task="Your task", llm=get_default_llm(), browser=Browser(), awi_mode=True)
result = await agent.run()
```

### Managing Credentials

```bash
# List registered agents
python -m browser_use.cli_agent_registry list

# Show agent details
python -m browser_use.cli_agent_registry show <agent_id>

# Delete agent
python -m browser_use.cli_agent_registry delete <agent_id>

# Cleanup expired credentials
python -m browser_use.cli_agent_registry cleanup
```

### Debugging

1. **Enable debug logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check AWI discovery**
   ```bash
   curl http://localhost:5000/.well-known/llm-text
   ```

3. **Verify credentials**
   ```bash
   python -m browser_use.cli_agent_registry list
   ```

4. **Review logs for patterns**
   - ✅ "AWI Mode active" = Success
   - ❌ "No AWI found" = Check backend
   - ⚠️ "Rate limit exceeded" = Add delays

## Benefits of AWI

### Speed
- **Traditional**: Seconds per action (render + parse)
- **AWI**: Milliseconds per action (direct API)

### Reliability
- **Traditional**: Breaks with UI changes
- **AWI**: Stable API contracts

### Security
- **Traditional**: Full DOM access
- **AWI**: Scoped permissions (read/write/admin)

### Resource Usage
- **Traditional**: Heavy (browser rendering)
- **AWI**: Light (HTTP requests only)

## Example: Blog Automation

**Traditional approach:**
```python
# Navigate, find elements, click, type (fragile, slow)
await agent.navigate('http://blog.com')
posts = await agent.find_elements('.post-link')
await posts[0].click()
comment_box = await agent.find_element('#comment-input')
await comment_box.type('Great post!')
submit = await agent.find_element('button[type="submit"]')
await submit.click()
```

**AWI approach:**
```python
# Direct API calls (fast, reliable)
agent = Agent(
    task="Add comment 'Great post!' to the first blog post",
    llm=get_default_llm(),
    browser=Browser(),
    awi_mode=True  # ← Uses AWI automatically
)
result = await agent.run()
# Agent uses structured API calls internally
```

## Advanced Topics

### Custom AWI Backends

See AWI specification in [AWI_OVERVIEW.md](./AWI_OVERVIEW.md#awi-manifest-specification) for implementing your own AWI-enabled backend.

### Rate Limit Strategies

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#rate-limiting) for:
- Exponential backoff implementation
- Batch operation spacing
- Reputation building tactics

### Multi-Agent Deployments

See [AGENT_REGISTRY.md](./AGENT_REGISTRY.md#multi-agent-support) for:
- Multiple agents per domain
- Agent name filtering
- Credential isolation

## Support

### Documentation Issues
- File an issue: https://github.com/browser-use/browser-use/issues
- Tag with `documentation` label

### Feature Requests
- File an issue: https://github.com/browser-use/browser-use/issues
- Tag with `enhancement` and `awi` labels

### Bug Reports
- File an issue with:
  - Full error logs
  - Reproduction steps
  - Environment details (OS, Python version, browser-use version)
  - AWI manifest (if applicable)

## Contributing

Improvements to documentation are welcome:

1. Fork the repository
2. Edit files in `docs/awi/`
3. Submit a pull request
4. Tag maintainers for review

## Version History

- **v0.11.2** (2026-01-17): Added agent registry with credential reuse
- **v0.11.0**: Generic AWI tool implementation
- **v0.10.0**: Initial AWI mode support

## License

Documentation licensed under the same license as browser-use.
