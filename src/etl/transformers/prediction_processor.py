"""Process burnout predictions."""

import pandas as pd
from pathlib import Path
from src.etl.loaders.database_loader import get_loader
from src.models.burnout.burnout_predictor import BurnoutPredictor
from src.utils.config_loader import get_config
from src.utils.logger import log


class PredictionProcessor:
    """Process burnout predictions."""
    
    def __init__(self, model_path: str = None):
        """Initialize prediction processor.
        
        Args:
            model_path: Path to trained model
        """
        self.loader = get_loader()
        self.config = get_config()
        
        # Initialize or load model
        if model_path is None:
            model_dir = Path(__file__).parent.parent.parent.parent / "models"
            model_dir.mkdir(exist_ok=True)
            model_path = model_dir / "burnout_model.pkl"
        
        self.predictor = BurnoutPredictor(model_path=str(model_path) if Path(model_path).exists() else None)
        self.model_path = model_path
    
    def train_model(self) -> dict:
        """Train the burnout prediction model.
        
        Returns:
            Training metrics
        """
        log.info("Fetching user features for training...")
        
        # Get user features
        features_df = self._get_user_features()
        
        if features_df.empty:
            log.error("No features available for training")
            return {}
        
        # Train model
        metrics = self.predictor.train(features_df)
        
        # Save model
        self.predictor.save_model(str(self.model_path))
        
        return metrics
    
    def generate_predictions(self) -> int:
        """Generate predictions for all users and load to BigQuery.
        
        Returns:
            Number of predictions generated
        """
        if not self.predictor.is_trained:
            log.error("Model not trained. Train model first.")
            return 0
        
        log.info("Fetching user features for prediction...")
        
        # Get user features
        features_df = self._get_user_features()
        
        if features_df.empty:
            log.warning("No features available for prediction")
            return 0
        
        log.info(f"Generating predictions for {len(features_df)} users...")
        
        # Generate predictions
        predictions = self.predictor.predict_batch(features_df)
        
        # Load to BigQuery
        loaded = self.loader.load_burnout_predictions(predictions)
        
        log.info(f"Generated and loaded {loaded} predictions")
        return loaded
    
    def _get_user_features(self) -> pd.DataFrame:
        """Get latest user features from BigQuery.
        
        Returns:
            DataFrame of user features
        """
        features_table = 'user_features'
        
        sql = f"""
        SELECT *
        FROM {features_table}
        WHERE feature_date = (
            SELECT MAX(feature_date)
            FROM {features_table}
        )
        """
        
        return self.loader.query(sql)


def main():
    """Main function to process predictions."""
    processor = PredictionProcessor()
    
    # Train model if not already trained
    if not processor.predictor.is_trained:
        log.info("Training model...")
        metrics = processor.train_model()
        log.info(f"Model training complete: {metrics}")
    
    # Generate predictions
    count = processor.generate_predictions()
    log.info(f"Prediction processing complete. Records: {count}")


if __name__ == "__main__":
    main()
