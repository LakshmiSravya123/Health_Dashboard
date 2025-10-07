# 🚀 Deploy to Vercel - Complete Guide

Your Mental Health Dashboard is now ready for Vercel with **CSV-backed demo mode**.

## ✅ What's Ready
- `api/index.py`: Serverless entrypoint (Flask WSGI)
- `vercel.json`: Builds API config
- `requirements.vercel.txt`: Slim dependencies (no transformers/torch)
- `src/dashboard/vercel_data_provider.py`: CSV-based data provider
- Demo CSVs in `data/`: 500 sentiment records, 50 predictions, 100 alerts
- Lazy imports: no heavy loads at cold start

## 📋 Deploy Steps

### Option 1: GitHub Import (Recommended)
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select `LakshmiSravya123/Health_Dashboard`
4. Framework Preset: **Other**
5. Root Directory: leave as `/` (repo root)
6. Click **Deploy**

### Option 2: Vercel CLI
```bash
# Use npx (no global install needed)
npx vercel

# Production
npx vercel --prod
```

## ⚙️ Required Environment Variables
After deploying, go to **Project → Settings → Environment Variables** and add:

| Key | Value | Apply To |
|-----|-------|----------|
| `DEPLOY_MODE` | `vercel` | Production + Preview |
| `PYTHON_REQUIREMENTS_FILE` | `requirements.vercel.txt` | Production + Preview |

Then **redeploy** from the Vercel dashboard.

## 🎯 What Happens
- When `DEPLOY_MODE=vercel`:
  - Dashboard uses `VercelDataProvider` (reads from CSVs in `data/`)
  - No SQLite connections or writes
  - Instant cold starts (~2-3s)
  - All charts populated with demo data

- When `DEPLOY_MODE` is not set (local):
  - Dashboard uses `DashboardDataProvider` (SQLite)
  - Full pipeline, model training, predictions
  - Writable database

## 📊 Demo Data Included
- **500 sentiment records** from `data/demo_sentiment.csv`
- **50 burnout predictions** from `data/demo_predictions.csv`
- **100 alerts** from `data/demo_alerts.csv`
- **50 user features** from `data/demo_features.csv`

All charts will show real data immediately on Vercel.

## 🔍 Verify Deployment
After deploy:
1. Open your Vercel URL
2. You should see the dashboard with:
   - Gradient header
   - 4 metric cards populated
   - Sentiment trend chart
   - Risk distribution
   - Burnout heatmap
   - Keyword analysis
   - Alert timeline

## 🐛 Troubleshooting

### SIGKILL / Sandbox Exit
- Ensure `PYTHON_REQUIREMENTS_FILE=requirements.vercel.txt` is set
- Check that `requirements.vercel.txt` does NOT include transformers/torch/spacy
- Redeploy after setting env vars

### Charts Show "No Data"
- Ensure `DEPLOY_MODE=vercel` is set in Vercel env
- Check that demo CSVs are committed in `data/`
- Redeploy

### Import Errors
- Check Function Logs in Vercel dashboard
- Ensure all imports in `api/index.py` and `src/dashboard/` are available in `requirements.vercel.txt`

### Slow Cold Starts
- Keep `requirements.vercel.txt` minimal
- Avoid importing heavy modules at top level
- Use lazy imports in callbacks (already implemented)

## 🎨 Features on Vercel
- ✅ Modern gradient UI
- ✅ Interactive filters (date, risk, sentiment, source)
- ✅ Auto-refresh every 30 seconds
- ✅ Responsive charts (Plotly)
- ✅ 500 demo records
- ✅ All tabs functional (Overview, Sentiment, Burnout, Alerts)

## 🔄 Update Demo Data
To refresh demo CSVs with new data:
```bash
# Locally, with venv activated
source venv/bin/activate
python scripts/generate_sample_data.py
python scripts/run_full_pipeline.py

# Export new CSVs
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.etl.loaders.database_loader import get_loader
import pandas as pd

loader = get_loader()
loader.query("SELECT * FROM processed_sentiment_data LIMIT 500").to_csv('data/demo_sentiment.csv', index=False)
loader.query("SELECT * FROM burnout_predictions LIMIT 100").to_csv('data/demo_predictions.csv', index=False)
loader.query("SELECT * FROM alert_history LIMIT 100").to_csv('data/demo_alerts.csv', index=False)
print("✓ Demo CSVs updated")
EOF

# Commit and push
git add data/demo_*.csv
git commit -m "Update demo CSVs"
git push origin main
```

Vercel will auto-redeploy with new data.

## 📈 Production Considerations
- Vercel serverless is read-only; no pipeline or DB writes
- For full production with pipelines:
  - Use Render/Fly.io/Heroku with Docker
  - Or connect to a managed DB (Postgres/MySQL) and refactor loaders
- Current Vercel setup is perfect for:
  - Demos
  - Presentations
  - Prototypes
  - Read-only dashboards

## 🎉 You're Done!
Your dashboard is live on Vercel with full demo data and beautiful charts.

**Next**: Share your Vercel URL and show off your AI-powered mental health analytics! 🚀
