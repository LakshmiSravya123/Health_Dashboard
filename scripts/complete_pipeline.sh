#!/bin/bash
# Complete the pipeline - generate predictions and alerts

cd "$(dirname "$0")/.."

echo "🔮 Generating Burnout Predictions..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.etl.transformers.prediction_processor import PredictionProcessor
from src.utils.logger import log

processor = PredictionProcessor()
if not processor.predictor.is_trained:
    log.info('Training model...')
    metrics = processor.train_model()
    log.info(f'Model trained: {metrics}')

count = processor.generate_predictions()
log.info(f'✓ Generated {count} predictions')
EOF

echo ""
echo "🔔 Checking for Alerts..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from src.alerts.alert_manager import AlertManager
from src.utils.logger import log

manager = AlertManager()
count = manager.check_and_send_alerts()
log.info(f'✓ Sent {count} alerts')
EOF

echo ""
echo "📊 Checking Database Status..."
sqlite3 data/mental_health.db << 'EOF'
.mode column
.headers on
SELECT 'Raw Records' as Table_Name, COUNT(*) as Count FROM raw_sentiment_data
UNION ALL SELECT 'Processed', COUNT(*) FROM processed_sentiment_data
UNION ALL SELECT 'Features', COUNT(*) FROM user_features
UNION ALL SELECT 'Predictions', COUNT(*) FROM burnout_predictions
UNION ALL SELECT 'Alerts', COUNT(*) FROM alert_history;
EOF

echo ""
echo "✅ Pipeline Complete!"
echo "Run: python src/dashboard/app.py"
echo "Then open: http://localhost:8050"
