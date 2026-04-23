"""
Seed the database with your authors.
Run: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db, engine
from app.models import Author
from sqlmodel import Session
import json

init_db()

AUTHORS = [
    {
        "name": "Mark Gurman",
        "venue": "Bloomberg",
        "page_url": "https://www.bloomberg.com/authors/AS7Hj1mBMGM/mark-gurman",
        "rss_url": "https://www.bloomberg.com/authors/AS7Hj1mBMGM/mark-gurman.rss",
        "fetch_mode": "rss",
        "tags": ["Tecnologia", "IA"],
        "color": "av-a",
    },
    {
        "name": "Martin Wolf",
        "venue": "Financial Times",
        "page_url": "https://www.ft.com/martin-wolf",
        "rss_url": "https://www.ft.com/martin-wolf?format=rss",
        "fetch_mode": "rss",
        "tags": ["Macro", "Mercados"],
        "color": "av-b",
    },
    {
        "name": "Thomas Friedman",
        "venue": "The New York Times",
        "page_url": "https://www.nytimes.com/by/thomas-l-friedman",
        # NYT doesn't have per-columnist RSS — we filter the Opinion feed by byline
        "fetch_mode": "filter",
        "filter_feed_url": "https://rss.nytimes.com/services/xml/rss/nyt/Opinion.xml",
        "filter_byline": "Thomas L. Friedman",
        "tags": ["Política", "Macro"],
        "color": "av-c",
    },
    {
        "name": "Editorial",
        "venue": "Estadão",
        "page_url": "https://www.estadao.com.br/opiniao/editorial",
        "rss_url": "https://www.estadao.com.br/arc/outboundfeeds/rss/?outputType=json&_website=estadao&section=/opiniao",
        "fetch_mode": "rss",
        "tags": ["Política", "Macro"],
        "color": "av-d",
    },
    {
        "name": "Malu Gaspar",
        "venue": "O Globo",
        "page_url": "https://oglobo.globo.com/autores/malu-gaspar/",
        # No RSS — we scrape the author page
        "fetch_mode": "scrape",
        "scrape_url": "https://oglobo.globo.com/autores/malu-gaspar/",
        "tags": ["Política"],
        "color": "av-e",
    },
]

with Session(engine) as session:
    for data in AUTHORS:
        author = Author(
            name=data["name"],
            venue=data["venue"],
            page_url=data.get("page_url"),
            rss_url=data.get("rss_url"),
            scrape_url=data.get("scrape_url"),
            fetch_mode=data.get("fetch_mode", "rss"),
            filter_feed_url=data.get("filter_feed_url"),
            filter_byline=data.get("filter_byline"),
            tags=json.dumps(data.get("tags", []), ensure_ascii=False),
            color=data.get("color"),
        )
        session.add(author)
    session.commit()
    print(f"✓ Seeded {len(AUTHORS)} authors.")
