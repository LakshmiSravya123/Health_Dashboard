"""BigQuery data loader."""

from typing import List, Dict, Any
from datetime import datetime
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from src.utils.config_loader import get_config
from src.utils.logger import log


class BigQueryLoader:
    """Load data into BigQuery tables."""
    
    def __init__(self):
        """Initialize BigQuery loader."""
        self.config = get_config()
        bq_config = self.config.get_bigquery_config()
        
        self.project_id = bq_config.get('project_id')
        self.dataset_id = bq_config.get('dataset_id')
        self.tables = bq_config.get('tables', {})
        
        self.client = bigquery.Client(project=self.project_id)
    
    def load(
        self,
        data: List[Dict[str, Any]],
        table_name: str,
        write_disposition: str = 'WRITE_APPEND'
    ) -> int:
        """Load data into BigQuery table.
        
        Args:
            data: List of records to load
            table_name: Name of target table
            write_disposition: Write disposition (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
            
        Returns:
            Number of rows loaded
        """
        if not data:
            log.warning(f"No data to load into {table_name}")
            return 0
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Configure load job
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition,
                schema_update_options=[
                    bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                ]
            )
            
            # Load data
            job = self.client.load_table_from_dataframe(
                df,
                table_ref,
                job_config=job_config
            )
            
            # Wait for job to complete
            job.result()
            
            log.info(f"Loaded {len(data)} rows into {table_ref}")
            return len(data)
        
        except Exception as e:
            log.error(f"Error loading data into {table_ref}: {str(e)}")
            raise
    
    def load_raw_sentiment_data(self, data: List[Dict[str, Any]]) -> int:
        """Load raw sentiment data.
        
        Args:
            data: List of raw sentiment records
            
        Returns:
            Number of rows loaded
        """
        table_name = self.tables.get('raw_sentiment', 'raw_sentiment_data')
        return self.load(data, table_name)
    
    def load_processed_sentiment_data(self, data: List[Dict[str, Any]]) -> int:
        """Load processed sentiment data.
        
        Args:
            data: List of processed sentiment records
            
        Returns:
            Number of rows loaded
        """
        table_name = self.tables.get('processed_sentiment', 'processed_sentiment_data')
        return self.load(data, table_name)
    
    def load_user_features(self, data: List[Dict[str, Any]]) -> int:
        """Load user features.
        
        Args:
            data: List of user feature records
            
        Returns:
            Number of rows loaded
        """
        table_name = self.tables.get('user_features', 'user_features')
        return self.load(data, table_name, write_disposition='WRITE_TRUNCATE')
    
    def load_burnout_predictions(self, data: List[Dict[str, Any]]) -> int:
        """Load burnout predictions.
        
        Args:
            data: List of prediction records
            
        Returns:
            Number of rows loaded
        """
        table_name = self.tables.get('burnout_predictions', 'burnout_predictions')
        return self.load(data, table_name)
    
    def load_alert_history(self, data: List[Dict[str, Any]]) -> int:
        """Load alert history.
        
        Args:
            data: List of alert records
            
        Returns:
            Number of rows loaded
        """
        table_name = self.tables.get('alerts', 'alert_history')
        return self.load(data, table_name)
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute a query and return results as DataFrame.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Query results as DataFrame
        """
        try:
            query_job = self.client.query(sql)
            df = query_job.to_dataframe()
            return df
        except Exception as e:
            log.error(f"Error executing query: {str(e)}")
            raise
    
    def get_unprocessed_records(self, limit: int = 1000) -> pd.DataFrame:
        """Get raw records that haven't been processed yet.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            DataFrame of unprocessed records
        """
        raw_table = self.tables.get('raw_sentiment', 'raw_sentiment_data')
        processed_table = self.tables.get('processed_sentiment', 'processed_sentiment_data')
        
        sql = f"""
        SELECT r.*
        FROM `{self.project_id}.{self.dataset_id}.{raw_table}` r
        LEFT JOIN `{self.project_id}.{self.dataset_id}.{processed_table}` p
            ON r.record_id = p.record_id
        WHERE p.record_id IS NULL
        ORDER BY r.timestamp DESC
        LIMIT {limit}
        """
        
        return self.query(sql)
    
    def delete_old_records(self, table_name: str, days: int) -> int:
        """Delete records older than specified days.
        
        Args:
            table_name: Name of table to clean
            days: Delete records older than this many days
            
        Returns:
            Number of rows deleted
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        sql = f"""
        DELETE FROM `{table_ref}`
        WHERE timestamp < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """
        
        try:
            query_job = self.client.query(sql)
            query_job.result()
            
            rows_affected = query_job.num_dml_affected_rows
            log.info(f"Deleted {rows_affected} old records from {table_ref}")
            return rows_affected
        
        except Exception as e:
            log.error(f"Error deleting old records from {table_ref}: {str(e)}")
            raise
