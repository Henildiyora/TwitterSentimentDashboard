import pandas as pd
import sqlite3
from transformers import pipeline
from src.preprocess import preprocess_tweet
from dotenv import load_dotenv
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_sqlite(db_path=None):
    """
    Initialize SQLite database and create tweets table.
    
    Args:
        db_path (str): Path to SQLite database (from .env if None)
    
    Returns:
        sqlite3.Connection: SQLite connection
    """
    try:
        db_path = db_path or os.getenv('SQLITE_DB', 'tweets.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                TweetID TEXT PRIMARY KEY,
                Text TEXT,
                Sentiment TEXT,
                Score REAL,
                Timestamp INTEGER
            )
        ''')
        conn.commit()
        logger.info(f"Initialized SQLite database at {db_path}")
        return conn
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {str(e)}")
        raise

def process_dataset(csv_path='data/sentiment140.csv', max_tweets=100, db_path=None):
    """
    Process the Sentiment140 dataset, analyze sentiment, and store in SQLite.
    
    Args:
        csv_path (str): Path to Sentiment140 CSV
        max_tweets (int): Maximum number of tweets to process
        db_path (str): Path to SQLite database (from .env if None)
    
    Returns:
        list: List of processed tweet data
    """
    try:
        # Load dataset
        logger.info(f"Loading dataset from {csv_path}...")
        df = pd.read_csv(csv_path, encoding='latin-1', names=['sentiment', 'id', 'date', 'query', 'user', 'text'])
        df = df.sample(n=min(max_tweets, len(df)), random_state=42)
        logger.info(f"Loaded {len(df)} tweets")

        # Initialize sentiment analysis pipeline with RoBERTa
        nlp = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment')
        logger.info("Initialized sentiment analysis pipeline")

        # Initialize SQLite
        conn = initialize_sqlite(db_path)
        cursor = conn.cursor()

        # Process tweets
        tweets_data = []
        for _, row in df.iterrows():
            try:
                cleaned_text = preprocess_tweet(row['text'])
                if not cleaned_text:
                    continue

                # Analyze sentiment
                result = nlp(cleaned_text)[0]
                sentiment_label = result['label'].replace('LABEL_0', 'NEGATIVE').replace('LABEL_1', 'NEUTRAL').replace('LABEL_2', 'POSITIVE')
                sentiment_score = result['score']

                # Store in SQLite
                cursor.execute('''
                    INSERT OR REPLACE INTO tweets (TweetID, Text, Sentiment, Score, Timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(row['id']), cleaned_text, sentiment_label, float(sentiment_score), int(time.time())))
                conn.commit()
                logger.info(f"Stored tweet {row['id']} in SQLite")

                tweets_data.append({
                    'TweetID': str(row['id']),
                    'Text': cleaned_text,
                    'Sentiment': sentiment_label,
                    'Score': float(sentiment_score),
                    'Timestamp': int(time.time())
                })
            except Exception as e:
                logger.error(f"Failed to process tweet {row['id']}: {str(e)}")
                continue

        conn.close()
        logger.info(f"Processed and stored {len(tweets_data)} tweets")
        return tweets_data
    except Exception as e:
        logger.error(f"Dataset processing failed: {str(e)}")
        raise