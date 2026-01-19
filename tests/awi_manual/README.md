# AWI Manual Tests

This directory contains manual test scripts for the AWI (Agent Web Interface) mode feature.

## Overview

These tests verify AWI mode functionality and require a running backend server (typically on `localhost:5000`) with MongoDB and Redis.

## Test Files

### 🎯 Primary Test (Recommended)
**`test_full_awi_mode_fixed.py`** - Complete AWI workflow test
- Full integration test with all AWI features
- Includes infinite loop prevention
- Clear task completion criteria
- **Start here for testing AWI mode**

### 🔧 Component Tests
**`test_awi_permission_dialog.py`** - Permission dialog flow
- Tests user approval flow
- Validates permission handling
- Useful for debugging auth issues

**`test_discovery_live.py`** - AWI discovery mechanism
- Tests automatic AWI detection
- Validates manifest parsing
- Checks HTTP header discovery

**`test_awi_automated_full.py`** - Automated test suite
- Full automated test with auto-approval
- Good for CI/CD integration
- No user interaction required

### 🔍 Verification Tests
**`test_awi_full_verification.py`** - Comprehensive verification
- End-to-end validation
- Tests all AWI operations
- Verifies session state tracking

**`test_redis_functionality.py`** - Redis integration
- Tests session management
- Validates Redis connectivity
- Verifies state persistence

### 🎨 Demo
**`demo_create_blog_post.py`** - Interactive demo
- Demonstrates AWI capabilities
- Shows blog post creation workflow
- Educational example

### 🚀 Runner Script
**`RUN_AWI_TEST.sh`** - Convenience script
- Runs recommended test suite
- Sets up environment
- Handles common setup tasks

## Quick Start

### 1. Prerequisites
Ensure these services are running:
```bash
# Backend server
http://localhost:5000

# MongoDB (default port 27017)
mongod

# Redis (default port 6379)
redis-server
```

### 2. Environment Setup
```bash
# Set your LLM API key
export OPENAI_API_KEY=your_key_here

# Optional: Custom backend URL
export AWI_BASE_URL=http://localhost:5000
```

### 3. Run Tests

**Recommended first test:**
```bash
cd tests/awi_manual
python test_full_awi_mode_fixed.py
```

**Or use the shell script:**
```bash
chmod +x RUN_AWI_TEST.sh
./RUN_AWI_TEST.sh
```

**For automated testing (no user interaction):**
```bash
python test_awi_automated_full.py
```

## Test Execution Flow

1. **Permission Test** → Verify auth flow works
2. **Discovery Test** → Confirm AWI detection
3. **Full Mode Test** → Run complete workflow
4. **Verification Test** → Validate all operations

## Expected Behavior

When AWI mode activates successfully:
- ✅ Agent discovers AWI via HTTP headers
- ✅ Permission dialog appears (manual tests)
- ✅ Agent registers with the AWI
- ✅ Agent uses API calls instead of DOM interaction
- ✅ Session state is tracked in Redis
- ✅ Task completes without DOM parsing

## Common Issues

### Backend Not Running
```
Error: Connection refused to localhost:5000
Fix: Start the backend server
```

### MongoDB Not Running
```
Error: MongoNetworkError
Fix: Start MongoDB with 'mongod'
```

### Redis Not Running
```
Error: Redis connection failed
Fix: Start Redis with 'redis-server'
```

### Permission Denied
```
Error: User declined AWI registration
Fix: Type 'y' when permission dialog appears
```

### Empty URL Navigation Error
```
Error: Navigation to  blocked by security policy
Fix: This has been fixed in latest code - update your branch
```

## Test Modes

- **Manual Tests**: Require user input for permission dialogs (most tests)
- **Automated Tests**: Use auto-approval for headless execution (`test_awi_automated_full.py`)
- **Demo Scripts**: Interactive demonstrations (`demo_create_blog_post.py`)

## For Developers

### File Naming Convention
- `test_*_fixed.py` = Latest fixed version (use this)
- `test_*_full.py` = Complete test suite
- `demo_*.py` = Interactive demonstrations

### Adding New Tests
1. Follow existing test patterns
2. Include prerequisites check
3. Add clear error messages
4. Document expected behavior
5. Test with real backend server

### CI Integration
Use `test_awi_automated_full.py` for CI pipelines:
- No user interaction required
- Auto-approval enabled
- Clear pass/fail output

## Documentation

For more information:
- **Implementation**: `/browser_use/awi/` - Core AWI code
- **Documentation**: `/docs/awi/` - All AWI documentation
- **Examples**: `/examples/awi_mode_*.py` - Usage examples

## Need Help?

1. Check `/docs/awi/README.md` for documentation index
2. Review `/docs/awi/HOWTO_RUN_AWI_MODE.md` for detailed setup
3. See `/docs/awi/DEBUG_AND_SOLUTION.md` for troubleshooting

---

**Note**: These are manual/integration tests, not unit tests. For CI unit tests, see `/tests/ci/` directory.
