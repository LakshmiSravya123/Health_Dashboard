"""Feature engineering for burnout prediction."""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.etl.loaders.bigquery_loader import BigQueryLoader
from src.utils.config_loader import get_config
from src.utils.logger import log


class FeatureEngineer:
    """Engineer features for burnout prediction."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.config = get_config()
        self.loader = BigQueryLoader()
        
        burnout_config = self.config.get_burnout_config()
        self.lookback_window = burnout_config.get('lookback_window', 30)
        self.feature_names = burnout_config.get('features', [])
    
    def compute_user_features(
        self,
        user_id_hash: str,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Compute features for a single user.
        
        Args:
            user_id_hash: Anonymized user ID
            end_date: End date for feature computation (default: now)
            
        Returns:
            Dictionary of computed features
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        start_date = end_date - timedelta(days=self.lookback_window)
        
        # Get user's sentiment data
        sentiment_data = self._get_user_sentiment_data(
            user_id_hash,
            start_date,
            end_date
        )
        
        if sentiment_data.empty:
            return self._empty_features(user_id_hash, end_date)
        
        # Compute features
        features = {
            'user_id_hash': user_id_hash,
            'feature_date': end_date.date().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Sentiment features
        features.update(self._compute_sentiment_features(sentiment_data))
        
        # Temporal features
        features.update(self._compute_temporal_features(sentiment_data))
        
        # Mental health indicator features
        features.update(self._compute_indicator_features(sentiment_data))
        
        return features
    
    def compute_all_user_features(
        self,
        end_date: datetime = None,
        min_posts: int = 3
    ) -> List[Dict[str, Any]]:
        """Compute features for all active users.
        
        Args:
            end_date: End date for feature computation
            min_posts: Minimum posts required to compute features
            
        Returns:
            List of feature dictionaries
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        start_date = end_date - timedelta(days=self.lookback_window)
        
        # Get all active users
        active_users = self._get_active_users(start_date, end_date, min_posts)
        
        log.info(f"Computing features for {len(active_users)} users")
        
        all_features = []
        for user_id_hash in active_users:
            try:
                features = self.compute_user_features(user_id_hash, end_date)
                all_features.append(features)
            except Exception as e:
                log.error(f"Error computing features for user {user_id_hash}: {str(e)}")
        
        log.info(f"Computed features for {len(all_features)} users")
        return all_features
    
    def _get_user_sentiment_data(
        self,
        user_id_hash: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Get sentiment data for a user within date range.
        
        Args:
            user_id_hash: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame of sentiment data
        """
        tables = self.loader.tables
        processed_table = tables.get('processed_sentiment', 'processed_sentiment_data')
        
        sql = f"""
        SELECT
            timestamp,
            sentiment_score,
            sentiment_label,
            mental_health_indicators
        FROM `{self.loader.project_id}.{self.loader.dataset_id}.{processed_table}`
        WHERE user_id_hash = '{user_id_hash}'
            AND timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
        ORDER BY timestamp
        """
        
        return self.loader.query(sql)
    
    def _get_active_users(
        self,
        start_date: datetime,
        end_date: datetime,
        min_posts: int
    ) -> List[str]:
        """Get list of active users.
        
        Args:
            start_date: Start date
            end_date: End date
            min_posts: Minimum number of posts
            
        Returns:
            List of user ID hashes
        """
        tables = self.loader.tables
        processed_table = tables.get('processed_sentiment', 'processed_sentiment_data')
        
        sql = f"""
        SELECT user_id_hash
        FROM `{self.loader.project_id}.{self.loader.dataset_id}.{processed_table}`
        WHERE timestamp BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
        GROUP BY user_id_hash
        HAVING COUNT(*) >= {min_posts}
        """
        
        df = self.loader.query(sql)
        return df['user_id_hash'].tolist()
    
    def _compute_sentiment_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute sentiment-based features.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Overall sentiment statistics
        features['avg_sentiment_7d'] = self._rolling_mean(df, 7)
        features['avg_sentiment_30d'] = df['sentiment_score'].mean()
        features['sentiment_volatility'] = df['sentiment_score'].std()
        
        # Negative post frequency
        features['negative_post_count_7d'] = self._count_negative_posts(df, 7)
        
        # Post frequency
        days_active = (df['timestamp'].max() - df['timestamp'].min()).days + 1
        features['post_frequency'] = len(df) / max(days_active, 1)
        
        # Sentiment trend
        features['sentiment_trend_7d'] = self._compute_trend(df, 7)
        
        # Engagement level (simplified - based on post frequency and consistency)
        features['engagement_level'] = min(features['post_frequency'] / 2.0, 1.0)
        
        return features
    
    def _compute_temporal_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute temporal pattern features.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Weekend activity ratio
        weekend_posts = len(df[df['day_of_week'].isin([5, 6])])
        weekday_posts = len(df[~df['day_of_week'].isin([5, 6])])
        features['weekend_activity_ratio'] = weekend_posts / max(weekday_posts, 1)
        
        # Late night activity (11pm - 5am)
        late_night_posts = len(df[(df['hour'] >= 23) | (df['hour'] <= 5)])
        features['late_night_activity_pct'] = late_night_posts / len(df) if len(df) > 0 else 0
        
        return features
    
    def _compute_indicator_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute mental health indicator features.
        
        Args:
            df: DataFrame with sentiment data
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Extract indicator scores from JSON column
        indicators = ['stress', 'anxiety', 'depression', 'burnout']
        
        for indicator in indicators:
            scores = []
            for _, row in df.iterrows():
                if pd.notna(row['mental_health_indicators']):
                    indicator_data = row['mental_health_indicators']
                    if isinstance(indicator_data, dict):
                        score = indicator_data.get(f'{indicator}_score', 0)
                        scores.append(score)
            
            avg_score = np.mean(scores) if scores else 0
            features[f'{indicator}_indicator_avg'] = round(avg_score, 3)
        
        return features
    
    def _rolling_mean(self, df: pd.DataFrame, days: int) -> float:
        """Compute rolling mean for last N days.
        
        Args:
            df: DataFrame with sentiment data
            days: Number of days for rolling window
            
        Returns:
            Rolling mean value
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = df['timestamp'].max() - pd.Timedelta(days=days)
        recent = df[df['timestamp'] >= cutoff]
        return recent['sentiment_score'].mean() if len(recent) > 0 else df['sentiment_score'].mean()
    
    def _count_negative_posts(self, df: pd.DataFrame, days: int) -> int:
        """Count negative posts in last N days.
        
        Args:
            df: DataFrame with sentiment data
            days: Number of days to look back
            
        Returns:
            Count of negative posts
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = df['timestamp'].max() - pd.Timedelta(days=days)
        recent = df[df['timestamp'] >= cutoff]
        return len(recent[recent['sentiment_label'].isin(['negative', 'very_negative'])])
    
    def _compute_trend(self, df: pd.DataFrame, days: int) -> float:
        """Compute sentiment trend (slope) for last N days.
        
        Args:
            df: DataFrame with sentiment data
            days: Number of days for trend calculation
            
        Returns:
            Trend slope
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = df['timestamp'].max() - pd.Timedelta(days=days)
        recent = df[df['timestamp'] >= cutoff]
        
        if len(recent) < 2:
            return 0.0
        
        # Simple linear regression
        x = np.arange(len(recent))
        y = recent['sentiment_score'].values
        slope = np.polyfit(x, y, 1)[0]
        
        return round(slope, 4)
    
    def _empty_features(self, user_id_hash: str, end_date: datetime) -> Dict[str, Any]:
        """Return empty features for users with no data.
        
        Args:
            user_id_hash: User ID
            end_date: Feature date
            
        Returns:
            Dictionary with null features
        """
        return {
            'user_id_hash': user_id_hash,
            'feature_date': end_date.date().isoformat(),
            'avg_sentiment_7d': None,
            'avg_sentiment_30d': None,
            'sentiment_volatility': None,
            'negative_post_count_7d': None,
            'post_frequency': None,
            'engagement_level': None,
            'stress_indicator_avg': None,
            'anxiety_indicator_avg': None,
            'depression_indicator_avg': None,
            'burnout_indicator_avg': None,
            'weekend_activity_ratio': None,
            'late_night_activity_pct': None,
            'sentiment_trend_7d': None,
            'last_updated': datetime.utcnow().isoformat()
        }
