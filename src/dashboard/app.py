"""Main dashboard application using Plotly Dash."""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
from src.dashboard.layouts import create_layout
from src.dashboard.callbacks import register_callbacks
from src.utils.config_loader import get_config
from src.utils.logger import log


class MentalHealthDashboard:
    """Mental Health Sentiment and Burnout Prediction Dashboard."""
    
    def __init__(self):
        """Initialize dashboard application."""
        self.config = get_config()
        dashboard_config = self.config.get_dashboard_config()
        
        # Initialize Dash app with Bootstrap theme
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            title="Mental Health Dashboard",
            suppress_callback_exceptions=True
        )
        
        # Set layout
        self.app.layout = create_layout()
        
        # Register callbacks
        register_callbacks(self.app)
        
        # Server configuration
        self.host = dashboard_config.get('host', '0.0.0.0')
        self.port = dashboard_config.get('port', 8050)
        self.debug = dashboard_config.get('debug', False)
        
        log.info("Dashboard initialized")
    
    def run(self):
        """Run the dashboard server."""
        log.info(f"Starting dashboard on {self.host}:{self.port}")
        self.app.run_server(
            host=self.host,
            port=self.port,
            debug=self.debug
        )


def main():
    """Main function to run dashboard."""
    dashboard = MentalHealthDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
