"""Lightweight CSV-based data provider for Vercel deployment."""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class VercelDataProvider:
    """Provide data from precomputed CSVs for Vercel serverless."""
    
    def __init__(self):
        """Initialize with CSV paths."""
        self.data_dir = PROJECT_ROOT / "data"
        self.sentiment_csv = self.data_dir / "demo_sentiment.csv"
        self.predictions_csv = self.data_dir / "demo_predictions.csv"
        self.alerts_csv = self.data_dir / "demo_alerts.csv"
        
        # Load CSVs once
        self._sentiment_df = None
        self._predictions_df = None
        self._alerts_df = None
    
    @property
    def sentiment_df(self):
        if self._sentiment_df is None:
            self._sentiment_df = pd.read_csv(self.sentiment_csv)
        return self._sentiment_df
    
    @property
    def predictions_df(self):
        if self._predictions_df is None:
            self._predictions_df = pd.read_csv(self.predictions_csv)
        return self._predictions_df
    
    @property
    def alerts_df(self):
        if self._alerts_df is None:
            self._alerts_df = pd.read_csv(self.alerts_csv)
        return self._alerts_df
    
    def get_key_metrics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get key metrics from CSVs."""
        df_s = self.sentiment_df
        df_p = self.predictions_df
        df_a = self.alerts_df
        
        # Filter by date
        df_s_filtered = df_s[(df_s['timestamp'] >= start_date) & (df_s['timestamp'] <= end_date)]
        df_p_filtered = df_p[(df_p['prediction_date'] >= start_date) & (df_p['prediction_date'] <= end_date)]
        df_a_filtered = df_a[(df_a['alert_timestamp'] >= start_date) & (df_a['alert_timestamp'] <= end_date)]
        
        return {
            'total_users': df_s_filtered['user_id_hash'].nunique() if not df_s_filtered.empty else 0,
            'high_risk_users': df_p_filtered[df_p_filtered['risk_level'].isin(['high', 'critical'])]['user_id_hash'].nunique() if not df_p_filtered.empty else 0,
            'avg_sentiment': df_s_filtered['sentiment_score'].mean() if not df_s_filtered.empty else 0.0,
            'active_alerts': len(df_a_filtered[df_a_filtered['status'] == 'sent']) if not df_a_filtered.empty else 0
        }
    
    def get_sentiment_trend(self, start_date: str, end_date: str, sources: List[str] = None) -> pd.DataFrame:
        """Get sentiment trend."""
        df = self.sentiment_df.copy()
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        agg = df.groupby('date').agg({'sentiment_score': 'mean', 'record_id': 'count'}).reset_index()
        agg.columns = ['date', 'avg_sentiment', 'post_count']
        return agg
    
    def get_risk_distribution(self, start_date: str, end_date: str, risk_level: str = 'all') -> pd.DataFrame:
        """Get risk distribution."""
        df = self.predictions_df.copy()
        df = df[(df['prediction_date'] >= start_date) & (df['prediction_date'] <= end_date)]
        if risk_level and risk_level != 'all':
            df = df[df['risk_level'] == risk_level]
        if df.empty:
            return pd.DataFrame()
        
        return df.groupby('risk_level').size().reset_index(name='count')
    
    def get_mental_health_indicators(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get mental health indicators (simplified for demo)."""
        df = self.sentiment_df.copy()
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        # Simplified: use sentiment as proxy for indicators
        agg = df.groupby('date')['sentiment_score'].mean().reset_index()
        agg['stress'] = (1 - agg['sentiment_score']) * 0.8
        agg['anxiety'] = (1 - agg['sentiment_score']) * 0.7
        agg['depression'] = (1 - agg['sentiment_score']) * 0.6
        agg['burnout'] = (1 - agg['sentiment_score']) * 0.5
        return agg[['date', 'stress', 'anxiety', 'depression', 'burnout']]
    
    def get_sentiment_distribution(self, start_date: str, end_date: str, sentiment_label: str = 'all') -> pd.DataFrame:
        """Get sentiment distribution."""
        df = self.sentiment_df.copy()
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        if sentiment_label and sentiment_label != 'all':
            df = df[df['sentiment_label'] == sentiment_label]
        if df.empty:
            return pd.DataFrame()
        
        return df.groupby('sentiment_label').size().reset_index(name='count')
    
    def get_sentiment_by_source(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get sentiment by source (demo: return empty)."""
        return pd.DataFrame(columns=['source', 'avg_sentiment', 'count'])
    
    def get_keyword_analysis(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get keyword analysis."""
        df = self.sentiment_df.copy()
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        if df.empty or 'keywords_detected' not in df.columns:
            return pd.DataFrame()
        
        all_keywords = []
        for val in df['keywords_detected'].dropna():
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        all_keywords.extend([str(x).lower() for x in parsed if x])
                except:
                    pass
        
        if not all_keywords:
            return pd.DataFrame()
        
        counts = Counter(all_keywords)
        top = counts.most_common(20)
        return pd.DataFrame(top, columns=['keyword', 'count'])
    
    def get_burnout_heatmap_data(self, start_date: str, end_date: str, risk_level: str = 'all') -> pd.DataFrame:
        """Get burnout heatmap data."""
        df = self.predictions_df.copy()
        df = df[(df['prediction_date'] >= start_date) & (df['prediction_date'] <= end_date)]
        if risk_level and risk_level != 'all':
            df = df[df['risk_level'] == risk_level]
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = df['prediction_date']
        return df[['date', 'user_id_hash', 'burnout_risk_score', 'risk_level']].head(1000)
    
    def get_risk_scores(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get risk scores."""
        df = self.predictions_df.copy()
        df = df[(df['prediction_date'] >= start_date) & (df['prediction_date'] <= end_date)]
        if df.empty:
            return pd.DataFrame()
        
        return df[['burnout_risk_score']]
    
    def get_contributing_factors(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get contributing factors (demo: return empty)."""
        return pd.DataFrame(columns=['factor_name', 'avg_importance'])
    
    def get_alert_timeline(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get alert timeline."""
        df = self.alerts_df.copy()
        df = df[(df['alert_timestamp'] >= start_date) & (df['alert_timestamp'] <= end_date)]
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['alert_timestamp']).dt.date
        return df.groupby(['date', 'severity']).size().reset_index(name='count')
