# 🔧 Vercel Deployment Troubleshooting

## Out of Memory (OOM) During Build

### ✅ Already Fixed
The latest commit reduces build memory usage:
- Removed `numpy` and `scikit-learn` (not needed for CSV demo mode)
- Pinned exact versions (faster dependency resolution)
- Increased function memory to 1024MB
- Set maxLambdaSize to 50mb

### If OOM Still Occurs

**Option 1: Use Vercel Pro (Recommended for Production)**
- Vercel Hobby tier has limited build resources
- Pro tier: $20/month, more build memory
- Go to: https://vercel.com/account/billing

**Option 2: Deploy Pre-built (No Build Step)**
Since your app is pure Python with no compilation:

1. Create `.vercelignore`:
```
__pycache__/
*.pyc
venv/
.git/
models/*.pkl
logs/
```

2. Ensure `requirements.vercel.txt` is minimal (already done)

3. Redeploy

**Option 3: Alternative Free Hosting**

If Vercel OOM persists, use these 100% free alternatives:

### A) Render (Free Tier)
- 512MB RAM (more than Vercel Hobby)
- Docker support (use your existing Dockerfile)

Steps:
```bash
# 1. Create render.yaml in repo root
cat > render.yaml << 'EOF'
services:
  - type: web
    name: mental-health-dashboard
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: DEPLOY_MODE
        value: vercel
    plan: free
EOF

# 2. Commit
git add render.yaml
git commit -m "Add Render config"
git push origin main

# 3. Go to https://dashboard.render.com/
# 4. New → Web Service → Connect your GitHub repo
# 5. Deploy
```

### B) Railway (Free $5/month credit)
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Set env vars
railway variables set DEPLOY_MODE=vercel
```

### C) Fly.io (Free tier: 3 VMs)
```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login and launch
flyctl auth login
flyctl launch

# 3. Set env
flyctl secrets set DEPLOY_MODE=vercel

# 4. Deploy
flyctl deploy
```

## Other Vercel Issues

### SIGKILL During Runtime
- Ensure `DEPLOY_MODE=vercel` is set in env vars
- Check that `PYTHON_REQUIREMENTS_FILE=requirements.vercel.txt` is set
- Verify no heavy imports in `api/index.py` or `src/dashboard/app.py`

### Charts Show "No Data"
- Confirm `DEPLOY_MODE=vercel` env var is set
- Check that demo CSVs exist in `data/` directory
- Redeploy after setting env vars

### Import Errors
- Check Function Logs in Vercel dashboard
- Ensure all imports are in `requirements.vercel.txt`
- Verify Python version compatibility (3.10)

### Slow Cold Starts
- Current setup should be ~2-3s
- If slower, check for heavy imports at module top level
- Use lazy imports (already implemented in callbacks)

## Recommended: Use Render for Free Production

Render's free tier is more generous than Vercel for Python apps:
- 512MB RAM vs Vercel's limited build memory
- Native Docker support
- Persistent disk (for SQLite if needed)
- Background workers (for pipelines)

**Quick Render Deploy:**
1. Push the `render.yaml` (shown above) to your repo
2. Go to https://dashboard.render.com/
3. New → Web Service → Connect GitHub
4. Select `LakshmiSravya123/Health_Dashboard`
5. Render auto-detects `render.yaml` and deploys

Your dashboard will be live at `https://mental-health-dashboard.onrender.com` in ~5 minutes.

## Summary

| Platform | Free Tier | Build RAM | Runtime RAM | Best For |
|----------|-----------|-----------|-------------|----------|
| **Vercel** | Yes | Limited | 1024MB | Static sites, light APIs |
| **Render** | Yes | 512MB | 512MB | **Python apps (recommended)** |
| **Railway** | $5 credit | Good | Good | Full-stack apps |
| **Fly.io** | 3 VMs | Good | 256MB | Containers |

**Recommendation**: Use **Render** for your Mental Health Dashboard. It's designed for Python apps and won't OOM during build.

## Need Help?
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Fly.io Docs: https://fly.io/docs

Your app is ready for any of these platforms! 🚀
