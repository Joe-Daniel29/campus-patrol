import os

# Must be set before the app is imported so the engine points at in-memory SQLite.
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"
os.environ["INGEST_TOKEN"] = ""

import pytest
from fastapi.testclient import TestClient

from app import models  # noqa: F401
from app.db import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture()
def zone(client):
    return client.post("/api/zones", json={"name": "Library", "x": 10, "y": 10}).json()


@pytest.fixture()
def rover(client):
    return client.post("/api/rovers", json={"name": "rover-01"}).json()
