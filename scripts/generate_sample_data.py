"""Generate sample data for testing the dashboard."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.extractors.survey_extractor import SurveyExtractor
from src.utils.logger import log


def main():
    """Generate sample survey data."""
    log.info("Generating sample data...")
    
    extractor = SurveyExtractor()
    
    # Create sample data with more records for better visualization
    file_path = extractor.create_sample_data(num_records=500)
    
    log.info(f"Sample data created at: {file_path}")
    log.info("You can now run the ETL pipeline to load this data")


if __name__ == "__main__":
    main()
