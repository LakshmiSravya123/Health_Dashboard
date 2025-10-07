"""SQLite data loader - 100% FREE local database."""

import sqlite3
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from src.utils.config_loader import get_config
from src.utils.logger import log


class SQLiteLoader:
    """Load data into SQLite database (free local option)."""
    
    def __init__(self):
        """Initialize SQLite loader."""
        self.config = get_config()
        sqlite_config = self.config.config.get('sqlite', {})
        
        self.db_path = sqlite_config.get('database_path', 'data/mental_health.db')
        self.tables = sqlite_config.get('tables', {})
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        log.info(f"Connected to SQLite database: {self.db_path}")
    
    def create_tables(self):
        """Create all required tables."""
        cursor = self.conn.cursor()
        
        # Raw sentiment data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_sentiment_data (
                record_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                source TEXT NOT NULL,
                text_content TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                ingestion_timestamp TEXT NOT NULL,
                language TEXT
            )
        ''')
        
        # Processed sentiment data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_sentiment_data (
                record_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sentiment_score REAL NOT NULL,
                sentiment_label TEXT NOT NULL,
                confidence REAL NOT NULL,
                mental_health_indicators TEXT,
                keywords_detected TEXT,
                processing_timestamp TEXT NOT NULL,
                model_version TEXT NOT NULL
            )
        ''')
        
        # User features table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_features (
                user_id_hash TEXT NOT NULL,
                feature_date TEXT NOT NULL,
                avg_sentiment_7d REAL,
                avg_sentiment_30d REAL,
                sentiment_volatility REAL,
                negative_post_count_7d INTEGER,
                post_frequency REAL,
                engagement_level REAL,
                stress_indicator_avg REAL,
                anxiety_indicator_avg REAL,
                depression_indicator_avg REAL,
                burnout_indicator_avg REAL,
                weekend_activity_ratio REAL,
                late_night_activity_pct REAL,
                sentiment_trend_7d REAL,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (user_id_hash, feature_date)
            )
        ''')
        
        # Burnout predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS burnout_predictions (
                prediction_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                prediction_timestamp TEXT NOT NULL,
                burnout_risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                confidence_interval TEXT,
                contributing_factors TEXT,
                prediction_horizon_days INTEGER NOT NULL,
                model_version TEXT NOT NULL,
                model_type TEXT NOT NULL
            )
        ''')
        
        # Alert history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                alert_id TEXT PRIMARY KEY,
                user_id_hash TEXT NOT NULL,
                alert_timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                trigger_condition TEXT NOT NULL,
                trigger_value REAL,
                channels_sent TEXT,
                status TEXT NOT NULL,
                acknowledged_timestamp TEXT,
                acknowledged_by TEXT,
                notes TEXT
            )
        ''')
        
        self.conn.commit()
        log.info("SQLite tables created successfully")
    
    def load(self, data: List[Dict[str, Any]], table_name: str) -> int:
        """Load data into SQLite table.
        
        Args:
            data: List of records to load
            table_name: Name of target table
            
        Returns:
            Number of rows loaded
        """
        if not data:
            log.warning(f"No data to load into {table_name}")
            return 0
        
        try:
            df = pd.DataFrame(data)
            
            # Convert complex types to JSON strings
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (dict, list)) else x)
            
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            
            log.info(f"Loaded {len(data)} rows into {table_name}")
            return len(data)
        
        except Exception as e:
            log.error(f"Error loading data into {table_name}: {str(e)}")
            raise
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute a query and return results as DataFrame.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Query results as DataFrame
        """
        try:
            df = pd.read_sql_query(sql, self.conn)
            return df
        except Exception as e:
            log.error(f"Error executing query: {str(e)}")
            raise
    
    def load_raw_sentiment_data(self, data: List[Dict[str, Any]]) -> int:
        """Load raw sentiment data."""
        return self.load(data, 'raw_sentiment_data')
    
    def load_processed_sentiment_data(self, data: List[Dict[str, Any]]) -> int:
        """Load processed sentiment data."""
        return self.load(data, 'processed_sentiment_data')
    
    def load_user_features(self, data: List[Dict[str, Any]]) -> int:
        """Load user features."""
        # Delete existing data for the same date
        if data:
            cursor = self.conn.cursor()
            for record in data:
                cursor.execute(
                    "DELETE FROM user_features WHERE user_id_hash = ? AND feature_date = ?",
                    (record.get('user_id_hash'), record.get('feature_date'))
                )
            self.conn.commit()
        
        return self.load(data, 'user_features')
    
    def load_burnout_predictions(self, data: List[Dict[str, Any]]) -> int:
        """Load burnout predictions."""
        return self.load(data, 'burnout_predictions')
    
    def load_alert_history(self, data: List[Dict[str, Any]]) -> int:
        """Load alert history."""
        return self.load(data, 'alert_history')
    
    def get_unprocessed_records(self, limit: int = 1000) -> pd.DataFrame:
        """Get raw records that haven't been processed yet."""
        sql = f"""
        SELECT r.*
        FROM raw_sentiment_data r
        LEFT JOIN processed_sentiment_data p ON r.record_id = p.record_id
        WHERE p.record_id IS NULL
        ORDER BY r.timestamp DESC
        LIMIT {limit}
        """
        return self.query(sql)
    
    def close(self):
        """Close database connection."""
        self.conn.close()
        log.info("SQLite connection closed")
