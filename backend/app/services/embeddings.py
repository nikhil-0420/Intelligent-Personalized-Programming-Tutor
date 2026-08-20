"""
Local embedding generation using sentence-transformers.
Model downloads once (~80MB) on first run, then caches locally — free, no API.
Forced to CPU to avoid VRAM contention with Ollama's Llama 3.1 8B locally.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _model


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))