import datetime
from datetime import timedelta
import requests
import feedparser
from newspaper import Article
from stocks_agent.core.db_setup import SessionLocal, NewsArticle
from stocks_agent.core.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_all_stock_news(days_back: int = 1) -> list[dict]:
    to_date = datetime.date.today()
    from_date = to_date - timedelta(days=days_back)
    articles = []
    # NewsAPI
    try:
        params = {
            'q': config.NEWS_API_QUERY,
            'from': from_date.isoformat(),
            'to': to_date.isoformat(),
            'apiKey': config.NEWS_API_KEY,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100
        }
        resp = requests.get('https://newsapi.org/v2/everything', params=params)
        if resp.status_code == 200:
            for art in resp.json().get('articles', []):
                articles.append({
                    'title': art.get('title'),
                    'url': art.get('url'),
                    'published': art.get('publishedAt'),
                    'summary': art.get('description'),
                    'source': art.get('source', {}).get('name')
                })
        else:
            logger.warning(f"NewsAPI error: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
    # RSS feeds
    for feed_url in getattr(config, 'RSS_FEEDS', []):
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                published = entry.get('published', entry.get('updated', None))
                articles.append({
                    'title': entry.get('title'),
                    'url': entry.get('link'),
                    'published': published,
                    'summary': entry.get('summary', ''),
                    'source': feed.feed.get('title', feed_url)
                })
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
    # Normalize published to datetime
    for art in articles:
        try:
            if art['published'] and not isinstance(art['published'], datetime.datetime):
                art['published'] = datetime.datetime.fromisoformat(art['published'].replace('Z', '+00:00'))
        except Exception:
            art['published'] = None
    return articles

def scrape_and_store_articles(items: list[dict]):
    with SessionLocal() as session:
        for item in items:
            if not item.get('url'):
                continue
            # Skip if published_at is missing
            if not item.get('published'):
                logger.warning(f"Skipping article with missing published date: {item.get('url')}")
                continue
            exists = session.query(NewsArticle).filter_by(url=item['url']).first()
            if exists:
                continue
            try:
                art = Article(item['url'])
                art.download()
                art.parse()
                content = art.text
            except Exception as e:
                logger.warning(f"Failed to scrape {item['url']}: {e}")
                content = None
            news = NewsArticle(
                source=item.get('source'),
                title=item.get('title'),
                url=item.get('url'),
                published_at=item.get('published'),
                content=content
            )
            session.add(news)
        session.commit()

def run_news_pipeline(days_back: int = 1):
    raw_items = fetch_all_stock_news(days_back)
    scrape_and_store_articles(raw_items)

if __name__ == "__main__":
    days = getattr(config, 'DAYS_BACK', 1)
    run_news_pipeline(days)
