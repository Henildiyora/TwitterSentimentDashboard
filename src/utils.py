import logging
from wordcloud import WordCloud
import io
import base64
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_wordcloud(text_data):
    """
    Generate a word cloud from tweet text.
    
    Args:
        text_data (list): List of tweet texts
    
    Returns:
        str: Base64 encoded word cloud image
    """
    try:
        stop_words = set(stopwords.words('english'))
        text = " ".join(text_data)
        tokens = [word for word in word_tokenize(text.lower()) if word not in stop_words and len(word) > 2]
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(tokens))
        
        img = io.BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img_str = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()
        return img_str
    except Exception as e:
        logger.error(f"Failed to generate word cloud: {str(e)}")
        return None