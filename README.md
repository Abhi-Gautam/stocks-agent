# Stocks Agent

A modular Python agent for acquiring, analyzing, and reporting on stock market data, news, and social sentiment.

---

## Features
- **Data Acquisition**: Fetches historical price data (Yahoo Finance), news (NewsAPI, RSS, Newspaper3k), and social media posts (Reddit, Twitter/X).
- **Database**: Stores all data in a local SQLite database (`data/stock_market.db`).
- **Analysis**: Symbol mention extraction, sentiment analysis, and recommendations.
- **Orchestration**: Scheduler for regular data updates.

## Setup
1. **Clone the repository**
2. **Install dependencies** (using Poetry):
   ```sh
   poetry install
   ```
3. **Configure environment**: Copy `.env.example` to `.env` and fill in your API keys and config values.
4. **Initialize the database** (tables auto-create on first run).

## Usage
- **Fetch price data:**
  ```sh
  poetry run python -m stocks_agent.data_acquisition.financial_data
  ```
- **Fetch news:**
  ```sh
  poetry run python -m stocks_agent.data_acquisition.news_data
  ```
- **Fetch social media posts:**
  ```sh
  poetry run python -m stocks_agent.data_acquisition.social_media
  ```
- **Run analysis:**
  ```sh
  poetry run python -m stocks_agent.analysis.content_analyzer
  ```

## Project Structure
- `core/`: Configuration and database setup
- `data_acquisition/`: Scripts for fetching data
- `analysis/`: Content and sentiment analysis
- `processing/`, `recommendation/`, `reporting/`: Advanced modules
- `data/`: SQLite database and data files

## .env Example
```
DB_PATH=data/stock_market.db
NEWS_API_QUERY=indian stock market
NEWS_API_KEY=your_newsapi_key
RSS_FEEDS=https://example.com/rss1.xml,https://example.com/rss2.xml
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_agent
REDDIT_SUBREDDIT=stocks
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_QUERY=stock OR market OR finance
SOCIAL_SYMBOLS=AAPL,GOOGL,MSFT
NEWS_KEYWORDS=stock,market,finance
NEWS_DAYS_BACK=1
DAYS_BACK=1
```

## License
MIT
