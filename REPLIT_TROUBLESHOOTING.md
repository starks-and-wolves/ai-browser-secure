# Replit Deployment Troubleshooting

Common issues and solutions when deploying browser-use demo on Replit.

---

## ❌ Error: "Failed to fetch" when starting demo

**Symptoms:**
```
[16:12:35] Failed to start: TypeError: Failed to fetch
```

### Root Causes & Solutions:

### 1. **CORS Issue (Most Common)**

**Problem:** Backend is not allowing requests from frontend domain.

**Solution:**

The CORS configuration has been updated to automatically allow Replit domains, but verify:

```python
# In browser_use/demo_server/main.py
# This should already be configured:
allow_origin_regex=r"https://.*\.repl\.co|..."
```

**If still having issues:**
1. Check backend logs for CORS errors
2. Verify both Repls are running
3. Restart both Repls

### 2. **Backend Not Running**

**Problem:** Backend Repl is stopped or sleeping.

**Solution:**
1. Go to backend Repl
2. Click "Run" button
3. Wait for server to start (should see "Uvicorn running...")
4. Try frontend again

### 3. **Wrong Backend URL**

**Problem:** Frontend is trying to connect to wrong URL.

**Check:**
```bash
# In frontend Repl shell:
cat .env.production

# Should show:
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co
```

**Fix:**
1. Update `.env.production` with correct backend URL
2. Or add to Replit Secrets (🔒 icon):
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://browser-use-backend.YOUR_USERNAME.repl.co`
3. Restart frontend

### 4. **Next.js Dev Mode CORS on Replit**

**Problem:** Getting this error:
```
⚠ Blocked cross-origin request from *.replit.dev to /_next/* resource
```

**Solution A: Use Production Mode (Recommended)**

The `.replit` file is already configured to use production mode:
```toml
[env]
NODE_ENV = "production"
```

Make sure you've run:
```bash
npm run build
npm start
```

**Solution B: Allow Dev Origins**

If you need dev mode, `next.config.ts` is already configured:
```typescript
experimental: {
  allowedDevOrigins: [
    '*.replit.dev',
    '*.repl.co',
  ],
}
```

Restart frontend for changes to take effect.

### 5. **Mixed Content (HTTPS/HTTP)**

**Problem:** Frontend is HTTPS but backend URL is HTTP.

**Check:**
- Frontend URL: `https://frontend.repl.co` ✅
- Backend URL: `http://backend.repl.co` ❌ (wrong!)

**Fix:**
Update `.env.production` to use HTTPS:
```bash
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co
```

---

## 🔍 Diagnostic Steps

### Step 1: Test Backend Health

In your **browser** or frontend Repl shell:

```bash
# Test backend health endpoint
curl https://browser-use-backend.YOUR_USERNAME.repl.co/health

# Should return:
{"status":"healthy"}
```

If this fails:
- Backend is not running
- Backend URL is wrong
- Backend crashed (check logs)

### Step 2: Check Frontend Environment

In frontend Repl shell:

```bash
# Check environment variable
echo $NEXT_PUBLIC_API_URL

# OR check .env.production
cat .env.production
```

Should show your backend URL.

### Step 3: Check Browser Console

1. Open frontend in browser
2. Press F12 (Developer Tools)
3. Go to "Console" tab
4. Try starting demo
5. Look for errors:

**CORS Error:**
```
Access to fetch at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Network Error:**
```
Failed to fetch
net::ERR_NAME_NOT_RESOLVED
```

### Step 4: Verify Both Repls Are Running

Both Repls should show:
- Green "Running" indicator
- No errors in console
- Backend: "Uvicorn running on..."
- Frontend: "Ready in X.Xs"

---

## 🛠️ Quick Fixes

### Fix 1: Restart Everything

```bash
# Backend Repl:
1. Click "Stop" (if running)
2. Click "Run"
3. Wait for "Uvicorn running..."

# Frontend Repl:
1. Click "Stop" (if running)
2. npm run build
3. Click "Run"
4. Wait for "Ready in..."
```

### Fix 2: Clear Cache & Rebuild

```bash
# In frontend Repl shell:
rm -rf .next node_modules
npm install
npm run build
npm start
```

### Fix 3: Update Backend URL

```bash
# In frontend Repl:
# Edit .env.production
nano .env.production

# Update to:
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co

# Save and restart
```

### Fix 4: Check Backend Logs

```bash
# In backend Repl console, look for:
# ✅ Good:
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete

# ❌ Bad:
ERROR: Failed to start
ModuleNotFoundError: No module named 'browser_use'
# Fix: Run ./replit_setup.sh
```

---

## 🧪 Test Connection Script

Add this button to your frontend for testing:

```typescript
// In app/live/page.tsx
const testBackendConnection = async () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  console.log('Testing connection to:', apiUrl)

  try {
    const response = await fetch(`${apiUrl}/health`)
    const data = await response.json()
    console.log('✅ Backend is reachable:', data)
    alert('Backend is reachable!')
  } catch (error) {
    console.error('❌ Backend not reachable:', error)
    alert('Backend not reachable. Check console.')
  }
}

// Add button:
<button onClick={testBackendConnection}>Test Backend Connection</button>
```

---

## 📊 Common Error Patterns

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `Failed to fetch` | CORS or backend down | Check backend running, verify URL |
| `net::ERR_NAME_NOT_RESOLVED` | Wrong backend URL | Update `.env.production` |
| `Access-Control-Allow-Origin` | CORS misconfigured | Check `main.py` CORS regex |
| `Session timeout` | Backend sleeping | Wait 60-90s or use UptimeRobot |
| `Blocked cross-origin /_next/*` | Dev mode on Replit | Use production mode or update `next.config.ts` |

---

## 🔐 Security Checklist

If everything else works but you still get errors:

1. **Check Secrets are set:**
   - Backend: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - Frontend: `NEXT_PUBLIC_API_URL` (optional, can use `.env.production`)

2. **Verify URLs use HTTPS:**
   - ✅ `https://backend.repl.co`
   - ❌ `http://backend.repl.co` (insecure, may be blocked)

3. **Check browser security:**
   - No ad blockers interfering
   - No privacy extensions blocking WebSockets
   - Cookies enabled

---

## 🆘 Still Not Working?

### Collect Diagnostic Info

1. **Backend URL:**
   ```bash
   # In frontend Repl:
   cat .env.production
   ```

2. **Backend Status:**
   ```bash
   # Visit in browser:
   https://browser-use-backend.YOUR_USERNAME.repl.co/health
   ```

3. **Frontend Console:**
   - Press F12 in browser
   - Copy error messages

4. **Backend Logs:**
   - Check backend Repl console
   - Look for errors

### Share for Help

Include:
- Error message from frontend console
- Backend logs
- Output of health endpoint
- Both Repl URLs

---

## 💡 Pro Tips

1. **Always test backend health first** before debugging frontend
2. **Use browser DevTools Network tab** to see exact requests/responses
3. **Check both backend AND frontend logs** - error might be on either side
4. **Restart both Repls** after configuration changes
5. **Use production mode** for deployments (avoids dev-mode issues)

---

## ✅ Working Configuration Example

**Backend `.replit`:**
```toml
run = ["python", "main.py"]
```

**Backend Secrets:**
```
OPENAI_API_KEY=sk-...
```

**Frontend `.replit`:**
```toml
run = ["npm", "start"]
[env]
NODE_ENV = "production"
```

**Frontend `.env.production`:**
```bash
NEXT_PUBLIC_API_URL=https://browser-use-backend.YOUR_USERNAME.repl.co
```

**Backend CORS (`main.py`):**
```python
allow_origin_regex=r"https://.*\.repl\.co|http://localhost:\d+"
```

---

**If all else fails:** Deploy backend separately on Render (free tier) and just use Replit for frontend.

---

Last updated: 2026-01-22
