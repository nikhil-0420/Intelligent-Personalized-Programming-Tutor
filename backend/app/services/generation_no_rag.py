"""
No-RAG ablation variant. Same model, same prompt structure, but with
NO retrieved curriculum context -- isolates what RAG actually contributes
versus the LLM answering from its own general knowledge.
"""

import ollama

MODEL_NAME = "llama3.1:8b"


def build_no_rag_prompt(query: str, topic_title: str, p_know: float) -> str:
    if p_know < 0.3:
        level_instruction = "The student is a beginner on this topic. Use simple language, avoid jargon, and give a concrete example."
    elif p_know < 0.6:
        level_instruction = "The student has partial understanding. Build on basics, but you can introduce more nuance."
    else:
        level_instruction = "The student has strong mastery. Be concise, focus on edge cases or deeper insight rather than re-explaining basics."

    # Deliberately NO context block here -- this is the entire point of the ablation
    prompt = f"""You are a programming tutor. Answer the student's question about {topic_title}.

STUDENT LEVEL: {level_instruction}

STUDENT QUESTION: {query}

Answer clearly and directly."""

    return prompt


def generate_response_no_rag(query: str, topic_title: str, p_know: float) -> str:
    prompt = build_no_rag_prompt(query, topic_title, p_know)
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"]