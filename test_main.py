from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_shorten_and_redirect():
    r = client.post("/shorten", json={"url": "https://www.google.com"})
    assert r.status_code == 200
    code = r.json()["code"]

    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://www.google.com"


def test_unknown_code():
    r = client.get("/inconnu", follow_redirects=False)
    assert r.status_code == 404


def test_invalid_payload():
    r = client.post("/shorten", json={"mauvais": "champ"})
    assert r.status_code == 422