import re
import logging
from dotenv import load_dotenv
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def preprocess_tweet(tweet_text):
    """
    Preprocess tweet text for sentiment analysis with advanced cleaning.
    
    Args:
        tweet_text (str): Raw tweet text
    
    Returns:
        str: Cleaned tweet text
    """
    try:
        logger.info("Preprocessing tweet...")
        # Remove URLs
        tweet_text = re.sub(r'http\S+|www\S+|https\S+', '', tweet_text, flags=re.MULTILINE)
        # Remove mentions and hashtags
        tweet_text = re.sub(r'@\w+|#\w+', '', tweet_text)
        # Remove special characters, keep alphanumeric and spaces
        tweet_text = re.sub(r'[^\w\s]', '', tweet_text)
        # Convert to lowercase
        tweet_text = tweet_text.lower()
        # Lemmatization
        lemmatizer = WordNetLemmatizer()
        tokens = word_tokenize(tweet_text)
        tweet_text = ' '.join(lemmatizer.lemmatize(token) for token in tokens)
        # Remove extra spaces
        tweet_text = re.sub(r'\s+', ' ', tweet_text).strip()
        logger.info("Tweet preprocessing completed")
        return tweet_text
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        raise