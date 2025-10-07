"""Chart generation for dashboard visualizations."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any
from src.utils.config_loader import get_config


class ChartGenerator:
    """Generate charts for dashboard."""
    
    def __init__(self):
        """Initialize chart generator."""
        self.config = get_config()
        dashboard_config = self.config.get_dashboard_config()
        
        self.theme = dashboard_config.get('theme', 'plotly_white')
        self.colors = dashboard_config.get('color_scheme', {})
    
    def create_sentiment_trend_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment trend line chart.
        
        Args:
            df: DataFrame with date and avg_sentiment columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No sentiment data available")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['avg_sentiment'],
            mode='lines+markers',
            name='Average Sentiment',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))
        
        # Add reference line at 0.5 (neutral)
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                      annotation_text="Neutral")
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Date",
            yaxis_title="Sentiment Score",
            yaxis_range=[0, 1],
            hovermode='x unified',
            showlegend=False
        )
        
        return fig
    
    def create_risk_distribution_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create risk distribution pie chart.
        
        Args:
            df: DataFrame with risk_level and count columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No risk data available")
        
        color_map = {
            'critical': self.colors.get('critical', '#d32f2f'),
            'high': self.colors.get('high', '#f57c00'),
            'medium': self.colors.get('medium', '#fbc02d'),
            'low': self.colors.get('low', '#388e3c')
        }
        
        colors = [color_map.get(level, '#757575') for level in df['risk_level']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df['risk_level'].str.title(),
            values=df['count'],
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            template=self.theme,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        
        return fig
    
    def create_indicators_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create mental health indicators chart.
        
        Args:
            df: DataFrame with date and indicator columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No indicator data available")
        
        fig = go.Figure()
        
        indicators = ['stress', 'anxiety', 'depression', 'burnout']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        for indicator, color in zip(indicators, colors):
            if indicator in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df[indicator],
                    mode='lines',
                    name=indicator.title(),
                    line=dict(color=color, width=2)
                ))
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Date",
            yaxis_title="Indicator Score",
            yaxis_range=[0, 1],
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_sentiment_distribution_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment distribution bar chart.
        
        Args:
            df: DataFrame with sentiment_label and count columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No sentiment data available")
        
        color_map = {
            'very_negative': '#d32f2f',
            'negative': '#f57c00',
            'neutral': '#757575',
            'positive': '#66bb6a',
            'very_positive': '#388e3c'
        }
        
        colors = [color_map.get(label, '#757575') for label in df['sentiment_label']]
        
        fig = go.Figure(data=[go.Bar(
            x=df['sentiment_label'].str.replace('_', ' ').str.title(),
            y=df['count'],
            marker_color=colors,
            text=df['count'],
            textposition='outside'
        )])
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Sentiment",
            yaxis_title="Count",
            showlegend=False
        )
        
        return fig
    
    def create_sentiment_by_source_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment by source bar chart.
        
        Args:
            df: DataFrame with source and avg_sentiment columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No source data available")
        
        fig = go.Figure(data=[go.Bar(
            x=df['source'].str.title(),
            y=df['avg_sentiment'],
            marker_color='#2E86AB',
            text=df['avg_sentiment'].round(2),
            textposition='outside'
        )])
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Data Source",
            yaxis_title="Average Sentiment",
            yaxis_range=[0, 1],
            showlegend=False
        )
        
        return fig
    
    def create_keyword_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create keyword frequency bar chart.
        
        Args:
            df: DataFrame with keyword and count columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No keyword data available")
        
        fig = go.Figure(data=[go.Bar(
            y=df['keyword'],
            x=df['count'],
            orientation='h',
            marker_color='#FF6B6B',
            text=df['count'],
            textposition='outside'
        )])
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Frequency",
            yaxis_title="Keyword",
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_burnout_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create burnout risk heatmap.
        
        Args:
            df: DataFrame with date, user_id_hash, and burnout_risk_score
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No burnout data available")
        
        # Pivot data for heatmap
        pivot = df.pivot_table(
            index='user_id_hash',
            columns='date',
            values='burnout_risk_score',
            aggfunc='mean'
        )
        
        # Limit to top 20 users by average risk
        if len(pivot) > 20:
            pivot = pivot.nlargest(20, pivot.columns[-1])
        
        # Anonymize user IDs for display
        pivot.index = [f"User {i+1}" for i in range(len(pivot))]
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='RdYlGn_r',
            zmid=0.5,
            text=pivot.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Risk Score")
        ))
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Date",
            yaxis_title="User",
            height=600
        )
        
        return fig
    
    def create_risk_score_distribution(self, df: pd.DataFrame) -> go.Figure:
        """Create risk score histogram.
        
        Args:
            df: DataFrame with burnout_risk_score column
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No risk score data available")
        
        fig = go.Figure(data=[go.Histogram(
            x=df['burnout_risk_score'],
            nbinsx=20,
            marker_color='#FF6B6B',
            opacity=0.7
        )])
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Burnout Risk Score",
            yaxis_title="Frequency",
            showlegend=False
        )
        
        return fig
    
    def create_contributing_factors_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create contributing factors bar chart.
        
        Args:
            df: DataFrame with factor_name and avg_importance columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No factor data available")
        
        fig = go.Figure(data=[go.Bar(
            y=df['factor_name'].str.replace('_', ' ').str.title(),
            x=df['avg_importance'],
            orientation='h',
            marker_color='#4ECDC4',
            text=df['avg_importance'].round(3),
            textposition='outside'
        )])
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Importance Score",
            yaxis_title="Factor",
            showlegend=False
        )
        
        return fig
    
    def create_alert_timeline_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create alert timeline stacked bar chart.
        
        Args:
            df: DataFrame with date, severity, and count columns
            
        Returns:
            Plotly figure
        """
        if df.empty:
            return self.create_empty_chart("No alert data available")
        
        fig = go.Figure()
        
        severities = ['critical', 'high', 'medium', 'low']
        colors = {
            'critical': self.colors.get('critical', '#d32f2f'),
            'high': self.colors.get('high', '#f57c00'),
            'medium': self.colors.get('medium', '#fbc02d'),
            'low': self.colors.get('low', '#388e3c')
        }
        
        for severity in severities:
            severity_data = df[df['severity'] == severity]
            if not severity_data.empty:
                fig.add_trace(go.Bar(
                    x=severity_data['date'],
                    y=severity_data['count'],
                    name=severity.title(),
                    marker_color=colors.get(severity, '#757575')
                ))
        
        fig.update_layout(
            template=self.theme,
            xaxis_title="Date",
            yaxis_title="Alert Count",
            barmode='stack',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_empty_chart(self, message: str = "No data available") -> go.Figure:
        """Create empty chart with message.
        
        Args:
            message: Message to display
            
        Returns:
            Empty Plotly figure
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            template=self.theme,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        
        return fig
