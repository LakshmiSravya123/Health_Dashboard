"""Process sentiment analysis on raw data."""

from typing import List, Dict, Any
from src.etl.loaders.database_loader import get_loader
from src.models.sentiment.sentiment_analyzer import SentimentAnalyzer
from src.utils.logger import log


class SentimentProcessor:
    """Process sentiment analysis on raw data."""
    
    def __init__(self):
        """Initialize sentiment processor."""
        self.loader = get_loader()
        self.analyzer = SentimentAnalyzer()
    
    def process_unprocessed_records(self, batch_size: int = 1000) -> int:
        """Process all unprocessed records.
        
        Args:
            batch_size: Number of records to process at once
            
        Returns:
            Number of records processed
        """
        log.info("Fetching unprocessed records...")
        
        # Get unprocessed records
        unprocessed = self.loader.get_unprocessed_records(limit=batch_size)
        
        if unprocessed.empty:
            log.info("No unprocessed records found")
            return 0
        
        log.info(f"Processing {len(unprocessed)} records...")
        
        # Convert to list of dicts
        records = unprocessed.to_dict('records')
        
        # Process sentiment
        processed = self.analyzer.process_records(records)
        
        # Load to BigQuery
        loaded = self.loader.load_processed_sentiment_data(processed)
        
        log.info(f"Processed and loaded {loaded} records")
        return loaded
    
    def process_all(self, max_batches: int = 10) -> int:
        """Process all unprocessed records in batches.
        
        Args:
            max_batches: Maximum number of batches to process
            
        Returns:
            Total number of records processed
        """
        total_processed = 0
        
        for batch_num in range(max_batches):
            processed = self.process_unprocessed_records()
            
            if processed == 0:
                break
            
            total_processed += processed
            log.info(f"Batch {batch_num + 1}: Processed {processed} records (Total: {total_processed})")
        
        return total_processed


def main():
    """Main function to process sentiment."""
    processor = SentimentProcessor()
    total = processor.process_all()
    log.info(f"Sentiment processing complete. Total records: {total}")


if __name__ == "__main__":
    main()
