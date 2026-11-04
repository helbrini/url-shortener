import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="URL Shortener")

# Stockage en mémoire pour l'instant : on le remplacera par Postgres plus tard
urls: dict[str, str] = {}


class UrlIn(BaseModel):
    url: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten(payload: UrlIn):
    code = secrets.token_urlsafe(4)
    urls[code] = payload.url
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    if code not in urls:
        raise HTTPException(status_code=404, detail="Code inconnu")
    return RedirectResponse(urls[code])