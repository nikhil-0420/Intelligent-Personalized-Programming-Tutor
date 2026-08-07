"""
One-time (or re-runnable) script: computes embeddings for every CurriculumChunk
that doesn't have one yet, and stores them in the DB.

Run this after seeding curriculum content, and again any time you add new chunks.
"""

from app.database import SessionLocal
from app.models.db_models import CurriculumChunk
from app.services.embeddings import embed_text


def backfill_embeddings():
    db = SessionLocal()
    try:
        chunks = db.query(CurriculumChunk).filter(CurriculumChunk.embedding.is_(None)).all()
        print(f"Found {len(chunks)} chunks without embeddings.")

        for i, chunk in enumerate(chunks):
            chunk.embedding = embed_text(chunk.content)
            if (i + 1) % 10 == 0:
                print(f"  Embedded {i + 1}/{len(chunks)}...")

        db.commit()
        print(f"Done. Embedded {len(chunks)} chunks.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()