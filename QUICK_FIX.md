# 🚀 Quick Fix for "Backend URL: localhost:8000" Error

## What Happened

Your frontend is using `localhost:8000` instead of your actual Replit backend URL.

## ✅ Solution (Choose One)

### Option 1: Use Auto-Detection (EASIEST - Recommended)

The new code has **automatic backend detection**!

**In your frontend Repl shell:**
```bash
# Pull latest changes
git pull origin main

# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build

# Stop and restart (Click "Stop" then "Run" button)
```

**Done!** Auto-detection will find your backend at:
```
https://browser-use-backend.YOUR_USERNAME.repl.co
```

---

### Option 2: Use UI Settings (NO REBUILD NEEDED)

**If you can't/don't want to pull new code:**

1. Go to your frontend URL
2. Navigate to the live demo page
3. Click **"⚙️ Backend Settings"** (collapsible section)
4. Update **Backend API URL** to:
   ```
   https://browser-use-backend.YOUR_USERNAME.repl.co
   ```
5. Click **"🔍 Test Connection"**
6. If ✅, start your demo!

**Note:** This only works for current session. For permanent fix, use Option 1 or 3.

---

### Option 3: Set Environment Variable

**In your frontend Repl shell:**

```bash
# Edit .env.production
nano .env.production
```

**Add/Update this line:**
```bash
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Rebuild:**
```bash
rm -rf .next
npm run build

# Stop and restart (Click "Stop" then "Run" button)
```

---

## 🎯 How to Find Your Backend URL

1. Go to your **backend Repl**
2. Look at the webview or URL bar
3. Copy the URL that looks like:
   ```
   https://browser-use-backend.YOUR_USERNAME.repl.co
   ```
4. Make sure backend is running (green indicator)

---

## ✅ Verify It Worked

Start a demo and check the logs:

**Before (Wrong):**
```
[18:22:57] Backend URL: http://localhost:8000
[18:22:57] Backend health check failed
```

**After (Correct):**
```
[18:22:57] Backend URL: https://browser-use-backend.YOUR_USERNAME.repl.co
[18:22:57] Backend is reachable (123ms)
```

---

## 🆘 Still Not Working?

### Check Backend is Running

Visit in browser:
```
https://browser-use-backend.YOUR_USERNAME.repl.co/health
```

Should return: `{"status":"healthy"}`

If not:
1. Go to backend Repl
2. Click "Run" button
3. Wait for "Uvicorn running..."

### Test Connection

In frontend UI:
1. Click "⚙️ Backend Settings"
2. Click "🔍 Test Connection"
3. Should show: "✅ Backend is reachable!"

### Check Logs

Press F12 in browser, go to Console tab, look for:
```
Backend URL: https://...
```

---

## 📚 More Help

- **[BACKEND_SETUP.md](demo-ui/BACKEND_SETUP.md)** - Complete backend URL setup guide
- **[FIXES_APPLIED.md](FIXES_APPLIED.md)** - All fixes and changes
- **[REPLIT_TROUBLESHOOTING.md](REPLIT_TROUBLESHOOTING.md)** - Detailed troubleshooting

---

**TL;DR:** Pull latest code → Rebuild → Backend URL auto-detected → Works! 🎉
