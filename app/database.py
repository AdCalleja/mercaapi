from sqlmodel import create_engine, Session
from functools import lru_cache
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/db/mercadona.db")


@lru_cache()
def get_engine(db_url: str = DATABASE_URL):
    return create_engine(db_url, connect_args={"check_same_thread": False})


def get_session():
    engine = get_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session
