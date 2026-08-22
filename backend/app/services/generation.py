"""
Wraps the unified LLM client for generating tutor responses, grounded in
retrieved curriculum chunks. Routes to Ollama (local dev) or Groq (hosted
demo) via llm_client, based on LLM_PROVIDER env var -- prompts unchanged
either way.
"""

from app.services.llm_client import generate_text


def build_prompt(query: str, retrieved_chunks: list[dict], p_know: float) -> str:
    context = "\n\n".join(
        f"[{c['chunk_type'].upper()}] {c['content']}" for c in retrieved_chunks
    )

    if p_know < 0.3:
        level_instruction = "The student is a beginner on this topic. Use simple language, avoid jargon, and give a concrete example."
    elif p_know < 0.6:
        level_instruction = "The student has partial understanding. Build on basics, but you can introduce more nuance."
    else:
        level_instruction = "The student has strong mastery. Be concise, focus on edge cases or deeper insight rather than re-explaining basics."

    prompt = f"""You are a programming tutor. Answer the student's question using ONLY the concepts, definitions, and procedures in the CONTEXT below. Do not use outside knowledge. If the context doesn't fully answer the question, say what's missing.

If the student's question asks you to trace through a specific input (e.g. "what does the array look like after pass N", "what is the output step by step"), you must work through that exact input yourself, one step at a time, applying the procedure described in the context. Do NOT copy a numeric result from a worked example in the context unless the student's input is identical to that example's input -- treat any example arrays/values in the context as illustrations of the *procedure*, not as answers to reuse. Show your intermediate state at each step before giving the final state.

CONTEXT:
{context}

STUDENT LEVEL: {level_instruction}

STUDENT QUESTION: {query}

Answer clearly and directly, grounded in the context above."""

    return prompt


def generate_response(query: str, retrieved_chunks: list[dict], p_know: float) -> str:
    prompt = build_prompt(query, retrieved_chunks, p_know)
    return generate_text(prompt, temperature=0.7)

def build_intro_prompt(topic_title: str, retrieved_chunks: list[dict], p_know: float) -> str:
    context = "\n\n".join(
        f"[{c['chunk_type'].upper()}] {c['content']}" for c in retrieved_chunks
    )

    if p_know < 0.3:
        level_instruction = "The student is new to this topic. Keep it short, simple, and welcoming -- a brief orientation, not a full lecture."
    elif p_know < 0.6:
        level_instruction = "The student has partial understanding. Briefly recap the core idea, then note what's often trickier about it."
    else:
        level_instruction = "The student already has strong mastery here. Keep this very brief -- a one-line reminder of the topic's core idea is enough."

    prompt = f"""You are a programming tutor. Give a brief overview of the topic below, grounded ONLY in the CONTEXT provided. This is an introduction, not an answer to a specific question -- keep it to 2-4 sentences.

TOPIC: {topic_title}

CONTEXT:
{context}

STUDENT LEVEL: {level_instruction}

Do not end with a question or a call to action -- just give the overview itself."""

    return prompt


def generate_topic_intro(topic_title: str, retrieved_chunks: list[dict], p_know: float) -> str:
    prompt = build_intro_prompt(topic_title, retrieved_chunks, p_know)
    return generate_text(prompt, temperature=0.7)