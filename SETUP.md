# Setup Guide - Mental Health Dashboard

This guide will help you set up and run the Mental Health Sentiment and Burnout Prediction Dashboard.

## Prerequisites

### Required
- Python 3.9 or higher
- Google Cloud Platform account with BigQuery enabled
- Git (for cloning the repository)

### Optional (for full functionality)
- Twitter Developer Account (for Twitter data extraction)
- Reddit API credentials (for Reddit data extraction)
- SMTP email account (for email alerts)
- Slack workspace (for Slack alerts)

## Step 1: Clone and Setup Environment

```bash
# Navigate to project directory
cd Health_dashboard

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model (for NLP)
python -m spacy download en_core_web_sm
```

## Step 2: Google Cloud Platform Setup

### 2.1 Create GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2.2 Enable BigQuery API

1. Navigate to "APIs & Services" > "Library"
2. Search for "BigQuery API"
3. Click "Enable"

### 2.3 Create Service Account

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name it "mental-health-dashboard"
4. Grant roles:
   - BigQuery Admin
   - BigQuery Data Editor
   - BigQuery Job User
5. Click "Create Key" and download JSON file
6. Save the JSON file securely (e.g., `~/credentials/mental-health-sa.json`)

### 2.4 Set Environment Variable

```bash
# On macOS/Linux:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# On Windows:
# set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json

# Make it permanent by adding to ~/.bashrc or ~/.zshrc
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"' >> ~/.bashrc
```

## Step 3: Configuration

### 3.1 Copy Environment Template

```bash
cp .env.example .env
```

### 3.2 Edit Configuration Files

**Edit `.env`:**
```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GCP_PROJECT_ID=your-gcp-project-id

# Optional - Add if using Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_token

# Optional - Add if using Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Optional - Add for email alerts
ALERT_EMAIL=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
```

**Edit `config/config.yaml`:**
```yaml
bigquery:
  project_id: "your-actual-gcp-project-id"  # Replace with your project ID
  dataset_id: "mental_health_analytics"
  location: "US"
```

## Step 4: Initialize Database

Create the BigQuery dataset and tables:

```bash
python src/etl/setup_warehouse.py
```

You should see output confirming table creation:
```
Created dataset your-project.mental_health_analytics
Created table your-project.mental_health_analytics.raw_sentiment_data
Created table your-project.mental_health_analytics.processed_sentiment_data
...
```

## Step 5: Generate Sample Data (Optional)

If you don't have API credentials yet, generate sample data:

```bash
python scripts/generate_sample_data.py
```

This creates `data/sample_survey_data.csv` with 200 sample records.

## Step 6: Run the Pipeline

### Option A: Run Complete Pipeline

```bash
python scripts/run_full_pipeline.py
```

This runs all steps:
1. Extract data from sources
2. Analyze sentiment
3. Compute features
4. Train model and generate predictions
5. Check and send alerts

### Option B: Run Individual Components

```bash
# Extract and load data
python src/etl/run_pipeline.py

# Process sentiment
python src/etl/transformers/sentiment_processor.py

# Compute features
python src/etl/transformers/feature_processor.py

# Generate predictions
python src/etl/transformers/prediction_processor.py

# Check alerts
python src/alerts/alert_manager.py
```

## Step 7: Launch Dashboard

```bash
python src/dashboard/app.py
```

The dashboard will be available at: **http://localhost:8050**

Open your browser and navigate to this URL to view the dashboard.

## Step 8: Verify Installation

### Check BigQuery Tables

```bash
# List tables
bq ls mental_health_analytics

# Query data
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as count FROM `your-project.mental_health_analytics.raw_sentiment_data`'
```

### Check Dashboard

1. Open http://localhost:8050
2. You should see:
   - Key metrics cards
   - Sentiment trend chart
   - Risk distribution
   - Various visualizations

## Troubleshooting

### Issue: "No module named 'src'"

**Solution:**
```bash
# Make sure you're in the project root directory
cd Health_dashboard

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: "google.auth.exceptions.DefaultCredentialsError"

**Solution:**
- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Check that the service account JSON file exists
- Ensure the service account has BigQuery permissions

### Issue: "No data available" in dashboard

**Solution:**
1. Check if data was loaded: `bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM mental_health_analytics.raw_sentiment_data'`
2. Run the pipeline: `python scripts/run_full_pipeline.py`
3. Generate sample data if needed: `python scripts/generate_sample_data.py`

### Issue: Twitter/Reddit API errors

**Solution:**
- Verify API credentials in `.env`
- Check API rate limits
- Disable sources in `config/config.yaml` if not using:
  ```yaml
  data_sources:
    twitter:
      enabled: false
    reddit:
      enabled: false
  ```

### Issue: Model training fails

**Solution:**
- Ensure you have enough data (minimum 50 records)
- Check that sentiment processing completed successfully
- Verify feature computation ran without errors

## Production Deployment

### Scheduling with Cron

Add to crontab for automated runs:

```bash
# Run pipeline every 6 hours
0 */6 * * * cd /path/to/Health_dashboard && /path/to/venv/bin/python scripts/run_full_pipeline.py >> logs/pipeline.log 2>&1
```

### Using Apache Airflow

Create a DAG in `airflow/dags/`:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

dag = DAG(
    'mental_health_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 */6 * * *',  # Every 6 hours
    catchup=False
)

run_pipeline = BashOperator(
    task_id='run_pipeline',
    bash_command='cd /path/to/Health_dashboard && python scripts/run_full_pipeline.py',
    dag=dag
)
```

### Docker Deployment

```bash
# Build image
docker build -t mental-health-dashboard .

# Run container
docker run -d \
  -p 8050:8050 \
  -v /path/to/credentials:/credentials \
  -e GOOGLE_APPLICATION_CREDENTIALS=/credentials/service-account.json \
  mental-health-dashboard
```

## Next Steps

1. **Customize Configuration**: Adjust thresholds, keywords, and alert rules in `config/config.yaml`
2. **Add Data Sources**: Configure Twitter, Reddit, or custom survey integrations
3. **Tune Models**: Adjust sentiment and burnout prediction model parameters
4. **Set Up Monitoring**: Configure Sentry or Prometheus for production monitoring
5. **Enable Alerts**: Configure email, Slack, or SMS alert channels

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review logs in `logs/dashboard.log`
- Open an issue on GitHub

## Security Notes

- Never commit `.env` or credential files to version control
- Use environment variables for all sensitive data
- Rotate API keys and credentials regularly
- Enable audit logging in BigQuery
- Review and comply with HIPAA, GDPR, and other regulations
