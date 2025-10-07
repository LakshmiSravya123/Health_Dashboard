"""Dashboard layouts and UI components."""

from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta


def create_layout():
    """Create main dashboard layout.
    
    Returns:
        Dash layout component
    """
    return dbc.Container([
        # Header
        create_header(),
        
        html.Hr(),
        
        # Main content
        dbc.Row([
            # Sidebar with filters
            dbc.Col([
                create_sidebar()
            ], width=3),
            
            # Main dashboard area
            dbc.Col([
                # Tabs for different views
                dbc.Tabs([
                    dbc.Tab(label="Overview", tab_id="overview"),
                    dbc.Tab(label="Sentiment Analysis", tab_id="sentiment"),
                    dbc.Tab(label="Burnout Predictions", tab_id="burnout"),
                    dbc.Tab(label="Alerts", tab_id="alerts"),
                ], id="tabs", active_tab="overview"),
                
                html.Div(id="tab-content", className="mt-4")
            ], width=9)
        ]),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # 30 seconds
            n_intervals=0
        ),
        
        # Store for data
        dcc.Store(id='data-store'),
        
    ], fluid=True, className="p-4")


def create_header():
    """Create dashboard header.
    
    Returns:
        Header component
    """
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-brain me-3", style={'color': '#667eea'}),
                    "Mental Health Analytics"
                ], style={'color': '#2d3748', 'fontWeight': '700', 'marginBottom': '0.5rem'}),
                html.P(
                    "AI-powered sentiment analysis and burnout prediction for proactive mental health care",
                    style={'color': '#718096', 'fontSize': '1.1rem'}
                )
            ])
        ], width=8),
        dbc.Col([
            html.Div([
                html.P([
                    html.I(className="fas fa-clock me-2", style={'color': '#667eea'}),
                    html.Span(id="last-updated", children=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             style={'color': '#4a5568'})
                ], className="text-end mb-2"),
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Refresh Data"
                ], id="refresh-button", 
                   style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          'border': 'none',
                          'boxShadow': '0 4px 6px rgba(102, 126, 234, 0.4)'},
                   size="sm", className="float-end")
            ])
        ], width=4)
    ], style={'marginBottom': '2rem', 'padding': '1.5rem', 
              'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              'borderRadius': '15px',
              'boxShadow': '0 10px 25px rgba(0,0,0,0.1)'})


def create_sidebar():
    """Create sidebar with filters.
    
    Returns:
        Sidebar component
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Filters", className="mb-0")),
        dbc.CardBody([
            # Date range selector
            html.Label("Date Range", className="fw-bold"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=(datetime.now() - timedelta(days=30)).date(),
                end_date=datetime.now().date(),
                display_format='YYYY-MM-DD',
                className="mb-3"
            ),
            
            html.Hr(),
            
            # Risk level filter
            html.Label("Risk Level", className="fw-bold"),
            dcc.Dropdown(
                id='risk-filter',
                options=[
                    {'label': 'All Levels', 'value': 'all'},
                    {'label': 'Critical', 'value': 'critical'},
                    {'label': 'High', 'value': 'high'},
                    {'label': 'Medium', 'value': 'medium'},
                    {'label': 'Low', 'value': 'low'}
                ],
                value='all',
                className="mb-3"
            ),
            
            html.Hr(),
            
            # Sentiment filter
            html.Label("Sentiment", className="fw-bold"),
            dcc.Dropdown(
                id='sentiment-filter',
                options=[
                    {'label': 'All Sentiments', 'value': 'all'},
                    {'label': 'Very Positive', 'value': 'very_positive'},
                    {'label': 'Positive', 'value': 'positive'},
                    {'label': 'Neutral', 'value': 'neutral'},
                    {'label': 'Negative', 'value': 'negative'},
                    {'label': 'Very Negative', 'value': 'very_negative'}
                ],
                value='all',
                className="mb-3"
            ),
            
            html.Hr(),
            
            # Data source filter
            html.Label("Data Source", className="fw-bold"),
            dcc.Checklist(
                id='source-filter',
                options=[
                    {'label': ' Twitter', 'value': 'twitter'},
                    {'label': ' Reddit', 'value': 'reddit'},
                    {'label': ' Surveys', 'value': 'survey'}
                ],
                value=['twitter', 'reddit', 'survey'],
                className="mb-3"
            ),
        ])
    ], className="shadow-sm")


def create_overview_tab():
    """Create overview tab content.
    
    Returns:
        Overview tab component
    """
    return html.Div([
        # Key metrics cards
        dbc.Row([
            dbc.Col([
                create_metric_card(
                    "Total Users Monitored",
                    "users-count",
                    "fas fa-users",
                    "primary"
                )
            ], width=3),
            dbc.Col([
                create_metric_card(
                    "High Risk Users",
                    "high-risk-count",
                    "fas fa-exclamation-triangle",
                    "danger"
                )
            ], width=3),
            dbc.Col([
                create_metric_card(
                    "Avg Sentiment Score",
                    "avg-sentiment",
                    "fas fa-smile",
                    "success"
                )
            ], width=3),
            dbc.Col([
                create_metric_card(
                    "Active Alerts",
                    "active-alerts",
                    "fas fa-bell",
                    "warning"
                )
            ], width=3)
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Sentiment Trend Over Time"),
                    dbc.CardBody([
                        dcc.Graph(id='sentiment-trend-chart')
                    ])
                ], className="shadow-sm")
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id='risk-distribution-chart')
                    ])
                ], className="shadow-sm")
            ], width=4)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Mental Health Indicators"),
                    dbc.CardBody([
                        dcc.Graph(id='indicators-chart')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])


def create_sentiment_tab():
    """Create sentiment analysis tab content.
    
    Returns:
        Sentiment tab component
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Sentiment Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id='sentiment-distribution-chart')
                    ])
                ], className="shadow-sm")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Sentiment by Source"),
                    dbc.CardBody([
                        dcc.Graph(id='sentiment-by-source-chart')
                    ])
                ], className="shadow-sm")
            ], width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Keyword Analysis"),
                    dbc.CardBody([
                        dcc.Graph(id='keyword-chart')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Posts"),
                    dbc.CardBody([
                        html.Div(id='recent-posts-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])


def create_burnout_tab():
    """Create burnout predictions tab content.
    
    Returns:
        Burnout tab component
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Burnout Risk Heatmap"),
                    dbc.CardBody([
                        dcc.Graph(id='burnout-heatmap')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Score Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id='risk-score-distribution')
                    ])
                ], className="shadow-sm")
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Contributing Factors"),
                    dbc.CardBody([
                        dcc.Graph(id='contributing-factors-chart')
                    ])
                ], className="shadow-sm")
            ], width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("High Risk Users"),
                    dbc.CardBody([
                        html.Div(id='high-risk-users-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])


def create_alerts_tab():
    """Create alerts tab content.
    
    Returns:
        Alerts tab component
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Alert Timeline"),
                    dbc.CardBody([
                        dcc.Graph(id='alert-timeline-chart')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Alert History"),
                    dbc.CardBody([
                        html.Div(id='alert-history-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])


def create_metric_card(title, value_id, icon, color):
    """Create a metric card component.
    
    Args:
        title: Card title
        value_id: ID for the value element
        icon: FontAwesome icon class
        color: Bootstrap color
        
    Returns:
        Metric card component
    """
    color_map = {
        'primary': '#667eea',
        'danger': '#f56565',
        'success': '#48bb78',
        'warning': '#ed8936'
    }
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon} fa-3x mb-3", 
                      style={'color': color_map.get(color, '#667eea')}),
                html.H2(id=value_id, children="--", 
                       style={'fontWeight': '700', 'color': '#2d3748', 'marginBottom': '0.5rem'}),
                html.P(title, style={'color': '#718096', 'fontSize': '0.9rem', 'marginBottom': '0'})
            ], className="text-center", style={'padding': '1rem'})
        ])
    ], style={'borderRadius': '15px',
              'border': 'none',
              'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
              'transition': 'transform 0.3s ease',
              'background': 'white'})
