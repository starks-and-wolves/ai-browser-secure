# Backend URL Setup Guide

The frontend needs to know where your backend is running. Here's how to configure it:

## 🤖 Auto-Detection (Replit)

On Replit, the frontend will **automatically detect** your backend URL if it follows the naming pattern:

- Frontend Repl: `browser-use-frontend.USERNAME.repl.co`
- Backend Repl: `browser-use-backend.USERNAME.repl.co`

**No configuration needed!** The auto-detection will find your backend.

---

## ⚙️ Manual Configuration

If auto-detection doesn't work or you're using a custom setup:

### Option 1: Environment Variable (Recommended)

**During build:**
```bash
# Create or edit .env.production
nano .env.production

# Add your backend URL:
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co

# Save and rebuild:
rm -rf .next
npm run build
npm start
```

### Option 2: Replit Secrets

In your Replit frontend:

1. Click **🔒 "Secrets"** (lock icon)
2. Add secret:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://browser-use-backend.YOUR_USERNAME.repl.co`
3. Rebuild:
   ```bash
   rm -rf .next
   npm run build
   npm start
   ```

### Option 3: UI Settings (Runtime)

In the live demo page:

1. Click **"⚙️ Backend Settings"**
2. Update the **Backend API URL** field
3. Click **"🔍 Test Connection"**
4. If successful, start your demo!

**Note:** This only persists for the current session.

---

## 🔍 Finding Your Backend URL

### On Replit:

1. Go to your backend Repl
2. Look at the URL bar or the webview panel
3. Copy the URL that looks like:
   ```
   https://browser-use-backend.YOUR_USERNAME.repl.co
   ```

### On Other Platforms:

- **Render**: `https://browser-use-backend.onrender.com`
- **Fly.io**: `https://browser-use-backend.fly.dev`
- **Vercel**: `https://browser-use-backend.vercel.app`
- **Local**: `http://localhost:8000`

---

## ✅ Verify Configuration

### Method 1: Check Logs

When you start a demo, you'll see:
```
[18:22:57] Checking backend connection...
[18:22:57] Backend URL: https://browser-use-backend.YOUR_USERNAME.repl.co
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
# Add: NEXT_PUBLIC_API_URL=https://backend.repl.co

# Clear and rebuild
rm -rf .next node_modules
npm install
npm run build
npm start
```

### "Backend health check failed"

**Problem:** Backend URL is wrong or backend is not running.

**Fix:**
1. Check backend is running (should show green indicator)
2. Visit backend URL in browser: `https://backend.repl.co/health`
3. Should return: `{"status":"healthy"}`
4. If not working, go to backend Repl and click "Run"

### "Failed to fetch" / CORS Error

**Problem:** Backend CORS not configured or wrong URL.

**Fix:**
1. Backend CORS is already configured for `*.repl.co`
2. Make sure both Repls are running
3. Restart both Repls
4. Check browser console (F12) for detailed error

---

## 📋 Quick Checklist

- [ ] Backend Repl is running
- [ ] Backend URL set in `.env.production` OR Replit Secrets
- [ ] Frontend rebuilt after setting URL (`npm run build`)
- [ ] Frontend restarted
- [ ] Test connection shows ✅
- [ ] Demo starts successfully

---

## 💡 Pro Tips

1. **Use Replit Secrets** instead of `.env.production` for easier updates
2. **Auto-detection works** if you name your Repls correctly
3. **Test connection first** before running a full demo
4. **Check the logs** - they tell you exactly what backend URL is being used
5. **Rebuild is required** - Next.js bakes env vars into the build

---

## 🆘 Still Having Issues?

See:
- [REPLIT_TROUBLESHOOTING.md](../REPLIT_TROUBLESHOOTING.md) - Detailed troubleshooting
- [FIXES_APPLIED.md](../FIXES_APPLIED.md) - Recent fixes for common issues
- [REPLIT_DEPLOYMENT.md](../REPLIT_DEPLOYMENT.md) - Full deployment guide

---

**Last Updated:** 2026-01-22
