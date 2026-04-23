from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json


class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    venue: str
    page_url: Optional[str] = None
    rss_url: Optional[str] = None
    scrape_url: Optional[str] = None        # for authors without RSS
    fetch_mode: str = "rss"                  # "rss" | "scrape" | "filter"
    filter_feed_url: Optional[str] = None   # for filtered feeds (e.g. NYT Opinion)
    filter_byline: Optional[str] = None     # filter articles by this byline string
    tags: str = "[]"                         # JSON list of strings
    color: Optional[str] = None
    active: bool = True
    max_articles: int = 10
    ignore_date_filter: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    articles: List["Article"] = Relationship(back_populates="author")

    def get_tags(self) -> List[str]:
        return json.loads(self.tags)

    def set_tags(self, tags: List[str]):
        self.tags = json.dumps(tags, ensure_ascii=False)


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="author.id")
    title: str
    url: str = Field(unique=True)
    summary: Optional[str] = None
    ai_summary: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    is_favorite: bool = False
    tags: str = "[]"

    author: Optional[Author] = Relationship(back_populates="articles")

    def get_tags(self) -> List[str]:
        return json.loads(self.tags)
