"""
Loads curriculum_data/dsa_topics.json into the DB (Topic + CurriculumChunk rows).

Run this once after init_db() to populate topics and RAG-retrievable content.
Re-running is safe -- it skips topics that already exist by slug.
"""

import json
import os
from sqlalchemy.orm import Session
from app.models.db_models import Topic, CurriculumChunk

CURRICULUM_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "curriculum_data", "dsa_topics.json"
)


def seed_curriculum(db: Session):
    with open(CURRICULUM_FILE, "r") as f:
        data = json.load(f)

    created, skipped = 0, 0

    for topic_data in data["topics"]:
        existing = db.query(Topic).filter(Topic.slug == topic_data["slug"]).first()
        if existing:
            skipped += 1
            continue

        topic = Topic(
            slug=topic_data["slug"],
            title=topic_data["title"],
            description=topic_data["description"],
            difficulty_level=topic_data["difficulty_level"],
            prerequisites=topic_data["prerequisites"],
        )
        db.add(topic)
        db.flush()  # get topic.id before inserting chunks

        for chunk_data in topic_data["chunks"]:
            chunk = CurriculumChunk(
                topic_id=topic.id,
                content=chunk_data["content"],
                difficulty_level=chunk_data["difficulty_level"],
                chunk_type=chunk_data["chunk_type"],
                source_file="dsa_topics.json",
            )
            db.add(chunk)

        created += 1

    db.commit()
    print(f"Curriculum seed complete: {created} topics created, {skipped} already existed.")


if __name__ == "__main__":
    from app.database import SessionLocal, init_db

    init_db()
    db = SessionLocal()
    try:
        seed_curriculum(db)
    finally:
        db.close()
