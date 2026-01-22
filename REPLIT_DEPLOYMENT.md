# 🚀 Replit Deployment Guide

This guide walks you through deploying the browser-use demo server and UI on Replit.

## 📋 Prerequisites

- GitHub account
- Replit account (free tier works!)
- OpenAI, Anthropic, or Browser-Use API key

---

## 🔧 Option 1: Two Separate Repls (Recommended)

Deploy backend and frontend as separate Repls for easier management.

### 🐍 Backend Deployment

#### 1. Create Backend Repl

1. Go to https://replit.com
2. Click **"+ Create Repl"**
3. Choose **"Import from GitHub"**
4. Enter your repo URL: `https://github.com/YOUR_USERNAME/ai-browser-secure`
5. Name it: `browser-use-backend`
6. Click **"Import from GitHub"**

**OR** if you have the code locally:

1. Click **"+ Create Repl"**
2. Choose **"Python"** template
3. Name it: `browser-use-backend`
4. Upload the entire repository via drag-and-drop

#### 2. Configuration Files

The following files are already configured in your repo:

- ✅ `.replit` - Replit configuration
- ✅ `replit.nix` - System dependencies (Python, Chromium)
- ✅ `main.py` - Entry point for the server
- ✅ `browser_use/demo_server/replit_config.py` - Optimized browser settings

#### 3. Set Environment Variables (Secrets)

In your backend Repl:

1. Click **🔒 "Secrets"** (lock icon in left sidebar)
2. Add these secrets:

```bash
# Required: Choose one LLM provider
OPENAI_API_KEY=your-openai-key-here
# OR
ANTHROPIC_API_KEY=your-anthropic-key-here

# Optional: Will be updated after frontend deployment
FRONTEND_URL=https://browser-use-frontend.YOUR_USERNAME.repl.co

# Optional: For remote browser service (if local Chromium fails)
# Get free 6 hours/month at https://www.browserless.io/
BROWSERLESS_TOKEN=your-browserless-token
```

#### 4. Install Dependencies

Click the **Shell** tab and run:

```bash
# Install Python dependencies
pip install -e .

# Install Chromium (may take 2-3 minutes)
playwright install chromium --with-deps

# Note: On free tier, this might show warnings - that's okay!
```

⚠️ **Free Tier Note**: Chromium may use significant memory (~200MB). The optimized config will help, but if you encounter issues, consider using Browserless.io (free tier available).

#### 5. Run the Backend

Click the **"Run"** button at the top.

You should see:

```
🚀 Starting browser-use demo server on port 8000
📍 Environment: Replit
🌐 Access at: https://browser-use-backend.YOUR_USERNAME.repl.co
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 6. Test the Backend

Click **"Open in a new tab"** or visit:
```
https://browser-use-backend.YOUR_USERNAME.repl.co/health
```

You should see:
```json
{"status": "healthy"}
```

✅ **Backend is live!** Copy the URL for the frontend setup.

---

### 🎨 Frontend Deployment

#### 1. Create Frontend Repl

1. Click **"+ Create Repl"**
2. Choose **"Import from GitHub"**
3. Enter your repo URL: `https://github.com/YOUR_USERNAME/ai-browser-secure`
4. Name it: `browser-use-frontend`
5. **Important**: Set **Root directory** to `demo-ui`
6. Click **"Import from GitHub"**

**OR** upload manually:

1. Click **"+ Create Repl"**
2. Choose **"Node.js"** template
3. Name it: `browser-use-frontend`
4. Upload the `demo-ui/` folder contents

#### 2. Configuration Files

The following files are already configured in `demo-ui/`:

- ✅ `.replit` - Replit configuration
- ✅ `replit.nix` - Node.js dependencies
- ✅ `.env.production` - Environment variables template
- ✅ `.env.example` - Example configuration

#### 3. Set Backend URL

**Option A: Edit `.env.production` file**

Open `.env.production` and update:

```bash
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co
```

**Option B: Use Replit Secrets**

1. Click **🔒 "Secrets"**
2. Add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://browser-use-backend.YOUR_USERNAME.repl.co`

#### 4. Install and Build

Click the **Shell** tab and run:

```bash
# Install dependencies
npm install

# Build for production
npm run build

# This may take 1-2 minutes
```

#### 5. Run the Frontend

Click the **"Run"** button at the top.

You should see:

```
> browser-use-demo-ui@0.1.0 start
> next start -p 3000

  ▲ Next.js 15.1.4
  - Local:        http://localhost:3000
  - Ready in 1.2s
```

#### 6. Test the Frontend

Click **"Open in a new tab"** or visit:
```
https://browser-use-frontend.YOUR_USERNAME.repl.co
```

You should see the browser-use demo UI!

✅ **Frontend is live!**

---

### 🔗 Connect Frontend to Backend

#### Update Backend CORS

Go back to your **backend Repl** and update the `FRONTEND_URL` secret:

1. Click **🔒 "Secrets"**
2. Update `FRONTEND_URL` with your frontend URL:
   ```
   https://browser-use-frontend.YOUR_USERNAME.repl.co
   ```
3. Click **"Restart"** to apply changes

The CORS is already configured to accept `*.repl.co` domains, so it should work immediately!

---

## 🧪 Testing Your Deployment

### 1. Test Backend Health

```bash
curl https://browser-use-backend.YOUR_USERNAME.repl.co/health
```

Expected: `{"status": "healthy"}`

### 2. Test Frontend

Visit: `https://browser-use-frontend.YOUR_USERNAME.repl.co`

### 3. Test Live Demo

1. Open the frontend URL
2. Click **"Run Demo"**
3. Enter a task like: "Go to google.com and search for 'browser automation'"
4. Watch the logs stream in real-time!

---

## ⚡ Optimization Tips

### 1. Keep Repls Awake (Free Tier Sleeps After 1 Hour)

**Option A: Use UptimeRobot (Recommended)**

1. Go to https://uptimerobot.com (free account)
2. Add two monitors:
   - **Backend**: `https://browser-use-backend.YOUR_USERNAME.repl.co/health`
   - **Frontend**: `https://browser-use-frontend.YOUR_USERNAME.repl.co`
3. Set interval to **5 minutes**
4. Your Repls will stay awake 24/7!

**Option B: Upgrade to Replit Core ($7/month)**

- Always-on Repls (no sleep)
- 2GB RAM (better for Chromium)
- Private Repls

### 2. Reduce Memory Usage

If Chromium crashes or fails to start, try these:

**Use Remote Browser (Browserless.io)**

1. Sign up at https://www.browserless.io/ (free 6 hours/month)
2. Get your token
3. Add to backend Secrets:
   ```
   BROWSERLESS_TOKEN=your-token-here
   ```
4. The system will automatically use remote browser when available!

**Disable Extensions**

Already configured in `replit_config.py`:
```python
'--disable-extensions',
'--disable-dev-shm-usage',
'--no-sandbox',
```

### 3. Improve Cold Start Time

Add a health check endpoint warm-up:

```bash
# In frontend, add this to your API client
// Warm up backend on page load
fetch(`${API_URL}/health`).catch(() => {});
```

---

## 📊 Architecture

```
┌──────────────────────────────────────────────┐
│              Replit Platform                 │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Backend Repl (Python)                 │ │
│  │  browser-use-backend.USERNAME.repl.co  │ │
│  │                                        │ │
│  │  - FastAPI server                      │ │
│  │  - Chromium browser (optimized)        │ │
│  │  - WebSocket endpoints                 │ │
│  │  - /api/live/*                         │ │
│  └────────────────────────────────────────┘ │
│           ▲                                  │
│           │ WebSocket + REST API             │
│           │                                  │
│  ┌────────┴───────────────────────────────┐ │
│  │  Frontend Repl (Node.js/Next.js)       │ │
│  │  browser-use-frontend.USERNAME.repl.co │ │
│  │                                        │ │
│  │  - Next.js app                         │ │
│  │  - Real-time UI                        │ │
│  │  - Log streaming                       │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### "Chromium not found"

```bash
# In backend Repl Shell:
playwright install chromium --with-deps
```

### "Module not found"

```bash
# Backend:
pip install -e .

# Frontend:
cd demo-ui && npm install
```

### "Connection refused" / CORS Error

1. Check backend Repl is running (green indicator)
2. Verify frontend `.env.production` has correct backend URL
3. Check backend logs for errors
4. Ensure CORS is configured (already done in `main.py`)

### "Out of memory" / Chromium crashes

**Option 1: Use Browserless.io**
```bash
# Add to backend Secrets:
BROWSERLESS_TOKEN=your-token
```

**Option 2: Upgrade to Replit Core**
- $7/month for 2GB RAM
- Much more stable for browser automation

### Repl sleeps after 1 hour

- Use UptimeRobot (free) to ping every 5 minutes
- Or upgrade to Replit Core for "Always On"

### Build fails on frontend

```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

---

## 💰 Cost Breakdown

**Free Tier:**
- ✅ Backend Repl: Free (sleeps after 1 hour)
- ✅ Frontend Repl: Free (sleeps after 1 hour)
- ✅ UptimeRobot: Free (keeps awake)
- ⚠️ Limited RAM (512MB) - may struggle with Chromium

**Replit Core ($7/month):**
- ✅ 2GB RAM (smooth Chromium)
- ✅ Always On (no sleep)
- ✅ Private Repls
- ✅ Better CPU

**Browserless.io:**
- ✅ Free: 6 hours/month
- 💰 Paid: $50/month for 200 hours

---

## 📝 Quick Checklist

### Backend:
- [ ] Created Python Repl: `browser-use-backend`
- [ ] Added Secrets (API keys)
- [ ] Ran `pip install -e .`
- [ ] Ran `playwright install chromium`
- [ ] Clicked "Run" - server started
- [ ] Tested `/health` endpoint
- [ ] Copied backend URL

### Frontend:
- [ ] Created Node.js Repl: `browser-use-frontend`
- [ ] Set root directory to `demo-ui` (if importing from GitHub)
- [ ] Updated `.env.production` with backend URL
- [ ] Ran `npm install`
- [ ] Ran `npm run build`
- [ ] Clicked "Run" - frontend started
- [ ] Tested opening the UI

### Connection:
- [ ] Updated backend `FRONTEND_URL` secret
- [ ] Tested live demo from UI
- [ ] Set up UptimeRobot (optional but recommended)

---

## 🎉 Success!

Your browser-use demo is now live on Replit!

**Share your deployment:**
- Backend: `https://browser-use-backend.YOUR_USERNAME.repl.co`
- Frontend: `https://browser-use-frontend.YOUR_USERNAME.repl.co`

---

## 🆘 Need Help?

- Check [TESTING.md](TESTING.md) for local development
- Check [README.md](README.md) for project overview
- Visit https://replit.com/support for Replit issues
- Open an issue on GitHub for browser-use specific problems

---

## 🔄 Updating Your Deployment

When you push changes to GitHub:

1. Go to your Repl
2. Click **"Version control"** (git icon)
3. Click **"Pull"** to fetch latest changes
4. Click **"Restart"** to apply changes

Or use Shell:
```bash
git pull origin main
# For backend: nothing else needed (auto-restarts)
# For frontend: npm run build && npm start
```

---

**Happy deploying! 🚀**
