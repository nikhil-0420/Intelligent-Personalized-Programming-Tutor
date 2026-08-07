"""
Wraps Ollama for generating tutor responses, grounded in retrieved curriculum chunks.
"""

import ollama

MODEL_NAME = "llama3.1:8b"


def build_prompt(query: str, retrieved_chunks: list[dict], p_know: float) -> str:
    """
    Assembles a prompt that forces the model to answer using ONLY the retrieved
    context -- this is what makes grounding checkable afterward, and what
    stops the model from just answering from its own general knowledge
    (which would defeat the purpose of RAG).
    """
    context = "\n\n".join(
        f"[{c['chunk_type'].upper()}] {c['content']}" for c in retrieved_chunks
    )

    if p_know < 0.3:
        level_instruction = "The student is a beginner on this topic. Use simple language, avoid jargon, and give a concrete example."
    elif p_know < 0.6:
        level_instruction = "The student has partial understanding. Build on basics, but you can introduce more nuance."
    else:
        level_instruction = "The student has strong mastery. Be concise, focus on edge cases or deeper insight rather than re-explaining basics."

    prompt = f"""You are a programming tutor. Answer the student's question using ONLY the information in the CONTEXT below. Do not use outside knowledge. If the context doesn't fully answer the question, say what's missing.

CONTEXT:
{context}

STUDENT LEVEL: {level_instruction}

STUDENT QUESTION: {query}

Answer clearly and directly, grounded in the context above."""

    return prompt


def generate_response(query: str, retrieved_chunks: list[dict], p_know: float) -> str:
    prompt = build_prompt(query, retrieved_chunks, p_know)

    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"]