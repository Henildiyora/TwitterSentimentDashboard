import plotly.express as px
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os
import logging
from src.utils import generate_wordcloud

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_sqlite_data(db_path=None, limit=1000, sentiment_filter=None, keyword=None):
    """
    Fetch recent tweets from SQLite database with optional filtering.
    
    Args:
        db_path (str): Path to SQLite database
        limit (int): Maximum number of items to fetch
        sentiment_filter (str): Filter by sentiment (POSITIVE, NEGATIVE, NEUTRAL, or None)
        keyword (str): Filter by keyword in tweet text
    
    Returns:
        list: List of tweet data
    """
    try:
        db_path = db_path or os.getenv('SQLITE_DB', 'tweets.db')
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM tweets"
        conditions = []
        params = []
        
        if sentiment_filter:
            conditions.append("Sentiment = ?")
            params.append(sentiment_filter)
        if keyword:
            conditions.append("Text LIKE ?")
            params.append(f"%{keyword}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY Timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        logger.info(f"Fetched {len(df)} items from SQLite")
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Failed to fetch SQLite data: {str(e)}")
        raise

def create_dashboard(db_path=None):
    """
    Create and run an advanced Plotly Dash app with Tailwind CSS and fixed layout.
    
    Args:
        db_path (str): Path to SQLite database
    """
    try:
        app = Dash(__name__, external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'
        ])

        app.layout = html.Div(className='container mx-auto p-4 bg-gray-100 h-screen flex flex-col', children=[
            html.H1("Advanced Twitter Sentiment Analysis Dashboard", className='text-3xl font-bold text-center mb-6 text-blue-800'),
            
            # Filters
            html.Div(className='flex flex-wrap gap-4 mb-6', children=[
                html.Div(className='flex-1 min-w-[200px]', children=[
                    html.Label("Sentiment Filter", className='block text-sm font-medium text-gray-700'),
                    dcc.Dropdown(
                        id='sentiment-filter',
                        options=[
                            {'label': 'All', 'value': ''},
                            {'label': 'Positive', 'value': 'POSITIVE'},
                            {'label': 'Neutral', 'value': 'NEUTRAL'},
                            {'label': 'Negative', 'value': 'NEGATIVE'}
                        ],
                        value='',
                        className='mt-1 block w-full border-gray-300 rounded-md shadow-sm'
                    )
                ]),
                html.Div(className='flex-1 min-w-[200px]', children=[
                    html.Label("Keyword Search", className='block text-sm font-medium text-gray-700'),
                    dcc.Input(
                        id='keyword-filter',
                        type='text',
                        placeholder='Enter keyword...',
                        className='mt-1 block w-full border-gray-300 rounded-md shadow-sm'
                    )
                ]),
                html.Button('Apply Filters', id='apply-filters', className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded')
            ]),

            # Visualizations
            html.Div(className='flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto', style={'maxHeight': 'calc(100vh - 200px)'}, children=[
                html.Div([
                    html.H2("Sentiment Distribution", className='text-xl font-semibold mb-2'),
                    dcc.Graph(id='sentiment-pie', style={'height': '100%', 'minHeight': '300px', 'maxHeight': '400px'})
                ], className='bg-white p-4 rounded-lg shadow'),
                html.Div([
                    html.H2("Sentiment Trends Over Time", className='text-xl font-semibold mb-2'),
                    dcc.Graph(id='sentiment-time', style={'height': '100%', 'minHeight': '300px', 'maxHeight': '400px'})
                ], className='bg-white p-4 rounded-lg shadow'),
                html.Div([
                    html.H2("Word Cloud", className='text-xl font-semibold mb-2'),
                    html.Img(id='word-cloud', className='w-full h-[300px] object-contain')
                ], className='bg-white p-4 rounded-lg shadow'),
                html.Div([
                    html.H2("Recent Tweets", className='text-xl font-semibold mb-2'),
                    dash_table.DataTable(
                        id='tweets-table',
                        columns=[
                            {'name': 'Tweet ID', 'id': 'TweetID'},
                            {'name': 'Text', 'id': 'Text'},
                            {'name': 'Sentiment', 'id': 'Sentiment'},
                            {'name': 'Score', 'id': 'Score'},
                            {'name': 'Timestamp', 'id': 'Timestamp'}
                        ],
                        style_table={'overflowX': 'auto', 'height': '300px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'maxWidth': '300px', 'whiteSpace': 'normal'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        page_size=10
                    )
                ], className='bg-white p-4 rounded-lg shadow')
            ]),

            dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Update every 60s
        ])

        @app.callback(
            [
                Output('sentiment-pie', 'figure'),
                Output('sentiment-time', 'figure'),
                Output('word-cloud', 'src'),
                Output('tweets-table', 'data')
            ],
            [
                Input('interval-component', 'n_intervals'),
                Input('apply-filters', 'n_clicks')
            ],
            [
                State('sentiment-filter', 'value'),
                State('keyword-filter', 'value')
            ]
        )
        def update_dashboard(n, n_clicks, sentiment_filter, keyword):
            try:
                sentiment_filter = sentiment_filter if sentiment_filter else None
                data = fetch_sqlite_data(db_path, sentiment_filter=sentiment_filter, keyword=keyword)
                df = pd.DataFrame(data)

                if df.empty:
                    empty_pie = px.pie(names=['No Data'], values=[1], title='Sentiment Distribution')
                    empty_time = px.line(title='Sentiment Trends Over Time')
                    return empty_pie, empty_time, '', []

                # Pie chart: Sentiment distribution
                sentiment_counts = df['Sentiment'].value_counts()
                pie_fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title='Sentiment Distribution',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                pie_fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=300
                )

                # Time series: Sentiment over time
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
                time_counts = df.groupby([pd.Grouper(key='Timestamp', freq='5min'), 'Sentiment']).size().unstack(fill_value=0)
                time_fig = px.line(
                    time_counts,
                    x=time_counts.index,
                    y=time_counts.columns,
                    title='Sentiment Trends Over Time',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                time_fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis_title="Time",
                    yaxis_title="Number of Tweets",
                    height=300
                )

                # Word cloud
                wordcloud_img = generate_wordcloud(df['Text'].tolist()) or ''

                # Table data
                table_data = df[['TweetID', 'Text', 'Sentiment', 'Score', 'Timestamp']].to_dict('records')

                return pie_fig, time_fig, wordcloud_img, table_data
            except Exception as e:
                logger.error(f"Failed to update dashboard: {str(e)}")
                raise

        logger.info("Starting Dash app...")
        app.run(host='0.0.0.0', port=8050, debug=False)
    except Exception as e:
        logger.error(f"Dashboard creation failed: {str(e)}")
        raise