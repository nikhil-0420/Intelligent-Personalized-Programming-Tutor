"""
RAG retrieval: given a query, find the top-k most semantically similar
curriculum chunks using cosine similarity against pre-computed embeddings.

Note: this does a full scan over all chunks for a topic (fine at 35 chunks;
if curriculum grows to thousands of chunks later, a vector DB like FAISS or
Chroma would replace this -- flagged here as a known scaling point, not a
concern at current scope).
"""

from sqlalchemy.orm import Session
from app.models.db_models import CurriculumChunk, Topic
from app.services.embeddings import embed_text, cosine_similarity


def retrieve_relevant_chunks(
    db: Session, query: str, topic_slug: str, top_k: int = 3
) -> list[dict]:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        raise ValueError(f"Unknown topic slug: {topic_slug}")

    chunks = db.query(CurriculumChunk).filter(CurriculumChunk.topic_id == topic.id).all()
    if not chunks:
        return []

    query_embedding = embed_text(query)

    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk.embedding)
        scored.append({
            "chunk_id": chunk.id,
            "content": chunk.content,
            "chunk_type": chunk.chunk_type,
            "difficulty_level": chunk.difficulty_level,
            "similarity": score,
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]