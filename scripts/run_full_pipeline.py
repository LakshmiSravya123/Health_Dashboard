"""Run the complete data pipeline."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.run_pipeline import ETLPipeline
from src.etl.transformers.sentiment_processor import SentimentProcessor
from src.etl.transformers.feature_processor import FeatureProcessor
from src.etl.transformers.prediction_processor import PredictionProcessor
from src.alerts.alert_manager import AlertManager
from src.utils.logger import log


def main():
    """Run the complete pipeline."""
    log.info("=" * 70)
    log.info("STARTING FULL MENTAL HEALTH ANALYTICS PIPELINE (100% FREE)")
    log.info("=" * 70)
    
    # Step 0: Initialize Database
    log.info("\n[0/5] Initializing Database...")
    from src.etl.loaders.database_loader import get_loader
    loader = get_loader()
    if hasattr(loader, 'create_tables'):
        loader.create_tables()
        log.info("✓ Database initialized (SQLite)")
    
    # Step 1: Extract and Load
    log.info("\n[1/5] Running ETL Pipeline...")
    pipeline = ETLPipeline()
    etl_summary = pipeline.run()
    
    # Check if we have any data at all (new or existing)
    if etl_summary['records_extracted'] == 0:
        log.warning("No data extracted. Pipeline stopped.")
        return
    
    if etl_summary['records_loaded'] == 0:
        log.info("Data already exists in database, continuing with processing...")
    
    # Step 2: Process Sentiment
    log.info("\n[2/5] Processing Sentiment Analysis...")
    sentiment_processor = SentimentProcessor()
    sentiment_count = sentiment_processor.process_all(max_batches=5)
    log.info(f"Processed {sentiment_count} sentiment records")
    
    # Step 3: Compute Features
    log.info("\n[3/5] Computing User Features...")
    feature_processor = FeatureProcessor()
    feature_count = feature_processor.compute_and_load_features()
    log.info(f"Computed features for {feature_count} users")
    
    # Step 4: Generate Predictions
    log.info("\n[4/5] Generating Burnout Predictions...")
    prediction_processor = PredictionProcessor()
    
    # Train model if needed
    if not prediction_processor.predictor.is_trained:
        log.info("Training burnout prediction model...")
        metrics = prediction_processor.train_model()
        log.info(f"Model training metrics: {metrics}")
    
    prediction_count = prediction_processor.generate_predictions()
    log.info(f"Generated {prediction_count} predictions")
    
    # Step 5: Check and Send Alerts
    log.info("\n[5/5] Checking Alert Conditions...")
    alert_manager = AlertManager()
    alert_count = alert_manager.check_and_send_alerts()
    log.info(f"Sent {alert_count} alerts")
    
    # Summary
    log.info("\n" + "=" * 70)
    log.info("PIPELINE COMPLETE")
    log.info("=" * 70)
    log.info(f"Records Extracted: {etl_summary['records_extracted']}")
    log.info(f"Records Loaded: {etl_summary['records_loaded']}")
    log.info(f"Sentiment Processed: {sentiment_count}")
    log.info(f"Features Computed: {feature_count}")
    log.info(f"Predictions Generated: {prediction_count}")
    log.info(f"Alerts Sent: {alert_count}")
    log.info("=" * 70)


if __name__ == "__main__":
    main()
