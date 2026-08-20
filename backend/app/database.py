"""
DB session setup. Uses DATABASE_URL env var -- defaults to local SQLite
for dev, set to a Postgres URL (e.g. from Render) for hosted deployment.
Postgres is required in production since most free hosts wipe the local
filesystem on redeploy/restart, so SQLite data wouldn't persist.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tutor.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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