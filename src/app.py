import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_sqlite_data(db_path=None, limit=100):
    """
    Fetch recent tweets from SQLite database.
    
    Args:
        db_path (str): Path to SQLite database (from .env if None)
        limit (int): Maximum number of items to fetch
    
    Returns:
        list: List of tweet data
    """
    try:
        db_path = db_path or os.getenv('SQLITE_DB', 'tweets.db')
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM tweets ORDER BY Timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info(f"Fetched {len(df)} items from SQLite")
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Failed to fetch SQLite data: {str(e)}")
        raise

def create_dashboard(db_path=None):
    """
    Create and run the Plotly Dash app.
    
    Args:
        db_path (str): Path to SQLite database (from .env if None)
    """
    try:
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.H1("Twitter Sentiment Dashboard"),
            dcc.Graph(id='sentiment-pie'),
            dcc.Graph(id='sentiment-time'),
            dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Update every 60s
        ])

        @app.callback(
            [Output('sentiment-pie', 'figure'), Output('sentiment-time', 'figure')],
            Input('interval-component', 'n_intervals')
        )
        def update_graphs(n):
            try:
                data = fetch_sqlite_data(db_path)
                df = pd.DataFrame(data)

                # Pie chart: Sentiment distribution
                sentiment_counts = df['Sentiment'].value_counts()
                pie_fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title='Sentiment Distribution'
                )

                # Time series: Sentiment over time
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
                time_counts = df.groupby([pd.Grouper(key='Timestamp', freq='1min'), 'Sentiment']).size().unstack(fill_value=0)
                time_fig = px.line(
                    time_counts,
                    x=time_counts.index,
                    y=time_counts.columns,
                    title='Sentiment Trends Over Time'
                )

                return pie_fig, time_fig
            except Exception as e:
                logger.error(f"Failed to update dashboard graphs: {str(e)}")
                raise

        logger.info("Starting Dash app...")
        app.run(host='0.0.0.0', port=8050, debug=False)
    except Exception as e:
        logger.error(f"Dashboard creation failed: {str(e)}")
        raise