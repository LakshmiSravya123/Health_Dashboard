"""Data provider for dashboard queries."""

import json
from collections import Counter
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
            substr(p.timestamp, 1, 10) as date,
            AVG(p.sentiment_score) as avg_sentiment,
            COUNT(*) as post_count
        FROM processed_sentiment_data p
        JOIN raw_sentiment_data r ON p.record_id = r.record_id
        WHERE p.timestamp >= '{start_date} 00:00:00' AND p.timestamp <= '{end_date} 23:59:59'
            {sources_filter}
        GROUP BY date
        ORDER BY date
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting sentiment trend: {str(e)}")
            return pd.DataFrame()
    
    def get_risk_distribution(self, start_date: str, end_date: str, risk_level: str = 'all') -> pd.DataFrame:
        """Get distribution of risk levels.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with risk distribution
        """
        risk_filter = "" if (not risk_level or risk_level == 'all') else f"AND risk_level = '{risk_level}'"
        sql = f"""
        SELECT
            risk_level,
            COUNT(*) as count
        FROM burnout_predictions
        WHERE prediction_date >= '{start_date}' AND prediction_date <= '{end_date}'
            {risk_filter}
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
        """Get mental health indicators over time (SQLite-friendly).
        
        We pull rows and aggregate in Python by parsing JSON strings from
        `mental_health_indicators`.
        """
        sql = f"""
        SELECT substr(timestamp, 1, 10) AS date, mental_health_indicators
        FROM processed_sentiment_data
        WHERE timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'
        ORDER BY date
        """
        try:
            df = self.loader.query(sql)
            if df.empty:
                return pd.DataFrame()
            # Parse JSON safely
            def parse_ind(row):
                v = row
                if isinstance(v, dict):
                    return v
                if isinstance(v, str) and v:
                    try:
                        parsed = json.loads(v)
                        # Only accept object (dict); otherwise fallback to empty dict
                        return parsed if isinstance(parsed, dict) else {}
                    except Exception:
                        return {}
                # Any other type (float/None/etc.) -> empty dict
                return {}
            df['parsed'] = df['mental_health_indicators'].apply(parse_ind)
            # Build aggregate per date
            agg = (
                df.groupby('date')['parsed']
                .apply(lambda xs: {
                    'stress': pd.Series([
                        x.get('stress_score', 0) if isinstance(x, dict) else 0 for x in xs
                    ]).mean() if len(xs) else 0,
                    'anxiety': pd.Series([
                        x.get('anxiety_score', 0) if isinstance(x, dict) else 0 for x in xs
                    ]).mean() if len(xs) else 0,
                    'depression': pd.Series([
                        x.get('depression_score', 0) if isinstance(x, dict) else 0 for x in xs
                    ]).mean() if len(xs) else 0,
                    'burnout': pd.Series([
                        x.get('burnout_score', 0) if isinstance(x, dict) else 0 for x in xs
                    ]).mean() if len(xs) else 0,
                })
                .reset_index(name='vals')
            )
            # Expand dict into columns with robust guards
            def _safe(d, key):
                if isinstance(d, dict):
                    return d.get(key, 0)
                return 0
            out = pd.concat([
                agg['date'],
                agg['vals'].apply(lambda d: _safe(d, 'stress')),
                agg['vals'].apply(lambda d: _safe(d, 'anxiety')),
                agg['vals'].apply(lambda d: _safe(d, 'depression')),
                agg['vals'].apply(lambda d: _safe(d, 'burnout')),
            ], axis=1)
            out.columns = ['date', 'stress', 'anxiety', 'depression', 'burnout']
            return out
        except Exception as e:
            log.error(f"Error getting mental health indicators: {str(e)}")
            return pd.DataFrame()
    
    def get_sentiment_distribution(
        self,
        start_date: str,
        end_date: str,
        sentiment_label: str = 'all'
    ) -> pd.DataFrame:
        """Get sentiment label distribution.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with sentiment distribution
        """
        sentiment_filter = "" if (not sentiment_label or sentiment_label == 'all') else f"AND sentiment_label = '{sentiment_label}'"
        sql = f"""
        SELECT
            sentiment_label,
            COUNT(*) as count
        FROM processed_sentiment_data
        WHERE timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'
            {sentiment_filter}
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
        WHERE p.timestamp >= '{start_date} 00:00:00' AND p.timestamp <= '{end_date} 23:59:59'
        GROUP BY r.source
        """
        
        try:
            return self.loader.query(sql)
        except Exception as e:
            log.error(f"Error getting sentiment by source: {str(e)}")
            return pd.DataFrame()
    
    def get_keyword_analysis(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get keyword frequency analysis (SQLite-friendly)."""
        sql = f"""
        SELECT keywords_detected
        FROM processed_sentiment_data
        WHERE timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'
        """
        try:
            df = self.loader.query(sql)
            if df.empty:
                return pd.DataFrame()
            all_keywords = []
            for val in df['keywords_detected']:
                if isinstance(val, list):
                    all_keywords.extend(val)
                elif isinstance(val, str):
                    # Try JSON first
                    parsed = None
                    try:
                        parsed = json.loads(val)
                    except Exception:
                        parsed = None
                    if isinstance(parsed, list):
                        all_keywords.extend([str(x) for x in parsed])
                    else:
                        # Fallback: comma-separated string
                        parts = [p.strip() for p in val.split(',') if p.strip()]
                        all_keywords.extend(parts)
            if not all_keywords:
                return pd.DataFrame()
            counts = Counter([k.lower() for k in all_keywords if k])
            top = counts.most_common(20)
            return pd.DataFrame(top, columns=['keyword', 'count'])
        except Exception as e:
            log.error(f"Error getting keyword analysis: {str(e)}")
            return pd.DataFrame()
    
    def get_burnout_heatmap_data(
        self,
        start_date: str,
        end_date: str,
        risk_level: str = 'all'
    ) -> pd.DataFrame:
        """Get burnout risk data for heatmap.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with burnout risk by date and user
        """
        risk_filter = "" if (not risk_level or risk_level == 'all') else f"AND risk_level = '{risk_level}'"
        sql = f"""
        SELECT
            prediction_date as date,
            user_id_hash,
            burnout_risk_score,
            risk_level
        FROM burnout_predictions
        WHERE prediction_date >= '{start_date}' AND prediction_date <= '{end_date}'
            {risk_filter}
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
        FROM burnout_predictions
        WHERE prediction_date >= '{start_date}' AND prediction_date <= '{end_date}'
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
        """Get top contributing factors to burnout (SQLite-friendly).
        
        Reads `contributing_factors` as JSON array per row and aggregates
        average importance per factor.
        """
        sql = f"""
        SELECT contributing_factors
        FROM burnout_predictions
        WHERE DATE(prediction_date) BETWEEN '{start_date}' AND '{end_date}'
        """
        try:
            df = self.loader.query(sql)
            if df.empty:
                return pd.DataFrame()
            bag = {}
            cnt = {}
            for val in df['contributing_factors']:
                items = None
                if isinstance(val, list):
                    items = val
                elif isinstance(val, str) and val:
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, list):
                            items = parsed
                    except Exception:
                        items = None
                if not items:
                    continue
                for it in items:
                    if isinstance(it, dict):
                        name = it.get('factor_name') or it.get('name')
                        imp = it.get('importance_score') or it.get('importance') or 0
                        if not name:
                            continue
                        bag[name] = bag.get(name, 0) + float(imp)
                        cnt[name] = cnt.get(name, 0) + 1
            if not bag:
                return pd.DataFrame()
            data = [
                {'factor_name': k, 'avg_importance': bag[k] / max(1, cnt.get(k, 1))}
                for k in bag.keys()
            ]
            out = pd.DataFrame(data).sort_values('avg_importance', ascending=False).head(10)
            return out
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
            substr(alert_timestamp, 1, 10) as date,
            severity,
            COUNT(*) as count
        FROM alert_history
        WHERE alert_timestamp >= '{start_date} 00:00:00' AND alert_timestamp <= '{end_date} 23:59:59'
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
        FROM processed_sentiment_data
        WHERE timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'
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
        FROM burnout_predictions
        WHERE prediction_date >= '{start_date}' AND prediction_date <= '{end_date}'
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
        FROM processed_sentiment_data
        WHERE timestamp >= '{start_date} 00:00:00' AND timestamp <= '{end_date} 23:59:59'
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
        FROM alert_history
        WHERE alert_timestamp >= '{start_date} 00:00:00' AND alert_timestamp <= '{end_date} 23:59:59'
            AND status = 'sent'
        """
        
        try:
            result = self.loader.query(sql)
            return int(result.iloc[0]['count']) if not result.empty else 0
        except:
            return 0
