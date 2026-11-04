import os
import secrets
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://shortener:shortener@localhost:5432/shortener",
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
    with get_conn() as conn:
        row = conn.execute(
            "SELECT url FROM urls WHERE code = %s", (code,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Code inconnu")
    return RedirectResponse(row[0])
