# 🚀 Render Quick Start (5 Minutes)

Get your browser-use demo running on Render in 5 minutes.

## Step 1: Push to GitHub (If Not Already)

```bash
git add .
git commit -m "Add Render deployment config"
git push origin main
```

---

## Step 2: Deploy to Render

### Option A: Automatic (Easiest) ⭐

1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repository: `ai-browser-secure`
4. Render detects `render.yaml` automatically
5. Click **"Apply"**
6. When prompted, add:
   - `OPENAI_API_KEY` = `your-key-here`
   - `ANTHROPIC_API_KEY` = `your-key-here` (or just use OpenAI)
7. Wait 5-10 minutes for deployment

**Done!** Both services are now live.

---

### Option B: Manual (If Blueprint Fails)

#### Backend:

1. https://dashboard.render.com → **"New +"** → **"Web Service"**
2. Connect your repo
3. **Settings:**
   - Name: `browser-use-backend`
   - Root Directory: *leave blank*
   - Build Command: `pip install -e . && playwright install chromium --with-deps`
   - Start Command: `python main.py`
   - Plan: Free
4. **Environment Variables:**
   - `OPENAI_API_KEY` = your key
5. Click **"Create Web Service"**
6. Copy the URL: `https://browser-use-backend.onrender.com`

#### Frontend:

1. **"New +"** → **"Web Service"**
2. Same repo
3. **Settings:**
   - Name: `browser-use-frontend`
   - Root Directory: `demo-ui`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
   - Plan: Free
4. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL` = `https://browser-use-backend.onrender.com`
   - `NODE_ENV` = `production`
5. Click **"Create Web Service"**

#### Connect Them:

1. Go to backend service → Environment
2. Add: `FRONTEND_URL` = `https://browser-use-frontend.onrender.com`
3. Save (auto-redeploys)

---

## Step 3: Test

1. **Backend:** Visit `https://browser-use-backend.onrender.com/health`
   - Should return: `{"status":"healthy"}`

2. **Frontend:** Visit `https://browser-use-frontend.onrender.com`
   - Should load the homepage

3. **Demo:** Click "Live Demo" → Enter API key → Start!

---

## Step 4: Keep Awake (Optional)

**Free services sleep after 15 min. Use UptimeRobot to keep them awake:**

1. Go to https://uptimerobot.com (free account)
2. Add monitor:
   - URL: `https://browser-use-backend.onrender.com/health`
   - Interval: 5 minutes
3. Add another for frontend:
   - URL: `https://browser-use-frontend.onrender.com`

**Done!** Services never sleep.

---

## 📋 Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Backend deployed (5-10 min)
- [ ] Frontend deployed (2-5 min)
- [ ] Backend `/health` returns JSON
- [ ] Frontend loads
- [ ] Demo works
- [ ] UptimeRobot set up (optional)

---

## 🎯 Your URLs

After deployment:

- **Frontend:** `https://browser-use-frontend.onrender.com`
- **Backend:** `https://browser-use-backend.onrender.com`

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check build logs in Render dashboard |
| Backend 404 | Wait 5-10 min for first deploy (Chromium installation) |
| Frontend can't connect | Check `NEXT_PUBLIC_API_URL` is correct |
| Services sleep | Set up UptimeRobot |

Full guide: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

## 🎉 That's It!

Your demo is now live and stable on Render. No more Replit issues!

Share your frontend URL with anyone: `https://browser-use-frontend.onrender.com`

---

**Total Time:** 5 minutes (automatic) or 10 minutes (manual)
**Cost:** $0/month
**Stability:** ⭐⭐⭐⭐⭐ (Much better than Replit!)

---

**Last Updated:** 2026-01-22
