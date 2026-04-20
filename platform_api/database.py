from sqlmodel import SQLModel, create_engine, Session
from platform_api.config import DATABASE_URL

engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
