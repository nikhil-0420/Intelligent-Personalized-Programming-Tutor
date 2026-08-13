"""
Feature extraction for the classical eval scorer.
Extracts numeric features from an interaction that a small model
(XGBoost/logistic regression) can learn to map to a 1-5 score per dimension.
"""

import numpy as np
from app.services.embeddings import embed_text, cosine_similarity


def extract_features(
    student_message: str,
    retrieved_chunks: list[str],
    p_know: float,
    tutor_response: str,
) -> dict:
    response_embedding = embed_text(tutor_response)
    chunk_embeddings = [embed_text(c) for c in retrieved_chunks]

    chunk_similarities = [
        cosine_similarity(response_embedding, ce) for ce in chunk_embeddings
    ]

    words = tutor_response.split()
    sentences = [s for s in tutor_response.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    return {
        # groundedness-relevant
        "max_chunk_similarity": max(chunk_similarities) if chunk_similarities else 0.0,
        "mean_chunk_similarity": float(np.mean(chunk_similarities)) if chunk_similarities else 0.0,
        "min_chunk_similarity": min(chunk_similarities) if chunk_similarities else 0.0,

        # pedagogical_fit-relevant
        "p_know": p_know,
        "response_word_count": len(words),
        "avg_word_length": float(np.mean([len(w) for w in words])) if words else 0.0,
        "technical_term_count": _count_technical_terms(tutor_response),

        # clarity-relevant
        "sentence_count": len(sentences),
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0.0,
        "has_punctuation_structure": int(any(p in tutor_response for p in [".", "!", "?"])),
    }


def _count_technical_terms(text: str) -> int:
    # Placeholder heuristic -- swap for a real curriculum-specific term list
    # pulled from your curriculum_data once you have it, or a CS jargon list.
    technical_terms = {
        "stack", "overflow", "invariant", "allocation", "terminating",
        "recursive", "iteration", "complexity", "asymptotic", "traversal",
    }
    return sum(1 for w in text.lower().split() if w.strip(".,!?") in technical_terms)