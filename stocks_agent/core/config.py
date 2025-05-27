import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    DB_PATH: str = os.getenv("DB_PATH")
    NEWS_API_QUERY: str = os.getenv("NEWS_API_QUERY")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    RSS_FEEDS: list = None
    DAYS_BACK: int = int(os.getenv("DAYS_BACK", 1))
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT")
    REDDIT_SUBREDDIT: str = os.getenv("REDDIT_SUBREDDIT")
    TWITTERAPI_IO_KEY: str = os.getenv("TWITTERAPI_IO_KEY")
    SOCIAL_SYMBOLS: list = None
    NEWS_KEYWORDS: str = os.getenv("NEWS_KEYWORDS")

    def __post_init__(self):
        missing = []
        if not self.DB_PATH:
            missing.append("DB_PATH")
        if not self.NEWS_API_QUERY:
            missing.append("NEWS_API_QUERY")
        if not self.NEWS_API_KEY:
            missing.append("NEWS_API_KEY")
        rss_feeds = os.getenv("RSS_FEEDS")
        if rss_feeds:
            self.RSS_FEEDS = [f.strip() for f in rss_feeds.split(",") if f.strip()]
        else:
            self.RSS_FEEDS = []
        # Social/Reddit/Twitter config
        if not self.REDDIT_CLIENT_ID:
            missing.append("REDDIT_CLIENT_ID")
        if not self.REDDIT_CLIENT_SECRET:
            missing.append("REDDIT_CLIENT_SECRET")
        if not self.REDDIT_USER_AGENT:
            missing.append("REDDIT_USER_AGENT")
        if not self.REDDIT_SUBREDDIT:
            missing.append("REDDIT_SUBREDDIT")
        social_symbols = os.getenv("SOCIAL_SYMBOLS")
        if social_symbols:
            self.SOCIAL_SYMBOLS = [s.strip() for s in social_symbols.split(",") if s.strip()]
        else:
            self.SOCIAL_SYMBOLS = []
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Expose a single config instance
config = Config()
