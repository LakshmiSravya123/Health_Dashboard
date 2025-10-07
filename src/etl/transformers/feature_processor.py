"""Process feature engineering for burnout prediction."""

from datetime import datetime
from src.etl.loaders.database_loader import get_loader
from src.models.burnout.feature_engineering import FeatureEngineer
from src.utils.logger import log


class FeatureProcessor:
    """Process feature engineering."""
    
    def __init__(self):
        """Initialize feature processor."""
        self.loader = get_loader()
        self.engineer = FeatureEngineer()
    
    def compute_and_load_features(self, end_date: datetime = None) -> int:
        """Compute features for all users and load to BigQuery.
        
        Args:
            end_date: End date for feature computation
            
        Returns:
            Number of feature records loaded
        """
        log.info("Computing user features...")
        
        # Compute features
        features = self.engineer.compute_all_user_features(end_date=end_date)
        
        if not features:
            log.warning("No features computed")
            return 0
        
        # Load to BigQuery
        loaded = self.loader.load_user_features(features)
        
        log.info(f"Computed and loaded features for {loaded} users")
        return loaded


def main():
    """Main function to process features."""
    processor = FeatureProcessor()
    count = processor.compute_and_load_features()
    log.info(f"Feature processing complete. Records: {count}")


if __name__ == "__main__":
    main()
