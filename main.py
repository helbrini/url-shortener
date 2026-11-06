import os
import secrets
from contextlib import asynccontextmanager

import psycopg
import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://shortener:shortener@localhost:5432/shortener",
)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = 3600  # un lien reste 1 heure dans le cache

cache = redis.Redis.from_url(
    REDIS_URL,
    socket_connect_timeout=1,
    socket_timeout=1,
    decode_responses=True,
)


def get_conn():
    return psycopg.connect(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                code TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)


class UrlIn(BaseModel):
    url: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten(payload: UrlIn):
    code = secrets.token_urlsafe(4)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO urls (code, url) VALUES (%s, %s)",
            (code, payload.url),
        )
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    # 1. On regarde d'abord dans le cache
    try:
        cached = cache.get(code)
    except redis.RedisError:
        cached = None  # Redis est en panne : on continue sans lui
    if cached:
        return RedirectResponse(cached)

    # 2. Sinon on interroge Postgres
    with get_conn() as conn:
        row = conn.execute(
            "SELECT url FROM urls WHERE code = %s", (code,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Code inconnu")

    # 3. On range le résultat dans le cache pour la prochaine fois
    try:
        cache.set(code, row[0], ex=CACHE_TTL)
    except redis.RedisError:
        pass
    return RedirectResponse(row[0])