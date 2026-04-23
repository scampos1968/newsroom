from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
import json

from ..database import get_session
from ..models import Author

router = APIRouter()


class AuthorCreate(BaseModel):
    name: str
    venue: str
    page_url: Optional[str] = None
    rss_url: Optional[str] = None
    scrape_url: Optional[str] = None
    fetch_mode: str = "rss"
    filter_feed_url: Optional[str] = None
    filter_byline: Optional[str] = None
    tags: List[str] = []
    color: Optional[str] = None


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    venue: Optional[str] = None
    page_url: Optional[str] = None
    rss_url: Optional[str] = None
    scrape_url: Optional[str] = None
    fetch_mode: Optional[str] = None
    filter_feed_url: Optional[str] = None
    filter_byline: Optional[str] = None
    tags: Optional[List[str]] = None
    active: Optional[bool] = None


class AuthorOut(BaseModel):
    id: int
    name: str
    venue: str
    page_url: Optional[str]
    rss_url: Optional[str]
    fetch_mode: str
    tags: List[str]
    active: bool
    article_count: int = 0

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AuthorOut])
def list_authors(session: Session = Depends(get_session)):
    authors = session.exec(select(Author)).all()
    result = []
    for a in authors:
        out = AuthorOut(
            id=a.id,
            name=a.name,
            venue=a.venue,
            page_url=a.page_url,
            rss_url=a.rss_url,
            fetch_mode=a.fetch_mode,
            tags=a.get_tags(),
            active=a.active,
            article_count=len(a.articles),
        )
        result.append(out)
    return result


@router.post("/", response_model=AuthorOut, status_code=201)
def create_author(data: AuthorCreate, session: Session = Depends(get_session)):
    author = Author(
        name=data.name,
        venue=data.venue,
        page_url=data.page_url,
        rss_url=data.rss_url,
        scrape_url=data.scrape_url,
        fetch_mode=data.fetch_mode,
        filter_feed_url=data.filter_feed_url,
        filter_byline=data.filter_byline,
        tags=json.dumps(data.tags, ensure_ascii=False),
        color=data.color,
    )
    session.add(author)
    session.commit()
    session.refresh(author)
    return AuthorOut(
        id=author.id,
        name=author.name,
        venue=author.venue,
        page_url=author.page_url,
        rss_url=author.rss_url,
        fetch_mode=author.fetch_mode,
        tags=author.get_tags(),
        active=author.active,
    )


@router.patch("/{author_id}", response_model=AuthorOut)
def update_author(
    author_id: int, data: AuthorUpdate, session: Session = Depends(get_session)
):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    for field, value in data.model_dump(exclude_none=True).items():
        if field == "tags":
            author.tags = json.dumps(value, ensure_ascii=False)
        else:
            setattr(author, field, value)
    session.add(author)
    session.commit()
    session.refresh(author)
    return AuthorOut(
        id=author.id,
        name=author.name,
        venue=author.venue,
        page_url=author.page_url,
        rss_url=author.rss_url,
        fetch_mode=author.fetch_mode,
        tags=author.get_tags(),
        active=author.active,
    )


@router.delete("/{author_id}", status_code=204)
def delete_author(author_id: int, session: Session = Depends(get_session)):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    session.delete(author)
    session.commit()
