# 🚀 Quick Start - Mental Health Dashboard

## Run in 3 Commands (100% FREE)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Generate data & run pipeline (creates 500 records)
python scripts/generate_sample_data.py
python scripts/run_full_pipeline.py

# 3. Launch dashboard
python src/dashboard/app.py
```

**Open**: http://localhost:8050 🎉

---

## 📊 What You'll See

### Modern, Beautiful Dashboard with:
- **Gradient Header** - Purple/blue theme
- **Metric Cards** - Large icons, clean design
- **Interactive Charts** - Sentiment trends, risk heatmaps
- **Real-time Updates** - Auto-refresh every 30 seconds

### Data:
- ✅ 500 mental health survey responses
- ✅ ~125 unique users
- ✅ Sentiment analysis (BERT NLP)
- ✅ Burnout predictions (ML model)
- ✅ Risk alerts

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8050 | xargs kill -9
python src/dashboard/app.py
```

### Reset Database
```bash
python scripts/reset_database.py
```

### Complete Partial Pipeline
```bash
./scripts/complete_pipeline.sh
```

---

## 💡 Features

- **100% FREE** - No cloud costs, uses SQLite
- **No API Keys** - Works with sample CSV data
- **Privacy-First** - All user IDs anonymized
- **Production-Ready** - Scalable architecture
- **Modern UI** - Beautiful gradients and shadows

---

## 📚 Documentation

- **[README.md](README.md)** - Full project overview
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup
- **[SETUP.md](SETUP.md)** - Advanced configuration

---

**Total Commits**: 25 commits  
**Repository**: https://github.com/LakshmiSravya123/Health_Dashboard.git  
**Status**: ✅ Production Ready
