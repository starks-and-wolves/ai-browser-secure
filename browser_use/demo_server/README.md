# Browser-Use Demo Server

FastAPI backend for live browser-use demonstrations with WebSocket streaming.

## Features

- **Live Execution**: Run browser-use agents in real-time
- **WebSocket Streaming**: Real-time step updates and metrics
- **AWI & Permission Modes**: Support for both execution modes
- **Session Management**: Automatic cleanup of old sessions
- **Security**: API key validation, rate limiting, CORS protection

## Quick Start

### Local Development

```bash
# From repository root
cd browser_use/demo_server

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server starts on http://localhost:8000
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Start live demo session
curl -X POST http://localhost:8000/api/live/start \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Extract article title from this blog post",
    "mode": "awi",
    "target_url": "https://blog.anthropic.com",
    "api_key": "sk-..."
  }'

# Response: { "session_id": "...", "websocket_url": "/ws/live/..." }
```

## API Documentation

### Endpoints

**`GET /`** - Root endpoint
- Returns server info and version

**`GET /health`** - Health check
- Returns: `{"status": "healthy"}`

**`POST /api/live/start`** - Start live demo
- Request body:
  ```json
  {
    "task": "Task description",
    "mode": "awi" | "permission",
    "target_url": "https://example.com",
    "api_key": "sk-..."
  }
  ```
- Response:
  ```json
  {
    "session_id": "uuid",
    "websocket_url": "/ws/live/{session_id}",
    "message": "Session created"
  }
  ```

**`GET /api/live/sessions/{session_id}`** - Get session status
- Returns session info and current status

**`DELETE /api/live/sessions/{session_id}`** - Stop session
- Terminates execution and cleanup

**`WS /api/live/ws/live/{session_id}`** - WebSocket endpoint
- Real-time execution streaming
- Send: `{"api_key": "sk-..."}`
- Receive: Step updates, metrics, completion

### WebSocket Messages

**Client → Server:**
```json
{
  "api_key": "sk-..."
}
```

**Server → Client:**
```json
// Ready
{"type": "ready", "message": "Send API key to start"}

// Status update
{"type": "status", "message": "Starting execution...", "task": "..."}

// Agent started
{"type": "agent_started", "message": "Agent execution started"}

// Step update
{"type": "step", "step_number": 1, "action": "navigate", "timestamp": 123456}

// Completion
{"type": "completed", "success": true, "total_steps": 5, "result": {...}}

// Metrics
{"type": "metrics", "tokens": 89, "steps": 3, "cost": 0.001, "mode": "awi"}

// Agent Registry (AWI mode only)
{
  "type": "agent_registry",
  "message": "📋 Registered AWI agents: 1",
  "agents": [{
    "agent_id": "uuid",
    "agent_name": "agent-name",
    "domain": "example.com",
    "awi_name": "Example AWI",
    "permissions": ["read", "write"],
    "created_at": "2026-01-22T00:00:00",
    "last_used": "2026-01-22T00:00:00"
  }],
  "cli_command": "python -m browser_use.cli_agent_registry list"
}

// Error
{"type": "error", "message": "Error description"}
```

## Environment Variables

```bash
# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Optional: Default API key (users can override)
OPENAI_API_KEY=sk-...
```

## Production Deployment

See [docs/demo-ui/live-demo-deployment.md](../../docs/demo-ui/live-demo-deployment.md) for detailed deployment instructions.

### Deploy to Render

```bash
# 1. Push to GitHub
git add .
git commit -m "Add demo server"
git push origin main

# 2. Connect to Render
# Visit render.com → New Blueprint
# Select render.yaml from this directory

# 3. Configure environment variables
# Add CORS_ORIGINS with your frontend URL

# 4. Deploy!
```

### Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up

# Add environment variables
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

## Project Structure

```
demo_server/
├── main.py                 # FastAPI app and configuration
├── routers/
│   ├── __init__.py
│   └── live.py            # Live execution endpoints + WebSocket
├── requirements.txt        # Python dependencies
├── render.yaml            # Render.com deployment config
└── README.md              # This file
```

## Development

### Running with Auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing WebSocket Locally

Use a WebSocket client or browser console:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/live/ws/live/{session_id}')

ws.onopen = () => {
  ws.send(JSON.stringify({ api_key: 'sk-...' }))
}

ws.onmessage = (event) => {
  console.log(JSON.parse(event.data))
}
```

## Security Considerations

### API Key Handling
- API keys are **never logged** or stored
- Keys exist only in memory during execution
- Cleared immediately after session ends

### Rate Limiting
- Implement rate limiting to prevent abuse
- Suggested: 10 executions per hour per IP
- Use slowapi or similar library

### CORS
- Only allow trusted frontend URLs
- Never use `allow_origins=["*"]` in production
- Update CORS_ORIGINS when deploying

### Domain Whitelist
- Restrict target_url to approved domains
- Prevent access to internal networks
- Validate URL format before execution

## Troubleshooting

### WebSocket Connection Failed
- Enable WebSocket support in hosting provider
- Check CORS includes frontend URL
- Verify backend is deployed and healthy

### Browser-Use Import Error
```bash
# Install browser-use in development mode
pip install -e ../..
```

### Port Already in Use
```bash
# Change port
uvicorn main:app --port 8001
```

### Session Timeout
- Sessions auto-cleanup after 30 minutes
- Maximum execution time: 15 steps
- Cold start on free tier: ~30 seconds

## Monitoring

### Logs

```bash
# Local development
# Logs appear in terminal

# Production (Render)
# View in Render dashboard → Logs tab
```

### Metrics

Track:
- Active sessions
- Average execution time
- Token usage per mode
- Success/failure rate

## Cost Optimization

### Reduce Costs
- Use headless browser mode (already configured)
- Limit max_steps (prevents runaway executions)
- Set session timeout (30 minutes)
- Use free tier with cold starts

### Free Tier Limits
- Render Free: 750 hours/month
- Cold start: 30 seconds
- Spins down after 15 min inactivity

## Roadmap

- [ ] Add authentication for private demos
- [ ] Session recording and replay
- [ ] Cost tracking and analytics
- [ ] Screenshot streaming
- [ ] Multiple LLM provider support
- [ ] Admin dashboard

## Support

- **Issues**: [GitHub Issues](https://github.com/browser-use/browser-use/issues)
- **Docs**: [Live Demo Deployment](../../docs/demo-ui/live-demo-deployment.md)
- **Discord**: [Join Community](https://discord.gg/browser-use)

---

**Built with FastAPI + browser-use**
