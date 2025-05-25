import datetime
from datetime import timedelta
from datetime import timezone
import praw
import re
from tweepy import Client
from stocks_agent.core.db_setup import SessionLocal, SocialPost, Stock
from stocks_agent.core.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT
    )

def fetch_reddit_posts(subreddit: str, symbols: list[str], days_back: int = 1, limit: int = 100) -> list[dict]:
    from datetime import timezone
    since = int((datetime.datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())
    reddit = init_reddit_client()
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).new(limit=limit):
            if submission.created_utc < since:
                continue
            text = (submission.title or "") + "\n" + (submission.selftext or "")
            for symbol in symbols:
                if symbol.lower() in text.lower():
                    posts.append({
                        "platform": "reddit",
                        "post_id": submission.id,
                        "symbol": symbol,
                        "author": getattr(submission.author, 'name', None),
                        "text": text,
                        "created_at": datetime.datetime.fromtimestamp(submission.created_utc, timezone.utc)
                    })
    except Exception as e:
        logger.error(f"Reddit fetch error: {e}")
    return posts

def init_twitter_client() -> Client:
    return Client(bearer_token=config.TWITTER_BEARER_TOKEN)

def fetch_twitter_posts(symbols: list[str], days_back: int = 1, max_results: int = 5) -> list[dict]:
    """
    Fetch recent tweets matching TWITTER_QUERY, then filter by our symbol list.
    """
    client = init_twitter_client()
    start_time = (
        datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=days_back)
    ).isoformat()

    resp = client.search_recent_tweets(
        query=config.TWITTER_QUERY,
        start_time=start_time,
        max_results=max_results,
        tweet_fields=["created_at", "author_id", "text"]
    )

    posts = []
    if resp.data:
        for t in resp.data:
            text = t.text or ""
            for symbol in symbols:
                if symbol.lower() in text.lower():
                    posts.append({
                        "platform": "twitter",
                        "post_id": str(t.id),
                        "symbol": symbol,
                        "author": t.author_id,
                        "text": text,
                        "created_at": t.created_at
                    })
    return posts

def store_social_posts(items: list[dict]):
    with SessionLocal() as session:
        for item in items:
            exists = session.query(SocialPost)\
                            .filter_by(platform=item["platform"], post_id=item["post_id"])\
                            .first()
            if exists:
                continue
            post = SocialPost(
                platform=item["platform"],
                post_id=item["post_id"],
                symbol=item["symbol"],
                author=item["author"],
                text=item["text"],
                created_at=item["created_at"]
            )
            session.add(post)
        session.commit()

def run_social_pipeline(symbols: list[str], days_back: int = 1):
    reddit_posts  = fetch_reddit_posts(config.REDDIT_SUBREDDIT, symbols, days_back)
    twitter_posts = fetch_twitter_posts(symbols, days_back)
    all_posts     = reddit_posts + twitter_posts
    store_social_posts(all_posts)

if __name__ == "__main__":
    # load symbols (for now from NEWS_KEYWORDS; later from your master Stocks table)
    keywords = getattr(config, 'NEWS_KEYWORDS', '')
    symbols = [s.strip() for s in keywords.split(",") if s.strip()]

    days_back = getattr(config, 'DAYS_BACK', 1)
    run_social_pipeline(symbols, days_back)
