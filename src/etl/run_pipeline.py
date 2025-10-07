"""Main ETL pipeline runner."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.etl.extractors.twitter_extractor import TwitterExtractor
from src.etl.extractors.reddit_extractor import RedditExtractor
from src.etl.extractors.survey_extractor import SurveyExtractor
from src.etl.loaders.database_loader import get_loader
from src.utils.config_loader import get_config
from src.utils.logger import log


class ETLPipeline:
    """Main ETL pipeline for mental health data."""
    
    def __init__(self):
        """Initialize ETL pipeline."""
        self.config = get_config()
        self.loader = get_loader()
        
        # Initialize extractors
        self.extractors = {}
        self._init_extractors()
    
    def _init_extractors(self):
        """Initialize data extractors based on configuration."""
        data_sources = self.config.get_data_sources_config()
        
        # Twitter
        if data_sources.get('twitter', {}).get('enabled', False):
            try:
                self.extractors['twitter'] = TwitterExtractor()
                log.info("Twitter extractor initialized")
            except Exception as e:
                log.warning(f"Could not initialize Twitter extractor: {str(e)}")
        
        # Reddit
        if data_sources.get('reddit', {}).get('enabled', False):
            try:
                self.extractors['reddit'] = RedditExtractor()
                log.info("Reddit extractor initialized")
            except Exception as e:
                log.warning(f"Could not initialize Reddit extractor: {str(e)}")
        
        # Surveys
        if data_sources.get('surveys', {}).get('enabled', False) or \
           data_sources.get('employee_feedback', {}).get('enabled', False):
            try:
                self.extractors['survey'] = SurveyExtractor()
                log.info("Survey extractor initialized")
            except Exception as e:
                log.warning(f"Could not initialize Survey extractor: {str(e)}")
    
    def extract_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data from all configured sources.
        
        Returns:
            Dictionary mapping source name to extracted records
        """
        all_data = {}
        
        for source_name, extractor in self.extractors.items():
            try:
                log.info(f"Extracting data from {source_name}")
                data = extractor.extract_with_validation()
                all_data[source_name] = data
                log.info(f"Extracted {len(data)} records from {source_name}")
            except Exception as e:
                log.error(f"Error extracting from {source_name}: {str(e)}")
                all_data[source_name] = []
        
        return all_data
    
    def load_all(self, data: Dict[str, List[Dict[str, Any]]]) -> int:
        """Load all extracted data into BigQuery.
        
        Args:
            data: Dictionary mapping source name to records
            
        Returns:
            Total number of rows loaded
        """
        total_loaded = 0
        
        # Combine all data
        all_records = []
        for source_name, records in data.items():
            all_records.extend(records)
        
        if all_records:
            try:
                loaded = self.loader.load_raw_sentiment_data(all_records)
                total_loaded += loaded
                log.info(f"Loaded {loaded} total records into BigQuery")
            except Exception as e:
                log.error(f"Error loading data: {str(e)}")
        
        return total_loaded
    
    def run(self) -> Dict[str, Any]:
        """Run the complete ETL pipeline.
        
        Returns:
            Pipeline execution summary
        """
        start_time = datetime.utcnow()
        log.info("=" * 60)
        log.info("Starting ETL Pipeline")
        log.info("=" * 60)
        
        summary = {
            'start_time': start_time.isoformat(),
            'sources_processed': 0,
            'records_extracted': 0,
            'records_loaded': 0,
            'errors': [],
            'status': 'success'
        }
        
        try:
            # Extract
            extracted_data = self.extract_all()
            summary['sources_processed'] = len(extracted_data)
            summary['records_extracted'] = sum(len(records) for records in extracted_data.values())
            
            # Load
            if summary['records_extracted'] > 0:
                loaded = self.load_all(extracted_data)
                summary['records_loaded'] = loaded
            else:
                log.warning("No records extracted, skipping load phase")
            
        except Exception as e:
            log.error(f"Pipeline error: {str(e)}")
            summary['status'] = 'failed'
            summary['errors'].append(str(e))
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        summary['end_time'] = end_time.isoformat()
        summary['duration_seconds'] = duration
        
        log.info("=" * 60)
        log.info(f"Pipeline completed in {duration:.2f} seconds")
        log.info(f"Status: {summary['status']}")
        log.info(f"Records extracted: {summary['records_extracted']}")
        log.info(f"Records loaded: {summary['records_loaded']}")
        log.info("=" * 60)
        
        return summary
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policies."""
        log.info("Starting data cleanup")
        
        etl_config = self.config.config.get('etl', {})
        retention = etl_config.get('retention', {})
        
        tables_to_clean = [
            ('raw_sentiment_data', retention.get('raw_data_days', 90)),
            ('processed_sentiment_data', retention.get('processed_data_days', 365)),
            ('burnout_predictions', retention.get('predictions_days', 180))
        ]
        
        for table_name, days in tables_to_clean:
            try:
                deleted = self.loader.delete_old_records(table_name, days)
                log.info(f"Cleaned {deleted} records from {table_name}")
            except Exception as e:
                log.error(f"Error cleaning {table_name}: {str(e)}")


def main():
    """Main function to run ETL pipeline."""
    pipeline = ETLPipeline()
    summary = pipeline.run()
    
    # Optionally run cleanup
    # pipeline.cleanup_old_data()
    
    return summary


if __name__ == "__main__":
    main()
