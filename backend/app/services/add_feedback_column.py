"""
One-off migration: adds the `feedback` column to the existing `interactions`
table in Postgres. Needed because init_db() uses Base.metadata.create_all(),
which only creates missing tables -- it does not alter existing ones.

Run this once after deploying the updated db_models.py.
"""

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS feedback VARCHAR;"))
    conn.commit()

print("Done. 'feedback' column added to interactions table (or already existed).")