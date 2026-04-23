from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .database import init_db
from .routers import authors, articles
from .fetcher import fetch_all_feeds

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Newsroom API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authors.router, prefix="/authors", tags=["authors"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])

@app.get("/")
def root():
    return {"status": "ok", "app": "Newsroom API"}

@app.post("/fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger fetching of all feeds."""
    background_tasks.add_task(fetch_all_feeds)
    return {"status": "fetching started"}

from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi.responses import JSONResponse
from fastapi import Request

@app.middleware("http")
async def add_charset(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response
