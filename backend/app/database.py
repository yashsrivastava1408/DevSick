from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

from .config import settings

sqlite_url = settings.DATABASE_URL

connect_args = {}
if sqlite_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
