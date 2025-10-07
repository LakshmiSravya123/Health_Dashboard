"""Data provider for dashboard queries."""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from src.etl.loaders.database_loader import get_loader
from src.utils.logger import log


class DashboardDataProvider:
    """Provide data for dashboard visualizations."""
    
    def __init__(self):
        """Initialize data provider."""
        self.loader = get_loader()
    
    def get_key_metrics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get key metrics for overview.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Dictionary of metrics
        """
        try:
            # Total users
            total_users = self._query_total_users(start_date, end_date)
            
            # High risk users
            high_risk = self._query_high_risk_users(start_date, end_date)
            
            # Average sentiment
            avg_sentiment = self._query_avg_sentiment(start_date, end_date)
            
            # Active alerts
            active_alerts = self._query_active_alerts(start_date, end_date)
            
            return {
                'total_users': total_users,
                'high_risk_users': high_risk,
                'avg_sentiment': avg_sentiment,
                'active_alerts': active_alerts
            }
        except Exception as e:
            log.error(f"Error getting key metrics: {str(e)}")
            return {
                'total_users': 0,
                'high_risk_users': 0,
                'avg_sentiment': 0,
                'active_alerts': 0
            }
    
    def get_sentiment_trend(
        self,
        start_date: str,
        end_date: str,
        sources: List[str] = None
    ) -> pd.DataFrame:
        """Get sentiment trend over time.
        
        Args:
            start_date: Start date
            end_date: End date
            sources: List of data sources to include
            
        Returns:
            DataFrame with sentiment trend data
        """
        sources_filter = ""
        if sources:
            sources_str = "', '".join(sources)
            sources_filter = f"AND r.source IN ('{sources_str}')"
        
        sql = f"""
        SELECT
            DATE(p.timestamp) as date,
            AVG(p.sentiment_score) as avg_sentiment,
            COUNT(*) as post_count
        FROM processed_sentiment_data p
        JOIN raw_sentiment_data r ON p.record_id = r.record_id
        WHERE DATE(p.timestamp) BETWEEN '{start_date}' AND '{end_date}'
            {sources_filter}
        GROUP BY date
        ORDER BY date
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting sentiment trend: {str(e)}")
            return pd.DataFrame()
    
    def get_risk_distribution(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get distribution of risk levels.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with risk distribution
        """
        sql = f"""
        SELECT
            risk_level,
            COUNT(*) as count
        FROM burnout_predictions
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY risk_level
        ORDER BY
            CASE risk_level
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting risk distribution: {str(e)}")
            return pd.DataFrame()
    
    def get_mental_health_indicators(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get mental health indicators over time.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with indicator trends
        """
        # Simplified - returns empty for now (JSON parsing complex in SQLite)
        # TODO: Implement JSON parsing for SQLite if needed
        try:
            return pd.DataFrame(columns=['date', 'stress', 'anxiety', 'depression', 'burnout'])
        except Exception as e:
            log.error(f"Error getting mental health indicators: {str(e)}")
            return pd.DataFrame()
    
    def get_sentiment_distribution(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get sentiment label distribution.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with sentiment distribution
        """
        sql = f"""
        SELECT
            sentiment_label,
            COUNT(*) as count
        FROM processed_sentiment_data
        WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY sentiment_label
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting sentiment distribution: {str(e)}")
            return pd.DataFrame()
    
    def get_sentiment_by_source(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get sentiment by data source.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with sentiment by source
        """
        sql = f"""
        SELECT
            r.source,
            AVG(p.sentiment_score) as avg_sentiment,
            COUNT(*) as count
        FROM processed_sentiment_data p
        JOIN raw_sentiment_data r ON p.record_id = r.record_id
        WHERE DATE(p.timestamp) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY r.source
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting sentiment by source: {str(e)}")
            return pd.DataFrame()
    
    def get_keyword_analysis(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get keyword frequency analysis.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with keyword counts
        """
        # Simplified - keywords stored as JSON string in SQLite
        # Return empty for now
        try:
            return pd.DataFrame(columns=['keyword', 'count'])
        except Exception as e:
            log.error(f"Error getting keyword analysis: {str(e)}")
            return pd.DataFrame()
    
    def get_burnout_heatmap_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get burnout risk data for heatmap.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with burnout risk by date and user
        """
        sql = f"""
        SELECT
            DATE(prediction_date) as date,
            user_id_hash,
            burnout_risk_score,
            risk_level
        FROM {self.loader.project_id}.{self.loader.dataset_id}.burnout_predictions
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date, burnout_risk_score DESC
        LIMIT 1000
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting burnout heatmap data: {str(e)}")
            return pd.DataFrame()
    
    def get_risk_scores(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get burnout risk scores.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with risk scores
        """
        sql = f"""
        SELECT burnout_risk_score
        FROM {self.loader.project_id}.{self.loader.dataset_id}.burnout_predictions
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting risk scores: {str(e)}")
            return pd.DataFrame()
    
    def get_contributing_factors(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get top contributing factors to burnout.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with contributing factors
        """
        # This would need to aggregate from the nested contributing_factors field
        # Simplified version for demonstration
        sql = f"""
        SELECT
            factor.factor_name,
            AVG(factor.importance_score) as avg_importance
        FROM {self.loader.project_id}.{self.loader.dataset_id}.burnout_predictions,
        UNNEST(contributing_factors) as factor
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY factor.factor_name
        ORDER BY avg_importance DESC
        LIMIT 10
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting contributing factors: {str(e)}")
            return pd.DataFrame()
    
    def get_alert_timeline(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get alert timeline data.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with alert timeline
        """
        sql = f"""
        SELECT
            DATE(alert_timestamp) as date,
            severity,
            COUNT(*) as count
        FROM {self.loader.project_id}.{self.loader.dataset_id}.alert_history
        WHERE DATE(alert_timestamp) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date, severity
        ORDER BY date
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting alert timeline: {str(e)}")
            return pd.DataFrame()
    
    def _query_total_users(self, start_date: str, end_date: str) -> int:
        """Query total unique users."""
        sql = f"""
        SELECT COUNT(DISTINCT user_id_hash) as count
        FROM {self.loader.project_id}.{self.loader.dataset_id}.processed_sentiment_data
        WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'
        """
        
        try:
            result = self.loader.query(sql)
            return int(result.iloc[0]['count']) if not result.empty else 0
        except:
            return 0
    
    def _query_high_risk_users(self, start_date: str, end_date: str) -> int:
        """Query high risk users count."""
        sql = f"""
        SELECT COUNT(DISTINCT user_id_hash) as count
        FROM {self.loader.project_id}.{self.loader.dataset_id}.burnout_predictions
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
            AND risk_level IN ('high', 'critical')
        """
        
        try:
            result = self.loader.query(sql)
            return int(result.iloc[0]['count']) if not result.empty else 0
        except:
            return 0
    
    def _query_avg_sentiment(self, start_date: str, end_date: str) -> float:
        """Query average sentiment score."""
        sql = f"""
        SELECT AVG(sentiment_score) as avg_score
        FROM {self.loader.project_id}.{self.loader.dataset_id}.processed_sentiment_data
        WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'
        """
        
        try:
            result = self.loader.query(sql)
            return float(result.iloc[0]['avg_score']) if not result.empty else 0.0
        except:
            return 0.0
    
    def _query_active_alerts(self, start_date: str, end_date: str) -> int:
        """Query active alerts count."""
        sql = f"""
        SELECT COUNT(*) as count
        FROM {self.loader.project_id}.{self.loader.dataset_id}.alert_history
        WHERE DATE(alert_timestamp) BETWEEN '{start_date}' AND '{end_date}'
            AND status = 'sent'
        """
        
        try:
            result = self.loader.query(sql)
            return int(result.iloc[0]['count']) if not result.empty else 0
        except:
            return 0
