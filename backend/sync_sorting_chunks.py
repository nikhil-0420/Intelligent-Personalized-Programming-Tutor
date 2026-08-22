"""
One-off: pushes the updated selection-sort and bubble-sort chunk content
from curriculum_data/dsa_topics.json into Postgres, and clears their stored
embedding so embed_chunks.py re-embeds them on its next run.

Run this once after replacing dsa_topics.json, then run embed_chunks.py.
"""

import json
import os
from app.database import SessionLocal
from app.models.db_models import Topic, CurriculumChunk

CURRICULUM_FILE = os.path.join(
    os.path.dirname(__file__), "curriculum_data", "dsa_topics.json"
)

# chunk indices within the "sorting" topic that were edited
EDITED_CHUNK_INDICES = [8, 10]  # bubble sort, selection sort


def sync_edited_chunks():
    with open(CURRICULUM_FILE, "r") as f:
        data = json.load(f)

    sorting_topic_data = next(t for t in data["topics"] if t["slug"] == "sorting")

    db = SessionLocal()
    try:
        topic = db.query(Topic).filter(Topic.slug == "sorting").first()
        if not topic:
            print("No 'sorting' topic found in DB -- nothing to sync.")
            return

        # pull chunks for this topic in the same order they were seeded
        db_chunks = (
            db.query(CurriculumChunk)
            .filter(CurriculumChunk.topic_id == topic.id)
            .order_by(CurriculumChunk.id.asc())
            .all()
        )

        updated = 0
        for idx in EDITED_CHUNK_INDICES:
            new_content = sorting_topic_data["chunks"][idx]["content"]
            db_chunk = db_chunks[idx]

            print(f"--- chunk index {idx} (db id {db_chunk.id}) ---")
            print("OLD:", db_chunk.content[:120], "...")
            print("NEW:", new_content[:120], "...")

            db_chunk.content = new_content
            db_chunk.embedding = None  # force re-embedding
            updated += 1

        db.commit()
        print(f"\nSynced {updated} chunk(s) and cleared their embeddings.")
        print("Now run: python -m app.services.embed_chunks")
    finally:
        db.close()


if __name__ == "__main__":
    sync_edited_chunks()