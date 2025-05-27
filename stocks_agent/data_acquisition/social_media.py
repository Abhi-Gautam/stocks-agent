import datetime
from datetime import timedelta, timezone
import praw
import requests
from stocks_agent.core.db_setup import SessionLocal, SocialPost
from stocks_agent.core.config import config
import logging
from dateutil import parser as date_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT
    )

def fetch_reddit_posts(subreddit: str, days_back: int = 1, limit: int = 100) -> list[dict]:
    since = int((datetime.datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())
    reddit = init_reddit_client()
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).new(limit=limit):
            if submission.created_utc < since:
                continue
            text = (submission.title or "") + "\n" + (submission.selftext or "")
            posts.append({
                "platform": "reddit",
                "post_id": submission.id,
                "symbol": None,  # To be filled later
                "author": getattr(submission.author, 'name', None),
                "text": text,
                "created_at": datetime.datetime.fromtimestamp(submission.created_utc, timezone.utc)
            })
    except Exception as e:
        logger.error(f"Reddit fetch error: {e}")
    return posts

def fetch_twitter_posts(usernames: list[str]) -> list[dict]:
    api_key = config.TWITTERAPI_IO_KEY
    posts = []
    for username in usernames:
        try:
            resp = requests.get(
                "https://api.twitterapi.io/twitter/user/last_tweets",
                headers={"X-API-Key": api_key},
                params={"userName": username}
            )
            if resp.status_code == 200:
                data = resp.json()
                tweets = data.get("data", {}).get("tweets", [])
                for t in tweets:
                    author_info = t.get("author", {})
                    posts.append({
                        "platform": "twitter",
                        "post_id": str(t.get("id")),
                        "symbol": None,  # To be filled later
                        "author": author_info.get("userName", username),
                        "text": t.get("text", ""),
                        "created_at": date_parser.parse(t.get("createdAt")) if t.get("createdAt") else None,
                        "url": t.get("url"),
                        "retweet_count": t.get("retweetCount"),
                        "reply_count": t.get("replyCount"),
                        "like_count": t.get("likeCount"),
                        "quote_count": t.get("quoteCount"),
                        "view_count": t.get("viewCount"),
                        "lang": t.get("lang"),
                    })
            else:
                logger.error(f"twitterAPI.io error for {username}: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"twitterAPI.io fetch error for {username}: {e}")
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
                symbol=item.get("symbol"),
                author=item["author"],
                text=item["text"],
                created_at=item["created_at"]
            )
            session.add(post)
        session.commit()

def run_social_pipeline(usernames: list[str], days_back: int = 1):
    # reddit_posts = fetch_reddit_posts(config.REDDIT_SUBREDDIT, days_back)
    twitter_posts = fetch_twitter_posts(usernames)
    all_posts = twitter_posts
    store_social_posts(all_posts)