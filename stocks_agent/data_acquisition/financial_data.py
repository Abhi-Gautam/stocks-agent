import pandas as pd
import yfinance as yf
import datetime
from stocks_agent.core.db_setup import SessionLocal, Stock, PriceData
from stocks_agent.core.config import config

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_stock(session, symbol: str, name: str = None) -> Stock:
    stock = session.query(Stock).filter_by(symbol=symbol).first()
    if stock:
        return stock
    stock = Stock(symbol=symbol, name=name or symbol)
    session.add(stock)
    session.commit()
    return stock

def fetch_price_data(symbol: str, start: datetime.date, end: datetime.date):
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, interval="1d")
    if df.empty:
        logger.warning(f"No price data found for {symbol} from {start} to {end}")
        return df
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    return df

def store_price_data(symbol: str, start: datetime.date, end: datetime.date):
    with SessionLocal() as session:
        stock = get_or_create_stock(session, symbol)
        df = fetch_price_data(symbol, start, end)
        if df is None or df.empty:
            return
        for dt, row in df.iterrows():
            price = PriceData(
                stock_id=stock.id,
                datetime=dt.to_pydatetime() if hasattr(dt, 'to_pydatetime') else dt,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=int(row['volume'])
            )
            session.add(price)
        session.commit()

def fetch_and_store_today(symbol: str):
    today = datetime.date.today()
    store_price_data(symbol, today, today + datetime.timedelta(days=1))

if __name__ == "__main__":
    try:
        SYMBOLS = getattr(config, 'SYMBOLS', ['AAPL', 'GOOGL', 'MSFT'])
    except Exception:
        SYMBOLS = ['AAPL', 'GOOGL', 'MSFT']
    end = datetime.date.today()
    start = end - datetime.timedelta(days=30)
    for symbol in SYMBOLS:
        try:
            logger.info(f"Fetching and storing price data for {symbol}")
            store_price_data(symbol, start, end)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
