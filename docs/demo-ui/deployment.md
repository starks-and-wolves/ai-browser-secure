# Demo UI Deployment Guide

This guide covers deploying the browser-use demo UI to Vercel (frontend) and optionally setting up a backend for live execution (Phase 3).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
3. [Environment Variables](#environment-variables)
4. [Custom Domain Setup](#custom-domain-setup)
5. [Backend Deployment (Optional)](#backend-deployment-optional)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Analytics](#monitoring--analytics)

---

## Quick Start

**Prerequisites:**
- Node.js 18+ installed
- Git repository hosted on GitHub
- Vercel account (free tier available)

**Deployment Steps:**
1. Push your code to GitHub
2. Connect GitHub repo to Vercel
3. Configure build settings (auto-detected)
4. Deploy!

**Estimated Time:** 5-10 minutes for first deployment

---

## Frontend Deployment (Vercel)

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Create Vercel Account**
   - Visit [vercel.com](https://vercel.com)
   - Sign up with GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select your GitHub repository (e.g., `ai-browser-secure`)
   - Vercel will auto-detect Next.js configuration

3. **Configure Build Settings**
   ```
   Framework Preset: Next.js
   Build Command: npm run build (auto-detected)
   Output Directory: .next (auto-detected)
   Install Command: npm install (auto-detected)
   Root Directory: demo-ui
   ```

   **IMPORTANT**: Set **Root Directory** to `demo-ui` since the Next.js app is in a subdirectory.

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to demo-ui directory
cd demo-ui

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# Deploy to production
vercel --prod
```

### Automatic Deployments

Vercel automatically deploys:
- **Production**: Every push to `main` branch → `your-project.vercel.app`
- **Preview**: Every pull request → unique preview URL
- **Branch**: Every push to other branches → branch-specific URL

**No manual action needed after initial setup!**

---

## Environment Variables

### Frontend Environment Variables

Create `.env.local` in `demo-ui/` directory for local development:

```bash
# Optional: Backend API URL (only needed if using Phase 3 live execution)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics (PostHog, Google Analytics, etc.)
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

**Setting Environment Variables in Vercel:**

1. Go to Project Settings → Environment Variables
2. Add variables:
   - `NEXT_PUBLIC_API_URL` (Production): `https://your-backend.onrender.com`
   - `NEXT_PUBLIC_API_URL` (Preview): `https://staging-backend.onrender.com`
3. Select environment scope (Production, Preview, Development)
4. Save and redeploy

**Important Notes:**
- `NEXT_PUBLIC_*` variables are exposed to the browser
- Never store secrets in `NEXT_PUBLIC_*` variables
- Variables require rebuild/redeploy to take effect

---

## Custom Domain Setup

### Add Custom Domain to Vercel

1. **Purchase Domain** (optional)
   - Use Namecheap, Google Domains, Cloudflare, etc.

2. **Add Domain in Vercel**
   - Project Settings → Domains
   - Enter domain (e.g., `demo.browser-use.com`)
   - Click "Add"

3. **Configure DNS**

   **Option A: Vercel Nameservers (Recommended)**
   - Copy Vercel nameservers from dashboard
   - Update your domain registrar's nameservers
   - Wait 24-48 hours for propagation

   **Option B: CNAME Record**
   - Add CNAME record in your DNS provider:
     ```
     Type: CNAME
     Name: demo (or @ for root domain)
     Value: cname.vercel-dns.com
     ```
   - Wait 1-2 hours for propagation

4. **SSL Certificate**
   - Vercel automatically provisions SSL certificate
   - HTTPS enabled by default (no configuration needed)

### Verify Domain Setup

```bash
# Check DNS propagation
dig demo.browser-use.com

# Should return Vercel's IP address (76.76.21.21)
```

---

## Backend Deployment (Optional)

**Note:** Only needed if implementing Phase 3 (live execution). Pre-recorded showcase (Phases 1-2) works without backend.

### Deploy to Render.com

1. **Create Account**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - New → Web Service
   - Connect GitHub repository
   - Configure:
     ```
     Name: browser-use-demo-backend
     Root Directory: browser_use/demo_server
     Runtime: Python 3.11
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Environment Variables**
   ```bash
   CORS_ORIGINS=https://your-frontend.vercel.app
   OPENAI_API_KEY=sk-... (if using OpenAI)
   ANTHROPIC_API_KEY=sk-... (if using Anthropic)
   ```

4. **Enable WebSocket Support**
   - Settings → Advanced → Enable WebSocket

5. **Deploy**
   - Click "Create Web Service"
   - Backend URL: `https://browser-use-demo-backend.onrender.com`

### Deploy to Railway (Alternative)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd browser_use/demo_server
railway init

# Deploy
railway up

# Add environment variables
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app
```

**Monthly Cost Estimate:**
- Render: $7/month (Starter plan)
- Railway: $5-10/month (usage-based)

---

## Troubleshooting

### Build Failures

**Error: "Module not found"**
```bash
# Verify all dependencies are in package.json
npm install

# Check for typos in import statements
# Ensure file paths use correct case (case-sensitive on Vercel)
```

**Error: "Out of memory"**
```bash
# Increase Node.js memory limit
# Add to package.json scripts:
"build": "NODE_OPTIONS=--max_old_space_size=4096 next build"
```

### Runtime Errors

**Error: "NEXT_PUBLIC_API_URL is undefined"**
- Environment variables not set in Vercel dashboard
- Rebuild required after adding variables
- Check variable name matches exactly (case-sensitive)

**Error: "CORS policy blocked"**
- Backend `CORS_ORIGINS` must include frontend URL
- Check for trailing slashes (should match exactly)
- Verify HTTPS vs HTTP

### Performance Issues

**Slow Page Load**
```bash
# Enable image optimization (already configured in Next.js)
# Use next/image component instead of <img> tags
# Check Vercel Analytics for performance insights
```

**High Bandwidth Usage**
- Optimize images: Convert to WebP, reduce resolution
- Enable Vercel Edge Network caching
- Compress demo JSON files

---

## Monitoring & Analytics

### Vercel Analytics (Built-in)

1. **Enable Analytics**
   - Project Settings → Analytics
   - Click "Enable Analytics"
   - Free tier includes 2,500 page views/month

2. **View Metrics**
   - Page load time
   - Web Vitals (LCP, FID, CLS)
   - Top pages

### Error Tracking with Sentry (Optional)

```bash
# Install Sentry
npm install @sentry/nextjs

# Initialize
npx @sentry/wizard@latest -i nextjs

# Add SENTRY_DSN to environment variables
```

### Uptime Monitoring (Optional)

**UptimeRobot (Free)**:
1. Create account at [uptimerobot.com](https://uptimerobot.com)
2. Add monitor:
   - Type: HTTPS
   - URL: `https://your-app.vercel.app`
   - Interval: 5 minutes
3. Set up email/Slack alerts

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (`npm run build`)
- [ ] Environment variables documented
- [ ] Demo data uploaded (S3/R2 or public directory)
- [ ] README updated with live URL

### Vercel Setup
- [ ] Project connected to GitHub
- [ ] Root directory set to `demo-ui`
- [ ] Environment variables configured
- [ ] Custom domain added (optional)
- [ ] SSL certificate verified

### Post-Deployment
- [ ] Test landing page (`/`)
- [ ] Test showcase page (`/showcase`)
- [ ] Verify animations work smoothly
- [ ] Check mobile responsiveness
- [ ] Test keyboard navigation (Tab, Enter)
- [ ] Verify all links work
- [ ] Check browser console for errors

### Backend (If Applicable)
- [ ] Backend deployed to Render/Railway
- [ ] WebSocket support enabled
- [ ] CORS configured correctly
- [ ] API health check endpoint working
- [ ] Frontend can connect to backend

---

## Continuous Integration

### GitHub Actions (Optional)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./demo-ui

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npm run lint
```

---

## Rollback Procedure

If deployment introduces bugs:

1. **Via Vercel Dashboard**
   - Deployments → Select previous working deployment
   - Click "..." → "Promote to Production"
   - Instant rollback (no rebuild needed)

2. **Via Git**
   ```bash
   # Revert last commit
   git revert HEAD
   git push origin main

   # Vercel auto-deploys reverted version
   ```

---

## Cost Summary

### Free Tier (MVP)
- Vercel: Free (100GB bandwidth/month)
- GitHub: Free
- **Total: $0/month**

### With Backend (Phase 3)
- Vercel: Free
- Render: $7/month
- **Total: $7/month**

### Production Scale
- Vercel Pro: $20/month (1TB bandwidth)
- Render Standard: $25/month
- CloudFlare R2: $5/month (demos storage)
- **Total: $50/month**

---

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [Render Documentation](https://render.com/docs)
- [Vercel CLI Reference](https://vercel.com/docs/cli)

---

## Getting Help

**Vercel Support:**
- Community forum: https://github.com/vercel/next.js/discussions
- Discord: https://discord.gg/nextjs

**Browser-Use Issues:**
- GitHub Issues: https://github.com/browser-use/browser-use/issues
- Documentation: https://docs.browser-use.com

**Common Issues:**
- Check Vercel deployment logs for build errors
- Verify all environment variables are set correctly
- Ensure demo data files exist in `public/demos/`
- Test locally with `npm run build && npm start` before deploying
