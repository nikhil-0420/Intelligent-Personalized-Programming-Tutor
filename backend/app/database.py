"""
DB session setup. SQLite for local dev — swap DATABASE_URL for Postgres later
if you need concurrent access (e.g. once you deploy, same pattern as your
accident project's move from local dev to Render).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./tutor.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.db_models import Base
    Base.metadata.create_all(bind=engine)
