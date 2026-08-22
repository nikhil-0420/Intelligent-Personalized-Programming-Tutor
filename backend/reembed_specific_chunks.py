"""
Targeted fix: re-embeds chunk ids 23 and 25 directly, bypassing the
NULL-detection query in embed_chunks.py (which doesn't catch these rows --
see note below).

Why the normal backfill missed them: SQLAlchemy's JSON column type stores
Python None as a literal JSON 'null' value, not SQL NULL, unless the column
is declared with JSON(none_as_null=True). So `embedding IS NULL` in SQL
doesn't match rows that were cleared via `chunk.embedding = None`, even
though the Python-side value reads back as None.
"""

from app.database import SessionLocal
from app.models.db_models import CurriculumChunk
from app.services.embeddings import embed_text

CHUNK_IDS = [23, 25]


def reembed_specific_chunks():
    db = SessionLocal()
    try:
        for chunk_id in CHUNK_IDS:
            chunk = db.query(CurriculumChunk).filter(CurriculumChunk.id == chunk_id).first()
            if chunk is None:
                print(f"chunk id {chunk_id}: NOT FOUND, skipping")
                continue

            chunk.embedding = embed_text(chunk.content)
            print(f"chunk id {chunk_id}: re-embedded (dim={len(chunk.embedding)})")

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    reembed_specific_chunks()