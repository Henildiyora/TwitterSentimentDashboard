import argparse
from dotenv import load_dotenv
import logging
from src.process_dataset import process_dataset
from src.app import create_dashboard

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Advanced Twitter Sentiment Analysis Dashboard")
    parser.add_argument('--csv-path', default='data/sentiment140.csv', help='Path to Sentiment140 CSV')
    parser.add_argument('--max-tweets', type=int, default=100, help='Maximum tweets to process')
    parser.add_argument('--db-path', help='Path to SQLite database (overrides .env)')
    args = parser.parse_args()

    try:
        logger.info("Starting pipeline...")
        # Process dataset and store in SQLite
        tweets_data = process_dataset(args.csv_path, args.max_tweets, args.db_path)
        logger.info("Dataset processing completed")

        # Launch dashboard
        create_dashboard(args.db_path)
        logger.info("Dashboard running")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()