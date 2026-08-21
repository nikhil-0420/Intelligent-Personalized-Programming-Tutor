"""
One-time migration: adds the interaction_type column to the existing
Postgres interactions table (SQLAlchemy's create_all() only creates
missing tables, never alters existing ones).
"""

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE interactions ADD COLUMN IF NOT EXISTS interaction_type VARCHAR DEFAULT 'explanation'"
    ))
    conn.commit()

print("Migration complete: interaction_type column added.")