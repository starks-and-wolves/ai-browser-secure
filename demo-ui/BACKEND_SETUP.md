# Backend URL Setup Guide

The frontend needs to know where your backend is running. Here's how to configure it:

## ⚙️ Configuration Options

### Option 1: Environment Variable (Recommended)

**During build:**
```bash
# Create or edit .env.production
nano .env.production

# Add your backend URL:
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# Save and rebuild:
rm -rf .next
npm run build
npm start
```

### Option 2: UI Settings (Runtime)

In the live demo page:

1. Click **"⚙️ Backend Settings"**
2. Update the **Backend API URL** field
3. Click **"🔍 Test Connection"**
4. If successful, start your demo!

**Note:** This only persists for the current session.

---

## 🔍 Finding Your Backend URL

### By Platform:

- **Render**: `https://your-backend.onrender.com`
- **Vercel**: `https://your-backend.vercel.app`
- **Fly.io**: `https://your-backend.fly.dev`
- **Local**: `http://localhost:8000`

---

## ✅ Verify Configuration

### Method 1: Check Logs

When you start a demo, you'll see:
```
[18:22:57] Checking backend connection...
[18:22:57] Backend URL: https://your-backend.onrender.com
[18:22:57] Backend is reachable (123ms)
```

If it says `http://localhost:8000`, your configuration isn't working.

### Method 2: Test Connection

In the UI:
1. Click **"⚙️ Backend Settings"**
2. Click **"🔍 Test Connection"**
3. Should show: `✅ Backend is reachable!`

### Method 3: Browser DevTools

1. Press F12
2. Go to Console tab
3. Should see: `Backend URL: https://...`

---

## 🐛 Troubleshooting

### "Backend URL: http://localhost:8000"

**Problem:** Environment variable not set or build didn't pick it up.

**Fix:**
```bash
# Set the variable
nano .env.production
# Add: NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# Clear and rebuild
rm -rf .next node_modules
npm install
npm run build
npm start
```

### "Backend health check failed"

**Problem:** Backend URL is wrong or backend is not running.

**Fix:**
1. Check backend is running
2. Visit backend URL in browser: `https://your-backend.onrender.com/health`
3. Should return: `{"status":"healthy"}`
4. If not working, check your deployment logs

### "Failed to fetch" / CORS Error

**Problem:** Backend CORS not configured or wrong URL.

**Fix:**
1. Backend CORS is already configured for `*.onrender.com` and `*.vercel.app`
2. Make sure both services are running
3. Restart both services
4. Check browser console (F12) for detailed error

---

## 📋 Quick Checklist

- [ ] Backend is running
- [ ] Backend URL set in `.env.production`
- [ ] Frontend rebuilt after setting URL (`npm run build`)
- [ ] Frontend restarted
- [ ] Test connection shows ✅
- [ ] Demo starts successfully

---

## 💡 Pro Tips

1. **Test connection first** before running a full demo
2. **Check the logs** - they tell you exactly what backend URL is being used
3. **Rebuild is required** - Next.js bakes env vars into the build

---

## 🆘 Still Having Issues?

See:
- [RENDER_DEPLOYMENT.md](../RENDER_DEPLOYMENT.md) - Full deployment guide for Render

---

**Last Updated:** 2026-01-30
