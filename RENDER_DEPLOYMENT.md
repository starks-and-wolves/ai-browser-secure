# 🚀 Render Deployment Guide

Complete guide to deploy browser-use demo on Render (both backend and frontend).

## 📋 Prerequisites

- GitHub account with your code pushed
- Render account (sign up at https://render.com)
- OpenAI or Anthropic API key

---

## ⚡ Quick Deploy (5 Minutes)

### Option A: Automatic Deploy with Blueprint

**This is the easiest way!**

1. Push your code to GitHub (if not already)
2. Go to https://dashboard.render.com
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will detect `render.yaml` and set up both services automatically
6. Click **"Apply"**
7. Add your API keys when prompted:
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
8. Wait for deployment (~5-10 minutes)

**Done!** Both services will be live.

---

## 📝 Option B: Manual Deploy (Step by Step)

If automatic deployment doesn't work, deploy manually:

### Step 1: Deploy Backend

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. **Configure:**
   - **Name:** `browser-use-backend`
   - **Region:** Oregon (US West) - recommended
   - **Branch:** `main`
   - **Root Directory:** leave blank
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -e . && playwright install chromium --with-deps
     ```
   - **Start Command:**
     ```bash
     python main.py
     ```
   - **Plan:** Free

5. **Environment Variables:** (Click "Advanced")
   - `PYTHON_VERSION` = `3.11.0`
   - `OPENAI_API_KEY` = `your-openai-key` (or use Anthropic)
   - `ANTHROPIC_API_KEY` = `your-anthropic-key` (optional)

6. Click **"Create Web Service"**

7. **Wait for deployment** (~5-10 minutes for first deploy)
   - Installing Chromium takes a few minutes
   - You'll see build logs in real-time

8. **Note your backend URL:**
   ```
   https://browser-use-backend.onrender.com
   ```

9. **Test backend:**
   Visit: `https://browser-use-backend.onrender.com/health`
   Should return: `{"status":"healthy"}`

---

### Step 2: Deploy Frontend

1. Click **"New +"** → **"Web Service"**
2. Connect same GitHub repository
3. **Configure:**
   - **Name:** `browser-use-frontend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** `demo-ui`
   - **Runtime:** Node
   - **Build Command:**
     ```bash
     npm install && npm run build
     ```
   - **Start Command:**
     ```bash
     npm start
     ```
   - **Plan:** Free

4. **Environment Variables:**
   - `NODE_VERSION` = `20.11.0`
   - `NODE_ENV` = `production`
   - `NEXT_PUBLIC_API_URL` = `https://browser-use-backend.onrender.com`
     (Use your actual backend URL from Step 1)

5. Click **"Create Web Service"**

6. **Wait for deployment** (~2-5 minutes)

7. **Note your frontend URL:**
   ```
   https://browser-use-frontend.onrender.com
   ```

---

### Step 3: Connect Frontend to Backend

1. Go to **backend service** in Render dashboard
2. Click **"Environment"** tab
3. Add/Update:
   - `FRONTEND_URL` = `https://browser-use-frontend.onrender.com`
     (Your actual frontend URL)
4. Click **"Save Changes"**
5. Backend will automatically redeploy

---

### Step 4: Test Everything

1. **Test Backend:**
   ```bash
   curl https://browser-use-backend.onrender.com/health
   ```
   Should return: `{"status":"healthy"}`

2. **Test Frontend:**
   Visit: `https://browser-use-frontend.onrender.com`
   Should load the home page

3. **Test Live Demo:**
   - Go to frontend → "Live Demo"
   - Click "⚙️ Backend Settings"
   - Should show: `https://browser-use-backend.onrender.com`
   - Click "🔍 Test Connection" → Should be ✅
   - Enter API key → Start demo → Should work!

---

## 🎯 Your Deployment URLs

After deployment, you'll have:

- **Frontend:** `https://browser-use-frontend.onrender.com`
- **Backend:** `https://browser-use-backend.onrender.com`

Share the frontend URL with anyone!

---

## ⚙️ Configuration Details

### Backend Configuration

**Free Tier Includes:**
- 512 MB RAM
- Shared CPU
- 100 GB bandwidth/month
- Sleeps after 15 min of inactivity

**Build Time:** ~5-10 minutes (first deploy)
- Installing Chromium takes most of the time
- Subsequent deploys are faster (~2-3 min)

**Wake Time:** 60-90 seconds when sleeping
- First request after sleep will be slow
- Use UptimeRobot to keep it awake (see below)

### Frontend Configuration

**Free Tier Includes:**
- 512 MB RAM
- Shared CPU
- 100 GB bandwidth/month
- Also sleeps after 15 min

**Build Time:** ~2-5 minutes

---

## 🔄 Keeping Services Awake (Optional)

Free tier services sleep after 15 minutes of inactivity.

### Option 1: UptimeRobot (Recommended)

**100% Free, keeps your services awake 24/7**

1. Go to https://uptimerobot.com
2. Sign up (free)
3. Add monitor:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Browser-Use Backend
   - **URL:** `https://browser-use-backend.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
4. Add another monitor for frontend:
   - **URL:** `https://browser-use-frontend.onrender.com`
5. **Done!** Services will never sleep.

### Option 2: Cron Job

**Set up a cron job to ping your services:**

```bash
# Add to crontab (crontab -e)
*/5 * * * * curl https://browser-use-backend.onrender.com/health
*/5 * * * * curl https://browser-use-frontend.onrender.com
```

### Option 3: Render Cron Job (Paid Feature)

Render offers cron jobs, but it's a paid feature.

---

## 🔧 Updating Your Deployment

### Automatic Updates (Recommended)

By default, Render auto-deploys on every push to `main` branch.

**To update:**
```bash
git add .
git commit -m "Update something"
git push origin main
```

Render will automatically rebuild and deploy.

### Manual Updates

1. Go to Render dashboard
2. Select your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🐛 Troubleshooting

### Backend Build Fails

**Error:** `playwright install` fails

**Fix:** Make sure build command includes `--with-deps`:
```bash
pip install -e . && playwright install chromium --with-deps
```

**Error:** "No module named 'browser_use'"

**Fix:** Ensure `pip install -e .` is in build command

### Frontend Build Fails

**Error:** "Module not found"

**Fix:** Make sure Root Directory is set to `demo-ui`

### Services Can't Connect

**Error:** Frontend can't reach backend

**Fix:**
1. Check backend is deployed and running
2. Visit backend `/health` endpoint - should return JSON
3. Verify `NEXT_PUBLIC_API_URL` in frontend environment variables
4. Check CORS - already configured in `main.py`

### "Failed to fetch" Error

**Fix:**
1. Check backend URL in frontend environment variables
2. Test backend: `curl https://backend.onrender.com/health`
3. Check browser console for CORS errors
4. Verify both services are not sleeping

### Backend Sleeps Too Often

**Fix:** Use UptimeRobot (free) to ping every 5 minutes

---

## 💰 Cost Breakdown

**Free Tier (Both Services):**
- Backend: Free (with sleep)
- Frontend: Free (with sleep)
- **Total:** $0/month

**With UptimeRobot:**
- Backend: Free
- Frontend: Free
- UptimeRobot: Free
- **Total:** $0/month (services stay awake!)

**Paid Tier (Optional):**
- Backend: $7/month (no sleep, better CPU/RAM)
- Frontend: $7/month (no sleep)
- **Total:** $14/month

---

## 📊 Performance

**Free Tier:**
- Cold start (sleeping): 60-90 seconds
- Warm start: <1 second
- Request latency: ~100-300ms
- Good for demos and low traffic

**With UptimeRobot:**
- No cold starts (always warm)
- Request latency: ~100-200ms
- Perfect for demos and medium traffic

---

## 🔐 Security Notes

### Environment Variables

**Never commit secrets to Git!**

Store all API keys in Render's environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

These are encrypted and secure.

### CORS

Backend CORS is already configured in `browser_use/demo_server/main.py`:
```python
allow_origin_regex=r"https://.*\.onrender\.com|..."
```

This allows all `*.onrender.com` domains.

---

## ✅ Deployment Checklist

### Before Deploying:
- [ ] Code pushed to GitHub
- [ ] Have API keys ready
- [ ] Render account created

### Backend Deployment:
- [ ] Service created
- [ ] Build command set correctly
- [ ] Start command: `python main.py`
- [ ] API keys added to environment
- [ ] Service deployed successfully
- [ ] Health check passes: `/health` returns JSON

### Frontend Deployment:
- [ ] Service created
- [ ] Root directory set to `demo-ui`
- [ ] Build command set correctly
- [ ] `NEXT_PUBLIC_API_URL` set to backend URL
- [ ] Service deployed successfully
- [ ] Can access homepage

### Connection:
- [ ] Backend `FRONTEND_URL` set
- [ ] Frontend can connect to backend
- [ ] Test connection shows ✅
- [ ] Live demo works

### Keep Awake (Optional):
- [ ] UptimeRobot monitor set up for backend
- [ ] UptimeRobot monitor set up for frontend

---

## 🆘 Getting Help

### Render Support

- **Docs:** https://render.com/docs
- **Community:** https://community.render.com
- **Status:** https://status.render.com

### Project Support

- **Issues:** Open issue on GitHub
- **Troubleshooting:** See the troubleshooting section above

---

## 🎉 Success!

Once deployed, your demo will be live at:

**Frontend:** `https://browser-use-frontend.onrender.com`

Share this URL with anyone to show off your demo!

---

## 📝 Quick Reference

| Task | Command/Action |
|------|----------------|
| Deploy backend | New Web Service → Configure → Deploy |
| Deploy frontend | New Web Service → Set root to `demo-ui` → Deploy |
| Update deployment | `git push origin main` (auto-deploys) |
| View logs | Dashboard → Service → Logs tab |
| Add env var | Dashboard → Service → Environment → Add |
| Test backend | `curl https://backend.onrender.com/health` |
| Keep awake | Set up UptimeRobot monitors |

---

## 🚀 Next Steps

After deployment:

1. **Test thoroughly** - Try all demo modes
2. **Set up UptimeRobot** - Keep services awake
3. **Monitor** - Check Render dashboard for errors
4. **Share** - Give frontend URL to users
5. **Iterate** - Push updates, Render auto-deploys

---

**Enjoy your stable, free deployment on Render!** 🎉

---

**Last Updated:** 2026-01-22
