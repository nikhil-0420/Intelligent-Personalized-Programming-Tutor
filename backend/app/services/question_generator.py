"""
Generates a grounded practice question for a topic -- a deliberately
separate flow from tutor.generate_response(), triggered explicitly
(e.g. a "Check my understanding" button), not appended to every explanation.
"""

from app.services.llm_client import generate_text


def build_question_prompt(topic_title: str, retrieved_chunks: list[dict], p_know: float) -> str:
    context = "\n\n".join(
        f"[{c['chunk_type'].upper()}] {c['content']}" for c in retrieved_chunks
    )

    if p_know < 0.3:
        difficulty_instruction = "Ask a simple, foundational question testing basic understanding."
    elif p_know < 0.6:
        difficulty_instruction = "Ask a moderately challenging question that requires applying the concept, not just recalling it."
    else:
        difficulty_instruction = "Ask a challenging question involving an edge case or a subtle distinction."

    return f"""You are a programming tutor creating a practice question, grounded ONLY in the context below.

TOPIC: {topic_title}

CONTEXT:
{context}

DIFFICULTY: {difficulty_instruction}

Write ONE clear, specific question to test the student's understanding of this topic. Do not answer it yourself. Do not include any preamble like "Here's a question" -- just the question itself."""


def generate_question(topic_title: str, retrieved_chunks: list[dict], p_know: float) -> str:
    prompt = build_question_prompt(topic_title, retrieved_chunks, p_know)
    return generate_text(prompt, temperature=0.8).strip()