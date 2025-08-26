# Twitter Sentiment Analysis Dashboard

This project provides a dashboard for visualizing Twitter sentiment using the Sentiment140 dataset. It processes tweets, analyzes sentiment with a Transformer model, stores results in a local SQLite database, and displays interactive graphs using Plotly Dash, running locally or deployable on Heroku.

## Dataset
- **Name**: Sentiment140
- **Description**: Contains 1.6 million tweets labeled for sentiment (positive, negative, neutral).
- **Source**: [Kaggle: Sentiment140 dataset](https://www.kaggle.com/datasets/kazanova/sentiment140)
- Located in `data/sentiment140.csv`. No sensitive PII; data is public.

## Features
- **Dataset Processing**: Loads and processes tweets from the Sentiment140 dataset.
- **Sentiment Analysis**: Uses a Hugging Face Transformer model (DistilBERT) to classify tweet sentiment.
- **Data Storage**: Stores results in a local SQLite database.
- **Live Dashboard**: Displays sentiment distribution and trends using Plotly Dash.

## Project Structure
- `data/`: Sentiment140 dataset.
- `src/`: Scripts for preprocessing, dataset processing, and dashboard.
- `main.py`: Orchestrates the pipeline.
- `.env.example`: Template for environment variables.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation.

## Setup Instructions
1. **Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   Note: Developed on macOS M1; dependencies are compatible with Apple Silicon.
2. **Download Dataset**:
   - Download `training.1600000.processed.noemoticon.csv` from [Kaggle: Sentiment140](https://www.kaggle.com/datasets/kazanova/sentiment140).
   - Rename to `data/sentiment140.csv`.
3. **Configure Environment**:
   - Copy `.env.example` to `.env` and specify `SQLITE_DB` (default: `tweets.db`).
4. **Run Pipeline Locally**:
   ```bash
   python main.py --csv-path data/sentiment140.csv --max-tweets 100
   ```
   This processes tweets, stores them in SQLite, and launches the dashboard at `http://127.0.0.1:8050`.

## Technologies
- **Hugging Face Transformers**: Sentiment analysis.
- **Plotly Dash**: Web dashboard.
- **SQLite**: Data storage.
- **Pandas**: Dataset processing.
