import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from platform_api.database import get_session
from platform_api.main import app


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session):
    def _get_session():
        yield session

    app.dependency_overrides[get_session] = _get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
