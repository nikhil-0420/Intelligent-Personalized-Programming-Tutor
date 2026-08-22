"""
Diagnostic: checks the current embedding state of chunk ids 23 and 25
directly, and reports which DATABASE_URL this script is actually using.
"""

import os
from app.database import SessionLocal, DATABASE_URL
from app.models.db_models import CurriculumChunk

print(f"DATABASE_URL in use: {DATABASE_URL}")

db = SessionLocal()
try:
    for chunk_id in [23, 25]:
        chunk = db.query(CurriculumChunk).filter(CurriculumChunk.id == chunk_id).first()
        if chunk is None:
            print(f"chunk id {chunk_id}: NOT FOUND")
            continue
        emb = chunk.embedding
        print(f"chunk id {chunk_id}: embedding is {'NULL' if emb is None else f'SET (len={len(emb)})'}")
        print(f"  content preview: {chunk.content[:80]}")

    total_null = db.query(CurriculumChunk).filter(CurriculumChunk.embedding.is_(None)).count()
    print(f"\nTotal chunks with NULL embedding (server-side count): {total_null}")
finally:
    db.close()