"""
Background scheduler — runs fetch_all_feeds every hour.
This runs as a separate process alongside the API server.
Start with: python scheduler.py
"""
import time
import logging
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db
from app.fetcher import fetch_all_feeds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL", "3600"))  # default: 1 hour

if __name__ == "__main__":
    init_db()
    logging.info(f"Scheduler started. Fetching every {INTERVAL_SECONDS}s.")
    while True:
        logging.info("Starting feed fetch cycle...")
        try:
            fetch_all_feeds()
        except Exception as e:
            logging.error(f"Fetch cycle error: {e}")
        logging.info(f"Sleeping {INTERVAL_SECONDS}s until next fetch.")
        time.sleep(INTERVAL_SECONDS)
