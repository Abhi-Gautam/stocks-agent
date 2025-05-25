import re
import datetime
from stocks_agent.core.db_setup import SessionLocal, NewsArticle, SocialPost, SentimentScore, Stock
from stocks_agent.core.config import config
from stocks_agent.analysis.sentiment_analyzer import get_sentiment

def find_symbol_mentions(text: str, symbols: list[str]) -> dict[str, list[str]]:
    if not text:
        return {}
    result = {}
    for symbol in symbols:
        matches = list(re.finditer(rf"\b{re.escape(symbol)}\b", text, flags=re.IGNORECASE))
        snippets = []
        for m in matches:
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 50)
            snippet = text[start:end]
            snippets.append(snippet)
        if snippets:
            result[symbol] = snippets
    return result

def analyze_positive_news_mentions(days_back: int = 1):
    with SessionLocal() as session:
        symbols = [s[0] for s in session.query(Stock.symbol).all()]
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
        articles = session.query(NewsArticle).filter(
            NewsArticle.published_at >= since
        ).all()
        for article in articles:
            # Skip if already has SentimentScore
            exists = session.query(SentimentScore).filter_by(post_type="news", post_id=article.id).first()
            if exists:
                continue
            snippets_dict = find_symbol_mentions(article.content, symbols)
            for symbol, snippet_list in snippets_dict.items():
                for snippet in snippet_list:
                    label, score = get_sentiment(snippet)
                    if label == "positive":
                        sentiment = SentimentScore(
                            post_type="news",
                            post_id=article.id,
                            sentiment=label,
                            score=score,
                            analyzed_at=datetime.datetime.utcnow()
                        )
                        session.add(sentiment)
        session.commit()

def analyze_positive_social_mentions(days_back: int = 1):
    with SessionLocal() as session:
        symbols = [s[0] for s in session.query(Stock.symbol).all()]
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
        posts = session.query(SocialPost).filter(
            SocialPost.created_at >= since
        ).all()
        for post in posts:
            # Skip if already has SentimentScore
            exists = session.query(SentimentScore).filter_by(post_type="social", post_id=post.id).first()
            if exists:
                continue
            snippets_dict = find_symbol_mentions(post.text, symbols)
            for symbol, snippet_list in snippets_dict.items():
                for snippet in snippet_list:
                    label, score = get_sentiment(snippet)
                    if label == "positive":
                        sentiment = SentimentScore(
                            post_type="social",
                            post_id=post.id,
                            sentiment=label,
                            score=score,
                            analyzed_at=datetime.datetime.utcnow()
                        )
                        session.add(sentiment)
        session.commit()

if __name__ == "__main__":
    days = getattr(config, 'DAYS_BACK', 1)
    analyze_positive_news_mentions(days)
    analyze_positive_social_mentions(days)
