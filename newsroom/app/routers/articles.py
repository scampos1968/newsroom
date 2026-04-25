from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from ..database import get_session
from ..models import Article, Author, DeletedArticle

router = APIRouter()


class ArticleOut(BaseModel):
    id: int
    author_id: int
    author_name: str
    author_venue: str
    title: str
    url: str
    summary: Optional[str]
    ai_summary: Optional[str]
    published_at: Optional[datetime]
    fetched_at: datetime
    is_read: bool
    is_favorite: bool
    tags: List[str]

    class Config:
        from_attributes = True


def _to_out(article: Article, author: Author) -> ArticleOut:
    return ArticleOut(
        id=article.id,
        author_id=article.author_id,
        author_name=author.name,
        author_venue=author.venue,
        title=article.title,
        url=article.url,
        summary=article.summary,
        ai_summary=article.ai_summary,
        published_at=article.published_at,
        fetched_at=article.fetched_at,
        is_read=article.is_read,
        is_favorite=article.is_favorite,
        tags=article.get_tags(),
    )


@router.get("/", response_model=List[ArticleOut])
def list_articles(
    author_id: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    favorites_only: bool = Query(False),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    session: Session = Depends(get_session),
):
    query = select(Article, Author).join(Author).where(Author.active == True)

    if author_id:
        query = query.where(Article.author_id == author_id)
    if unread_only:
        query = query.where(Article.is_read == False)
    if favorites_only:
        query = query.where(Article.is_favorite == True)

    query = query.order_by(Article.is_read.asc(), Article.published_at.desc()).offset(offset).limit(limit)
    rows = session.exec(query).all()

    results = []
    for article, author in rows:
        if tag:
            tags = article.get_tags()
            if tag not in tags:
                continue
        results.append(_to_out(article, author))
    return results


@router.patch("/{article_id}/read")
def mark_read(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.is_read = not article.is_read
    session.add(article)
    session.commit()
    return {"is_read": article.is_read}


@router.patch("/{article_id}/favorite")
def toggle_favorite(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.is_favorite = not article.is_favorite
    session.add(article)
    session.commit()
    return {"is_favorite": article.is_favorite}


@router.delete("/{article_id}", status_code=204)
def delete_article(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if not session.get(DeletedArticle, article.url):
        session.add(DeletedArticle(url=article.url))
    session.delete(article)
    session.commit()
