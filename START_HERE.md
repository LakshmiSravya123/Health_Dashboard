# 🚀 Quick Start - Mental Health Dashboard

## ✅ Complete Setup (5 Steps)

### 1. Activate Virtual Environment
```bash
cd Health_dashboard
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies (if not done)
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Generate Sample Data
```bash
python scripts/generate_sample_data.py
```

### 4. Run the Pipeline
```bash
python scripts/run_full_pipeline.py
```

### 5. Launch Dashboard
```bash
python src/dashboard/app.py
```

Then open: **http://localhost:8050**

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Solution**: Make sure you're in the project root and virtual environment is activated:
```bash
cd Health_dashboard
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/dashboard/app.py
```

### "ModuleNotFoundError: No module named 'loguru'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### "No data loaded. Pipeline stopped."
**Solution**: Generate sample data first:
```bash
python scripts/generate_sample_data.py
```

### Dashboard won't start
**Solution**: Use the helper script:
```bash
./run_dashboard.sh
```

---

## 📊 What You'll See

Once the dashboard loads, you'll have:
- **Overview Tab**: Key metrics, sentiment trends, risk distribution
- **Sentiment Analysis Tab**: Sentiment breakdown, keyword analysis
- **Burnout Predictions Tab**: Risk heatmap, contributing factors
- **Alerts Tab**: Alert timeline and history

---

## 🎯 Next Steps

1. **Add Your Own Data**: Place CSV files in `data/` directory
2. **Configure Sources**: Edit `config/config.yaml`
3. **Customize Alerts**: Modify alert rules in config
4. **Deploy**: Use Docker or cloud platforms

---

## 💡 Tips

- **Free Setup**: Uses SQLite by default (no cloud costs)
- **Sample Data**: 200 mental health survey responses included
- **Auto-refresh**: Dashboard updates every 30 seconds
- **Privacy**: All user IDs are anonymized (SHA-256)

---

## 📞 Need Help?

- Check [README.md](README.md) for full documentation
- See [QUICKSTART.md](QUICKSTART.md) for detailed setup
- Open an issue on GitHub
