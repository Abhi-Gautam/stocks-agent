from stocks_agent.core.db_setup import Base, engine
from stocks_agent.data_acquisition.news_data import run_news_pipeline
from stocks_agent.data_acquisition.social_media import run_social_pipeline
from stocks_agent.core.config import config

# usernames for social media
USERNAMES = ["VVVStockAnalyst", "stocksgeeks", "accuracy_Invst"]

def empty_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def main():
    print("Emptying database...")
    empty_database()
    print("Parsing news articles...")
    # run_news_pipeline()
    print("Parsing social media posts...")
    run_social_pipeline(USERNAMES)
    print("Done.")

if __name__ == "__main__":
    main()
