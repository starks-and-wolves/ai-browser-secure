# Live Demo Deployment Guide

This guide covers deploying the complete demo UI with live execution capabilities (frontend + backend).

## Architecture

```
Users → Vercel (Next.js Frontend)
          ↓
        /showcase → Pre-recorded demos (static JSON)
        /live → WebSocket connection
          ↓
        Render (FastAPI Backend)
          ↓
        Browser-Use Agent → Live execution
```

---

## Backend Deployment (Render.com)

### Prerequisites

- GitHub repository
- Render.com account (free tier available)
- OpenAI API key

### Step 1: Prepare Repository

```bash
# Commit all changes
git add .
git commit -m "Add live demo backend"
git push origin main
```

### Step 2: Deploy to Render

**Option 1: Blueprint (Recommended)**

1. Visit [render.com](https://render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select `browser_use/demo_server/render.yaml`
5. Click "Apply"

**Option 2: Manual Setup**

1. Visit [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect GitHub repository
4. Configure:
   ```
   Name: browser-use-demo-backend
   Runtime: Python 3.11
   Root Directory: (leave empty)
   Build Command:
   pip install uv && \
   uv pip install -e . && \
   cd browser_use/demo_server && \
   pip install -r requirements.txt

   Start Command:
   cd browser_use/demo_server && \
   uvicorn main:app --host 0.0.0.0 --port $PORT

   Plan: Starter ($7/month)
   ```

### Step 3: Configure Environment Variables

Add these environment variables in Render dashboard:

```bash
# CORS origins (add your Vercel URL after frontend deployment)
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Optional: OpenAI API key (users can provide their own)
OPENAI_API_KEY=sk-...
```

### Step 4: Enable WebSocket Support

1. Go to Settings → Advanced
2. Enable "WebSocket Support"
3. Save changes

### Step 5: Deploy

- Click "Create Web Service"
- Wait 5-10 minutes for first deployment
- Backend URL: `https://browser-use-demo-backend.onrender.com`

### Step 6: Test Backend

```bash
# Health check
curl https://browser-use-demo-backend.onrender.com/health

# Should return: {"status":"healthy"}
```

---

## Frontend Deployment (Vercel)

### Step 1: Set Environment Variable

Create `.env.production` in `demo-ui/`:

```bash
NEXT_PUBLIC_API_URL=https://browser-use-demo-backend.onrender.com
```

### Step 2: Deploy to Vercel

**Option 1: Vercel Dashboard**

1. Visit [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   ```
   Framework Preset: Next.js
   Root Directory: demo-ui
   Build Command: npm run build
   Output Directory: .next
   ```

5. Add environment variable:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://browser-use-demo-backend.onrender.com
   ```

6. Click "Deploy"

**Option 2: Vercel CLI**

```bash
cd demo-ui
npm install -g vercel
vercel login
vercel --prod
```

### Step 3: Update Backend CORS

After frontend is deployed, update backend environment variable:

```bash
# In Render dashboard, update CORS_ORIGINS:
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## Testing Live Demo

### Test Locally (Before Deployment)

**Terminal 1: Start Backend**
```bash
cd browser_use/demo_server
python main.py
# Backend running on http://localhost:8000
```

**Terminal 2: Start Frontend**
```bash
cd demo-ui
npm run dev
# Frontend running on http://localhost:3000
```

**Visit**: http://localhost:3000/live

### Test Production

1. Visit: `https://your-app.vercel.app/live`
2. Configure demo:
   - Mode: AWI or Permission
   - Target: https://blog.anthropic.com
   - Task: "Extract the main article content and title"
   - API Key: `sk-...` (your OpenAI key)
3. Click "Start Demo"
4. Watch real-time execution in log panel

---

## Pre-configured Blog Post Demos

### AWI Mode - Blog Extraction

**Target**: https://blog.anthropic.com
**Task**: "Extract the main article title and first 3 paragraphs from the latest blog post"
**Expected**:
- 2-3 API calls
- ~50-80 tokens
- $0.001 cost
- 1-2 seconds

### Permission Mode - Secure Browsing

**Target**: https://medium.com
**Task**: "Find the top trending article about AI and extract its title"
**Expected**:
- 5-8 steps
- Domain approval prompts
- ~500-800 tokens
- $0.005-0.008 cost

---

## Monitoring & Debugging

### Backend Logs (Render)

1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time logs

### Common Issues

**1. WebSocket Connection Failed**

```
Error: WebSocket connection to 'wss://...' failed
```

**Solution**:
- Ensure WebSocket support is enabled in Render settings
- Check CORS configuration includes frontend URL
- Verify backend is deployed and healthy

**2. API Key Invalid**

```
Error: Authentication failed
```

**Solution**:
- Verify OpenAI API key is valid
- Check key has sufficient credits
- Ensure key format is correct (starts with `sk-`)

**3. Task Timeout**

```
Error: Task timed out after 15 steps
```

**Solution**:
- Simplify task description
- Target simpler websites
- AWI mode is faster - use it when possible

**4. CORS Error**

```
Error: CORS policy blocked
```

**Solution**:
- Update `CORS_ORIGINS` in Render to include your Vercel URL
- Ensure both HTTP and HTTPS versions are included
- Redeploy backend after updating

---

## Cost Breakdown

### Monthly Costs

**Render (Backend)**:
- Starter Plan: $7/month
- Includes: 512 MB RAM, always-on
- WebSocket support included

**Vercel (Frontend)**:
- Hobby Plan: Free
- Includes: 100GB bandwidth/month
- Automatic SSL

**LLM Usage** (user-provided API keys):
- Users pay for their own LLM costs
- Typical demo: $0.001-0.01 per execution

**Total**: $7/month (or free if using Render free tier with cold starts)

### Free Tier Option

Render offers a free tier with limitations:
- Services spin down after 15 minutes of inactivity
- 30-second cold start delay
- 750 hours/month (enough for demo)

To use free tier:
1. Select "Free" plan instead of "Starter"
2. Accept cold start delays
3. Add note on live demo page: "First execution may take 30 seconds (cold start)"

---

## Security Best Practices

### API Key Handling

- ✅ Never log API keys
- ✅ Never store API keys in database
- ✅ Use API keys only in memory during execution
- ✅ Clear API key after session ends
- ❌ Never commit API keys to git

### Rate Limiting

Add to `browser_use/demo_server/routers/live.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/start")
@limiter.limit("10/hour")  # 10 executions per hour per IP
async def start_live_demo(request: Request, demo_request: LiveDemoRequest):
    # ... existing code
```

### Domain Whitelist

For permission mode, restrict to safe domains:

```python
ALLOWED_DOMAINS = [
    "anthropic.com",
    "medium.com",
    "techcrunch.com",
    "blog.google",
]

if not any(domain in request.target_url for domain in ALLOWED_DOMAINS):
    raise HTTPException(400, "Domain not whitelisted for demo")
```

---

## Updating Deployment

### Backend Updates

```bash
# Make changes
git add .
git commit -m "Update backend"
git push origin main

# Render auto-deploys on push to main
# Wait 2-3 minutes for deployment
```

### Frontend Updates

```bash
# Make changes
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys on push to main
# Deployment completes in ~1 minute
```

---

## Rollback Procedure

### Render Rollback

1. Go to Render dashboard
2. Click "Deploys" tab
3. Select previous working deployment
4. Click "Redeploy"

### Vercel Rollback

1. Go to Vercel dashboard
2. Click "Deployments"
3. Select previous working deployment
4. Click "..." → "Promote to Production"

---

## Performance Optimization

### Backend

- Use headless browser mode (already configured)
- Limit max_steps to 15 (prevents runaway executions)
- Enable response compression in FastAPI
- Use connection pooling for database (if added later)

### Frontend

- WebSocket reconnection logic (already implemented)
- Loading states during execution (already implemented)
- Throttle log updates to avoid UI lag
- Use React.memo for heavy components

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Update CORS configuration
4. ✅ Test live demo end-to-end
5. 📝 Add analytics (PostHog/Plausible)
6. 📝 Add demo recording feature
7. 📝 Add session replay
8. 📝 Add cost calculator

---

## Support

**Issues**:
- Backend: Check Render logs
- Frontend: Check Vercel deployment logs
- WebSocket: Check browser console for errors

**Documentation**:
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [browser-use GitHub](https://github.com/browser-use/browser-use)

---

**Ready to deploy?** Start with backend deployment, then frontend!
