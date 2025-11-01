
# dashboard_logic.py
import dash
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from src.database import query_fx_rates
from utils.config import Config
from utils.dashboard_ui import serve_layout, COLORS

import plotly.graph_objects as go

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = dash.Dash(__name__)
app.title = "FX Rate Dashboard"
app.layout = serve_layout()

def _empty_figure(title="No data"):
    return {
        "data": [],
        "layout": {
            "title": {"text": title, "font": {"color": COLORS['text'], "size": 18}},
            "template": "plotly_dark",
            "paper_bgcolor": COLORS['bg_card'],
            "plot_bgcolor": COLORS['bg_card'],
            "font": {"color": COLORS['text']},
            "height": 400
        }
    }

@app.callback(
    [Output('fx-rate-graph', 'figure'),
     Output('percentage-change-graph', 'figure'),
     Output('error-message', 'children')],
    [Input('primary-currency', 'value'),
     Input('secondary-currency', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graphs(primary_curr, secondary_curr, start_date, end_date):
    try:
        logger.info("Update requested: %s vs %s (%s -> %s)", primary_curr, secondary_curr, start_date, end_date)

        if not primary_curr or not secondary_curr:
            return _empty_figure("Select currencies"), _empty_figure("Select currencies"), "Please select both currencies."

        primary_rates = query_fx_rates(primary_curr) or []
        secondary_rates = query_fx_rates(secondary_curr) or []

        if len(primary_rates) == 0 or len(secondary_rates) == 0:
            return _empty_figure("No data"), _empty_figure("No data"), "No rate history found."

        df_p = pd.DataFrame(primary_rates, columns=['rate', 'timestamp'])
        df_s = pd.DataFrame(secondary_rates, columns=['rate', 'timestamp'])
        df_p['timestamp'] = pd.to_datetime(df_p['timestamp'])
        df_s['timestamp'] = pd.to_datetime(df_s['timestamp'])
        df_p = df_p.sort_values('timestamp')
        df_s = df_s.sort_values('timestamp')

        # Merge on timestamp
        df = pd.merge_asof(df_p, df_s, on='timestamp', direction='nearest', tolerance=pd.Timedelta('1D'),
                           suffixes=('_p', '_s')).dropna()

        if df.empty:
            return _empty_figure("No overlapping data"), _empty_figure("No data"), "No overlapping timestamps."

        df['direct_rate'] = df['rate_p'] / df['rate_s']
        df['direct_rate_ma7'] = df['direct_rate'].rolling(window=7, min_periods=1).mean()
        df['pct_direct'] = df['direct_rate'].pct_change() * 100
        df['volatility'] = df['pct_direct'].rolling(window=7, min_periods=1).std()

        # --- Plot 1: Exchange Rate ---
        fig1 = go.Figure([
            go.Scatter(x=df['timestamp'], y=df['direct_rate'], mode='lines+markers',
                       name=f'{primary_curr}/{secondary_curr}',
                       line=dict(color=COLORS['primary'], width=3))
        ])
        fig1.add_trace(go.Scatter(x=df['timestamp'], y=df['direct_rate_ma7'],
                                  mode='lines', name='7-day MA',
                                  line=dict(color=COLORS['warning'], dash='dash')))
        fig1.update_layout(
            title=f'📈 Exchange Rate: {primary_curr}/{secondary_curr}',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text'])
        )

        # --- Plot 2: % Change ---
        fig2 = go.Figure([
            go.Bar(x=df['timestamp'], y=df['pct_direct'], name='% Change', marker_color=COLORS['secondary']),
            go.Scatter(x=df['timestamp'], y=df['volatility'], name='Volatility (7d)', yaxis='y2',
                       line=dict(color=COLORS['danger'], width=3))
        ])
        fig2.update_layout(
            title='📊 Daily % Change and Volatility',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            yaxis2=dict(overlaying='y', side='right', showgrid=False)
        )

        return fig1, fig2, ""
    except Exception as e:
        logger.exception("Error updating graphs")
        return _empty_figure("Error"), _empty_figure("Error"), f"Error: {str(e)}"

def run_dashboard():
    app.run(debug=Config.DASH_DEBUG, port=Config.DASH_PORT)
