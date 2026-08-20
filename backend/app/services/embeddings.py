"""
Local embedding generation using fastembed (ONNX runtime, not torch).
Uses the same underlying weights as sentence-transformers/all-MiniLM-L6-v2,
so embedding space and existing similarity thresholds are unchanged --
this only replaces the inference backend to cut memory usage.
"""

from fastembed import TextEmbedding
import numpy as np

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = next(model.embed([text]))
    return embedding.tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))