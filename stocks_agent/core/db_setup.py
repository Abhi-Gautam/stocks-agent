from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from enum import Enum as PyEnum
from datetime import datetime
from stocks_agent.core.config import config

# SQLAlchemy engine
engine = create_engine(f"sqlite:///{config.DB_PATH}", echo=False)

# Base class
Base = declarative_base()

# Enum for post_type
class PostType(PyEnum):
    news = "news"
    social = "social"

# Models
class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price_data = relationship("PriceData", back_populates="stock")

class PriceData(Base):
    __tablename__ = "price_data"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    stock = relationship("Stock", back_populates="price_data")

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    content = Column(Text)

class SocialPost(Base):
    __tablename__ = "social_posts"
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    post_id = Column(String, unique=True, nullable=False)
    symbol = Column(String, nullable=False)
    author = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

class SentimentScore(Base):
    __tablename__ = "sentiment_scores"
    id = Column(Integer, primary_key=True)
    post_type = Column(Enum(PostType), nullable=False)
    post_id = Column(Integer, nullable=False)  # Could be NewsArticle.id or SocialPost.id
    sentiment = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    analyzed_at = Column(DateTime, nullable=False)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)
    rationale = Column(Text)

class PortfolioEntry(Base):
    __tablename__ = "portfolio_entries"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    shares = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    entry_date = Column(DateTime, nullable=False)

# Session maker and helper
SessionLocal = sessionmaker(bind=engine)
def get_session():
    return SessionLocal()

# Create tables
Base.metadata.create_all(engine)

# Export
__all__ = [
    "engine", "SessionLocal", "get_session", "Base",
    "Stock", "PriceData", "NewsArticle", "SocialPost", "SentimentScore", "Recommendation", "PortfolioEntry"
]
