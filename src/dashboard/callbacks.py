"""Dashboard callbacks for interactivity."""

from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from src.dashboard.layouts import (
    create_overview_tab,
    create_sentiment_tab,
    create_burnout_tab,
    create_alerts_tab
)
from src.dashboard.data_provider import DashboardDataProvider
from src.dashboard.charts import ChartGenerator
from src.utils.logger import log


def register_callbacks(app):
    """Register all dashboard callbacks.
    
    Args:
        app: Dash application instance
    """
    data_provider = DashboardDataProvider()
    chart_gen = ChartGenerator()
    
    @app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'active_tab')
    )
    def render_tab_content(active_tab):
        """Render content based on active tab."""
        if active_tab == 'overview':
            return create_overview_tab()
        elif active_tab == 'sentiment':
            return create_sentiment_tab()
        elif active_tab == 'burnout':
            return create_burnout_tab()
        elif active_tab == 'alerts':
            return create_alerts_tab()
        return create_overview_tab()
    
    @app.callback(
        Output('last-updated', 'children'),
        [Input('interval-component', 'n_intervals'),
         Input('refresh-button', 'n_clicks')]
    )
    def update_timestamp(n_intervals, n_clicks):
        """Update last updated timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Overview tab callbacks
    @app.callback(
        [Output('users-count', 'children'),
         Output('high-risk-count', 'children'),
         Output('avg-sentiment', 'children'),
         Output('active-alerts', 'children')],
        [Input('interval-component', 'n_intervals'),
         Input('refresh-button', 'n_clicks'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_metrics(n_intervals, n_clicks, start_date, end_date):
        """Update key metrics."""
        try:
            metrics = data_provider.get_key_metrics(start_date, end_date)
            return (
                f"{metrics.get('total_users', 0):,}",
                f"{metrics.get('high_risk_users', 0):,}",
                f"{metrics.get('avg_sentiment', 0):.2f}",
                f"{metrics.get('active_alerts', 0):,}"
            )
        except Exception as e:
            log.error(f"Error updating metrics: {str(e)}")
            return "--", "--", "--", "--"
    
    @app.callback(
        Output('sentiment-trend-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('refresh-button', 'n_clicks'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('source-filter', 'value')]
    )
    def update_sentiment_trend(n_intervals, n_clicks, start_date, end_date, sources):
        """Update sentiment trend chart."""
        try:
            data = data_provider.get_sentiment_trend(start_date, end_date, sources)
            return chart_gen.create_sentiment_trend_chart(data)
        except Exception as e:
            log.error(f"Error updating sentiment trend: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('risk-distribution-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('refresh-button', 'n_clicks'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('risk-filter', 'value')]
    )
    def update_risk_distribution(n_intervals, n_clicks, start_date, end_date, risk_level):
        """Update risk distribution chart."""
        try:
            data = data_provider.get_risk_distribution(start_date, end_date, risk_level)
            return chart_gen.create_risk_distribution_chart(data)
        except Exception as e:
            log.error(f"Error updating risk distribution: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('indicators-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('refresh-button', 'n_clicks'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_indicators(n_intervals, n_clicks, start_date, end_date):
        """Update mental health indicators chart."""
        try:
            data = data_provider.get_mental_health_indicators(start_date, end_date)
            return chart_gen.create_indicators_chart(data)
        except Exception as e:
            log.error(f"Error updating indicators: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    # Sentiment tab callbacks
    @app.callback(
        Output('sentiment-distribution-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('sentiment-filter', 'value')]
    )
    def update_sentiment_distribution(n_intervals, start_date, end_date, sentiment_label):
        """Update sentiment distribution chart."""
        try:
            data = data_provider.get_sentiment_distribution(start_date, end_date, sentiment_label)
            return chart_gen.create_sentiment_distribution_chart(data)
        except Exception as e:
            log.error(f"Error updating sentiment distribution: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('sentiment-by-source-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_sentiment_by_source(n_intervals, start_date, end_date):
        """Update sentiment by source chart."""
        try:
            data = data_provider.get_sentiment_by_source(start_date, end_date)
            return chart_gen.create_sentiment_by_source_chart(data)
        except Exception as e:
            log.error(f"Error updating sentiment by source: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('keyword-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_keyword_chart(n_intervals, start_date, end_date):
        """Update keyword analysis chart."""
        try:
            data = data_provider.get_keyword_analysis(start_date, end_date)
            return chart_gen.create_keyword_chart(data)
        except Exception as e:
            log.error(f"Error updating keyword chart: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    # Burnout tab callbacks
    @app.callback(
        Output('burnout-heatmap', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('risk-filter', 'value')]
    )
    def update_burnout_heatmap(n_intervals, start_date, end_date, risk_level):
        """Update burnout risk heatmap."""
        try:
            data = data_provider.get_burnout_heatmap_data(start_date, end_date, risk_level)
            return chart_gen.create_burnout_heatmap(data)
        except Exception as e:
            log.error(f"Error updating burnout heatmap: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('risk-score-distribution', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_risk_score_distribution(n_intervals, start_date, end_date):
        """Update risk score distribution."""
        try:
            data = data_provider.get_risk_scores(start_date, end_date)
            return chart_gen.create_risk_score_distribution(data)
        except Exception as e:
            log.error(f"Error updating risk score distribution: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    @app.callback(
        Output('contributing-factors-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_contributing_factors(n_intervals, start_date, end_date):
        """Update contributing factors chart."""
        try:
            data = data_provider.get_contributing_factors(start_date, end_date)
            return chart_gen.create_contributing_factors_chart(data)
        except Exception as e:
            log.error(f"Error updating contributing factors: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
    
    # Alerts tab callbacks
    @app.callback(
        Output('alert-timeline-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_alert_timeline(n_intervals, start_date, end_date):
        """Update alert timeline chart."""
        try:
            data = data_provider.get_alert_timeline(start_date, end_date)
            return chart_gen.create_alert_timeline_chart(data)
        except Exception as e:
            log.error(f"Error updating alert timeline: {str(e)}")
            return chart_gen.create_empty_chart("Error loading data")
