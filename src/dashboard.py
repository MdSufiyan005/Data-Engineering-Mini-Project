import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from src.database import query_fx_rates
from utils.config import Config

print("Starting dashboard...")
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('FX Rate Dashboard', style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.Label('Primary Currency:'),
            dcc.Dropdown(
                id='primary-currency',
                options=[
                    {'label': 'USD', 'value': 'USD'},
                    {'label': 'GBP', 'value': 'GBP'},
                    {'label': 'JPY', 'value': 'JPY'},
                    {'label': 'EUR', 'value': 'EUR'}
                ],
                value='USD'
            ),
            
            html.Label('Compare with:'),
            dcc.Dropdown(
                id='secondary-currency',
                options=[
                    {'label': 'GBP', 'value': 'GBP'},
                    {'label': 'JPY', 'value': 'JPY'},
                    {'label': 'EUR', 'value': 'EUR'},
                    {'label': 'USD', 'value': 'USD'}
                ],
                value='EUR'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Time Range:'),
            dcc.DatePickerRange(
                id='date-range',
                start_date=(datetime.now() - timedelta(days=30)).date(),
                end_date=datetime.now().date()
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    html.Div([
        dcc.Loading(
            id="loading-1",
            type="default",
            children=[
                html.Div([
                    dcc.Graph(id='fx-rate-graph'),
                    dcc.Graph(id='percentage-change-graph')
                ])
            ],
        ),
    ]),
    
    html.Div(id='error-message', style={'color': 'red'})
])

@app.callback(
    [Output('fx-rate-graph', 'figure'),
     Output('percentage-change-graph', 'figure')],
    [Input('primary-currency', 'value'),
     Input('secondary-currency', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graphs(primary_curr, secondary_curr, start_date, end_date):
    # Query data for both currencies
    primary_rates = query_fx_rates(primary_curr)
    secondary_rates = query_fx_rates(secondary_curr)
    
    # Debug print
    print(f"Primary rates: {len(primary_rates) if primary_rates else 0} records")
    print(f"Secondary rates: {len(secondary_rates) if secondary_rates else 0} records")
    
    if primary_rates and secondary_rates:
        # Create DataFrames for both currencies
        df_primary = pd.DataFrame(primary_rates, columns=['rate', 'timestamp'])
        df_secondary = pd.DataFrame(secondary_rates, columns=['rate', 'timestamp'])
        
        # Convert timestamps
        df_primary['timestamp'] = pd.to_datetime(df_primary['timestamp'])
        df_secondary['timestamp'] = pd.to_datetime(df_secondary['timestamp'])
        
        # Filter by date range
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        mask_primary = (df_primary['timestamp'].dt.date >= start_date.date()) & \
                      (df_primary['timestamp'].dt.date <= end_date.date())
        mask_secondary = (df_secondary['timestamp'].dt.date >= start_date.date()) & \
                        (df_secondary['timestamp'].dt.date <= end_date.date())
        
        df_primary = df_primary.loc[mask_primary]
        df_secondary = df_secondary.loc[mask_secondary]
        
        # Calculate percentage changes
        df_primary['pct_change'] = df_primary['rate'].pct_change() * 100
        df_secondary['pct_change'] = df_secondary['rate'].pct_change() * 100
        
        # Create exchange rate comparison figure
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig1.add_trace(
            go.Scatter(x=df_primary['timestamp'], y=df_primary['rate'],
                      name=f'{primary_curr}/EUR', line=dict(color='blue')),
            secondary_y=False
        )
        
        fig1.add_trace(
            go.Scatter(x=df_secondary['timestamp'], y=df_secondary['rate'],
                      name=f'{secondary_curr}/EUR', line=dict(color='red')),
            secondary_y=True
        )
        
        fig1.update_layout(
            title=f'Exchange Rate Comparison',
            xaxis_title='Date',
            yaxis_title=f'{primary_curr}/EUR Rate',
            yaxis2_title=f'{secondary_curr}/EUR Rate'
        )
        
        # Create percentage change figure
        fig2 = go.Figure()
        
        fig2.add_trace(
            go.Scatter(x=df_primary['timestamp'], y=df_primary['pct_change'],
                      name=f'{primary_curr} % Change', line=dict(color='blue'))
        )
        
        fig2.add_trace(
            go.Scatter(x=df_secondary['timestamp'], y=df_secondary['pct_change'],
                      name=f'{secondary_curr} % Change', line=dict(color='red'))
        )
        
        fig2.update_layout(
            title='Daily Percentage Changes',
            xaxis_title='Date',
            yaxis_title='Percentage Change (%)'
        )
        
        return fig1, fig2
    
    return {}, {}

def run_dashboard():
    """Run the dashboard server"""
    app.run(
        debug=Config.DASH_DEBUG,
        port=Config.DASH_PORT
    )