# Quick Start Guide - 100% FREE Setup

Get the Mental Health Dashboard running in **10 minutes** with **ZERO cost**!

## Prerequisites

- Python 3.9+ (free)
- 10 minutes of your time
- **NO paid services needed!**

## 🚀 Quick Setup (4 Steps)

### Step 1: Install Dependencies (3 min)

```bash
cd Health_dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Generate Sample Data (1 min)

```bash
# Create sample mental health survey data
python scripts/generate_sample_data.py
```

This creates 200 sample records in `data/sample_survey_data.csv`

### Step 3: Run the Pipeline (3 min)

```bash
# This will:
# 1. Create SQLite database (free, local)
# 2. Load sample data
# 3. Analyze sentiment with BERT (free)
# 4. Train burnout prediction model (free)
# 5. Generate predictions

python scripts/run_full_pipeline.py
```

### Step 4: Launch Dashboard (1 min)

```bash
python src/dashboard/app.py
```

**Open browser**: http://localhost:8050 🎉

## ✅ That's It!

You now have a fully functional mental health analytics dashboard running locally with:
- ✅ SQLite database (100% free)
- ✅ NLP sentiment analysis
- ✅ ML burnout predictions
- ✅ Interactive visualizations
- ✅ Sample data to explore

## 📊 What You'll See

The dashboard displays:

1. **Overview Tab**
   - Total users monitored
   - High-risk user count
   - Average sentiment score
   - Active alerts
   - Sentiment trends over time
   - Risk distribution pie chart

2. **Sentiment Analysis Tab**
   - Sentiment distribution
   - Sentiment by data source
   - Keyword frequency analysis
   - Recent posts

3. **Burnout Predictions Tab**
   - Risk score heatmap
   - Risk distribution histogram
   - Contributing factors
   - High-risk users table

4. **Alerts Tab**
   - Alert timeline
   - Alert history

## 🔄 Running the Pipeline

### One-Time Full Run
```bash
python scripts/run_full_pipeline.py
```

This executes:
1. ✅ Data extraction (Twitter, Reddit, Surveys)
2. ✅ Sentiment analysis (NLP processing)
3. ✅ Feature engineering
4. ✅ Burnout prediction (ML model)
5. ✅ Alert generation

### Individual Components

```bash
# Just extract data
python src/etl/run_pipeline.py

# Just analyze sentiment
python src/etl/transformers/sentiment_processor.py

# Just compute features
python src/etl/transformers/feature_processor.py

# Just generate predictions
python src/etl/transformers/prediction_processor.py

# Just check alerts
python src/alerts/alert_manager.py
```

## 🔌 Adding Real Data Sources

### Twitter Integration

1. Get API credentials from [developer.twitter.com](https://developer.twitter.com)
2. Add to `.env`:
   ```bash
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_BEARER_TOKEN=your_token
   ```
3. Enable in `config/config.yaml`:
   ```yaml
   data_sources:
     twitter:
       enabled: true
   ```

### Reddit Integration

1. Create app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Add to `.env`:
   ```bash
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```
3. Enable in `config/config.yaml`:
   ```yaml
   data_sources:
     reddit:
       enabled: true
   ```

### Survey/CSV Data

1. Place CSV file in `data/` directory
2. Update `config/config.yaml`:
   ```yaml
   data_sources:
     employee_feedback:
       enabled: true
       source_type: "csv"
       path: "data/your_survey_data.csv"
   ```

CSV format:
```csv
user_id,response_text,timestamp,survey_type
user_1,"Feeling stressed lately",2024-01-15T10:00:00,wellbeing
user_2,"Great work environment!",2024-01-15T11:00:00,wellbeing
```

## 📧 Setting Up Alerts

### Email Alerts

1. Generate app password (for Gmail: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords))
2. Add to `.env`:
   ```bash
   ALERT_EMAIL=your_email@gmail.com
   ALERT_EMAIL_PASSWORD=your_app_password
   ```
3. Enable in `config/config.yaml`:
   ```yaml
   alerts:
     enabled: true
     channels:
       email:
         enabled: true
   ```

### Slack Alerts

1. Create Slack webhook: [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)
2. Add to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
3. Enable in config

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access dashboard at http://localhost:8050

## ⏰ Scheduling (Production)

### Using Cron

```bash
# Edit crontab
crontab -e

# Add line (runs every 6 hours)
0 */6 * * * cd /path/to/Health_dashboard && /path/to/venv/bin/python scripts/run_full_pipeline.py >> logs/cron.log 2>&1
```

### Using systemd (Linux)

Create `/etc/systemd/system/mental-health-pipeline.service`:

```ini
[Unit]
Description=Mental Health Pipeline
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Health_dashboard
Environment="GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json"
ExecStart=/path/to/venv/bin/python scripts/run_full_pipeline.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mental-health-pipeline
sudo systemctl start mental-health-pipeline
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_sentiment.py -v
```

## 📈 Monitoring

### Check Pipeline Status

```bash
# View logs
tail -f logs/dashboard.log

# Check BigQuery data
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `your-project.mental_health_analytics.raw_sentiment_data`'

# Check last run
bq query --use_legacy_sql=false \
  'SELECT MAX(ingestion_timestamp) FROM `your-project.mental_health_analytics.raw_sentiment_data`'
```

### Dashboard Metrics

Access http://localhost:8050 and check:
- ✅ Total Users Monitored > 0
- ✅ Sentiment Trend shows data
- ✅ Risk Distribution populated
- ✅ No error messages

## 🔧 Troubleshooting

### "No data in dashboard"
```bash
# Generate sample data
python scripts/generate_sample_data.py

# Run pipeline
python scripts/run_full_pipeline.py

# Refresh dashboard (Ctrl+R)
```

### "BigQuery permission denied"
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify service account has BigQuery Admin role
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### "Module not found"
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Dashboard won't start"
```bash
# Check port availability
lsof -i :8050

# Use different port
python src/dashboard/app.py --port 8051
```

## 📚 Next Steps

1. **Customize**: Edit `config/config.yaml` to adjust thresholds and keywords
2. **Integrate**: Add your real data sources (Twitter, Reddit, surveys)
3. **Tune Models**: Adjust ML model parameters for better predictions
4. **Scale**: Deploy to cloud (GCP Cloud Run, AWS ECS, etc.)
5. **Secure**: Implement authentication and role-based access

## 🆘 Need Help?

- **Documentation**: See [SETUP.md](SETUP.md) for detailed setup
- **Architecture**: See [README.md](README.md) for system overview
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guide
- **Issues**: Open an issue on GitHub

## 🎯 Key Features Checklist

After setup, you should have:

- ✅ BigQuery data warehouse with 5 tables
- ✅ ELT pipeline for data extraction
- ✅ NLP sentiment analysis (BERT-based)
- ✅ ML burnout prediction model
- ✅ Interactive Plotly Dash dashboard
- ✅ Automated alert system
- ✅ Sample data for testing
- ✅ Comprehensive logging

**Congratulations! Your Mental Health Dashboard is ready! 🎉**
