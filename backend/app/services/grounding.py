"""
Grounding audit: checks whether a generated response actually reflects the
retrieved context, rather than the model ignoring it and hallucinating from
general knowledge.

Approach: embed the response, compare its similarity against the retrieved
chunks it was supposedly grounded in. Above threshold = grounded.
This is a heuristic, not a proof -- flagged in your write-up as a starting
point, with LLM-as-judge (Phase #10) as the more rigorous follow-up check.
"""

from app.services.embeddings import embed_text, cosine_similarity

GROUNDING_THRESHOLD = 0.35


def compute_grounding_score(response: str, retrieved_chunks: list[dict]) -> float:
    if not retrieved_chunks:
        return 0.0

    response_embedding = embed_text(response)

    similarities = [
        cosine_similarity(response_embedding, embed_text(c["content"]))
        for c in retrieved_chunks
    ]

    # Use max, not average -- response only needs to align with the most
    # relevant chunk, not all of them equally.
    return max(similarities)


def is_grounded(response: str, retrieved_chunks: list[dict]) -> bool:
    return compute_grounding_score(response, retrieved_chunks) >= GROUNDING_THRESHOLD