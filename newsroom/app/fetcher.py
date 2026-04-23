import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
import logging
import os

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
DAYS_LIMIT = int(os.getenv("ARTICLE_DAYS_LIMIT", "2"))

def now_sp():
    return datetime.now(SAO_PAULO).astimezone(timezone.utc).replace(tzinfo=None)

def cutoff():
    return now_sp() - timedelta(days=DAYS_LIMIT)

from .database import engine
from .models import Author, Article

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def extract_date_from_url(url: str) -> Optional[datetime]:
    """Extract publication date from URL pattern /YYYY/MM/."""
    import re as _re
    pattern = r"/([0-9]{4})/([0-9]{2})/"
    m = _re.search(pattern, url)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), 1, tzinfo=timezone.utc).replace(tzinfo=None)
        except Exception:
            pass
    return None


def fetch_article_date_estadao(url: str) -> Optional[datetime]:
    """Fetch date from Estadão article JSON-LD (only for scrape mode)."""
    import json as _json
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        from bs4 import BeautifulSoup as _BS
        soup = _BS(resp.text, "html.parser")
        for s in soup.find_all("script", type="application/ld+json"):
            try:
                d = _json.loads(s.string)
                dp = d.get("datePublished") or d.get("dateCreated")
                if dp:
                    from datetime import datetime as _dt
                    # Parse ISO format like 2026-04-22T20:00:00-03:00
                    dt = _dt.fromisoformat(dp)
                    return dt.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
    except Exception:
        pass
    return None


def parse_date(entry) -> Optional[datetime]:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
    return None


def fetch_rss(author: Author, session: Session):
    logger.info(f"RSS fetch: {author.name} → {author.rss_url}")
    feed = feedparser.parse(author.rss_url, request_headers=HEADERS)
    saved = 0
    limit = None if author.ignore_date_filter else cutoff()
    for entry in feed.entries[:author.max_articles]:
        url = entry.get("link", "")
        if not url:
            continue
        pub = parse_date(entry)
        if limit and pub and pub < limit:
            continue
        existing = session.exec(select(Article).where(Article.url == url)).first()
        if existing:
            continue
        article = Article(
            author_id=author.id,
            title=entry.get("title", "Sem título"),
            url=url,
            summary=_clean_summary(entry.get("summary", "")),
            published_at=pub,
            tags=author.tags,
        )
        session.add(article)
        saved += 1
    session.commit()
    logger.info(f"  → saved {saved} new articles for {author.name}")


def fetch_filtered_feed(author: Author, session: Session):
    logger.info(f"Filtered feed: {author.name} → {author.filter_feed_url}")
    feed = feedparser.parse(author.filter_feed_url, request_headers=HEADERS)
    byline = (author.filter_byline or author.name).lower()
    saved = 0
    limit = None if author.ignore_date_filter else cutoff()
    for entry in feed.entries[:max(author.max_articles * 5, 50)]:
        author_field = (
            entry.get("author", "")
            + entry.get("dc_creator", "")
            + entry.get("title", "")
        ).lower()
        if byline not in author_field:
            continue
        url = entry.get("link", "")
        if not url:
            continue
        pub = parse_date(entry)
        if limit and pub and pub < limit:
            continue
        existing = session.exec(select(Article).where(Article.url == url)).first()
        if existing:
            continue
        article = Article(
            author_id=author.id,
            title=entry.get("title", "Sem título"),
            url=url,
            summary=_clean_summary(entry.get("summary", "")),
            published_at=pub,
            tags=author.tags,
        )
        session.add(article)
        saved += 1
    session.commit()
    logger.info(f"  → saved {saved} new articles for {author.name}")


def fetch_scrape(author: Author, session: Session):
    """Scrape author page. Handles Estadão (by URL pattern) and O Globo."""
    logger.info(f"Scraping: {author.name} → {author.scrape_url}")
    try:
        resp = httpx.get(author.scrape_url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"  Scrape error for {author.name}: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    saved = 0
    is_estadao = "estadao.com.br" in author.scrape_url
    url_pattern = author.filter_byline  # reused field: URL pattern filter
    seen = set()

    # O Globo: use feed-post-link class which has correct titles
    # Estadão: use all links and filter by URL pattern
    selector = "a[href]" if is_estadao else "a.feed-post-link[href]"

    for a in soup.select(selector):
        href = a.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            base = "https://www.estadao.com.br" if is_estadao else "https://oglobo.globo.com"
            href = base + href
        if not href.startswith("http"):
            continue

        # Filter by URL pattern
        if url_pattern and url_pattern not in href:
            continue

        # Skip author index page
        if href.rstrip("/") == author.scrape_url.rstrip("/"):
            continue

        # Get title first — skip if empty
        title = a.get_text(strip=True)
        if not is_estadao:
            # For O Globo feed-post-link, text IS the title
            pass
        else:
            # For Estadão, look for a heading inside the link
            title_el = a.find(["h2", "h3", "h4"])
            if title_el:
                title = title_el.get_text(strip=True)
        title = title.strip()
        if len(title) < 10:
            continue

        if href in seen:
            continue
        seen.add(href)

        existing = session.exec(select(Article).where(Article.url == href)).first()
        if existing:
            continue

        # Extract date from URL or fetch from article
        if is_estadao:
            pub_date = fetch_article_date_estadao(href)
        else:
            pub_date = extract_date_from_url(href) or now_sp()

        article = Article(
            author_id=author.id,
            title=title,
            url=href,
            published_at=pub_date or now_sp(),
            tags=author.tags,
        )
        session.add(article)
        saved += 1
        if saved >= author.max_articles:
            break

    session.commit()
    logger.info(f"  → saved {saved} new articles for {author.name}")


def _clean_summary(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)[:800]


def fetch_all_feeds():
    with Session(engine) as session:
        authors = session.exec(select(Author).where(Author.active == True)).all()
        logger.info(f"Fetching feeds for {len(authors)} authors...")
        for author in authors:
            try:
                if author.fetch_mode == "rss" and author.rss_url:
                    fetch_rss(author, session)
                elif author.fetch_mode == "filter" and author.filter_feed_url:
                    fetch_filtered_feed(author, session)
                elif author.fetch_mode == "scrape" and author.scrape_url:
                    fetch_scrape(author, session)
            except Exception as e:
                logger.error(f"Error fetching {author.name}: {e}")
        logger.info("All feeds fetched.")
