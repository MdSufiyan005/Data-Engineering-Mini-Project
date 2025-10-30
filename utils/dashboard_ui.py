# dashboard_ui.py
from dash import dcc, html
from datetime import datetime, timedelta

# Color palette
COLORS = {
    'bg_main': '#0f172a',
    'bg_card': '#1e293b',
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'text': '#f1f5f9',
    'text_muted': '#94a3b8',
    'border': '#334155'
}

def serve_layout():
    """Builds and returns the dashboard layout"""
    return html.Div([
        # Header
        html.Div([
            html.H1('💱 FX Rate Dashboard', style={
                'textAlign': 'center',
                'marginBottom': '5px',
                'color': COLORS['text'],
                'fontSize': '2.5rem',
                'fontWeight': '700',
                'letterSpacing': '-0.02em'
            }),
            html.P('Real-time currency exchange monitoring', style={
                'textAlign': 'center',
                'color': COLORS['text_muted'],
                'fontSize': '1rem',
                'margin': '0'
            })
        ], style={
            'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
            'padding': '40px 20px',
            'marginBottom': '30px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),

        # Main container
        html.Div([
            # Controls
            html.Div([
                html.Div([
                    html.Label('Primary Currency:', style={
                        'color': COLORS['text'],
                        'fontWeight': '600',
                        'fontSize': '0.9rem',
                        'marginBottom': '8px',
                        'display': 'block'
                    }),
                    dcc.Dropdown(
                        id='primary-currency',
                        options=[
                            {'label': '🇺🇸 USD - US Dollar', 'value': 'USD'},
                            {'label': '🇬🇧 GBP - British Pound', 'value': 'GBP'},
                            {'label': '🇯🇵 JPY - Japanese Yen', 'value': 'JPY'},
                            {'label': '🇪🇺 EUR - Euro', 'value': 'EUR'}
                        ],
                        value='USD',
                        clearable=False,
                        style={'marginBottom': '20px'}
                    ),

                    html.Label('Compare with:', style={
                        'color': COLORS['text'],
                        'fontWeight': '600',
                        'fontSize': '0.9rem',
                        'marginBottom': '8px',
                        'display': 'block'
                    }),
                    dcc.Dropdown(
                        id='secondary-currency',
                        options=[
                            {'label': '🇬🇧 GBP - British Pound', 'value': 'GBP'},
                            {'label': '🇯🇵 JPY - Japanese Yen', 'value': 'JPY'},
                            {'label': '🇪🇺 EUR - Euro', 'value': 'EUR'},
                            {'label': '🇺🇸 USD - US Dollar', 'value': 'USD'}
                        ],
                        value='EUR',
                        clearable=False
                    ),
                ], style={
                    'width': '48%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'paddingRight': '20px'
                }),

                html.Div([
                    html.Label('Time Range:', style={
                        'color': COLORS['text'],
                        'fontWeight': '600',
                        'fontSize': '0.9rem',
                        'marginBottom': '8px',
                        'display': 'block'
                    }),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=(datetime.now() - timedelta(days=30)).date(),
                        end_date=datetime.now().date(),
                        display_format='MMM D, YYYY'
                    ),
                ], style={
                    'width': '48%',
                    'float': 'right',
                    'display': 'inline-block'
                })
            ], style={
                'backgroundColor': COLORS['bg_card'],
                'padding': '30px',
                'borderRadius': '12px',
                'marginBottom': '25px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Charts
            dcc.Loading(
                id="loading-1",
                type="circle",
                color=COLORS['primary'],
                children=[
                    html.Div([
                        html.Div([
                            dcc.Graph(id='fx-rate-graph', config={'displayModeBar': True})
                        ], style={
                            'backgroundColor': COLORS['bg_card'],
                            'padding': '20px',
                            'borderRadius': '12px',
                            'marginBottom': '25px',
                            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                            'border': f'1px solid {COLORS["border"]}'
                        }),

                        html.Div([
                            dcc.Graph(id='percentage-change-graph', config={'displayModeBar': True})
                        ], style={
                            'backgroundColor': COLORS['bg_card'],
                            'padding': '20px',
                            'borderRadius': '12px',
                            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                            'border': f'1px solid {COLORS["border"]}'
                        })
                    ])
                ],
            ),

            # Error message
            html.Div(id='error-message', style={
                'color': COLORS['danger'],
                'textAlign': 'center',
                'marginTop': '20px',
                'padding': '15px',
                'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                'borderRadius': '8px',
                'fontWeight': '500'
            })
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '0 20px 40px 20px'
        })
    ], style={
        'backgroundColor': COLORS['bg_main'],
        'minHeight': '100vh',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    })
