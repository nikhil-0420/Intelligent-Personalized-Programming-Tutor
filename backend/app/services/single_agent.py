"""
Single-agent baseline for the multi-agent ablation. One LLM call that
both judges the student's message (is_attempt, correct) AND generates
the tutor's response, in one shot -- mirroring what Assessor + Tutor
do as two separate calls in the real pipeline.
"""

import json
import re
import ollama

MODEL_NAME = "llama3.1:8b"


def build_single_agent_prompt(student_message: str, topic_title: str, context: str, p_know: float) -> str:
    if p_know < 0.3:
        level_instruction = "The student is a beginner. Use simple language, avoid jargon, give a concrete example."
    elif p_know < 0.6:
        level_instruction = "The student has partial understanding. Build on basics but can introduce nuance."
    else:
        level_instruction = "The student has strong mastery. Be concise, focus on edge cases or deeper insight."

    return f"""You are a programming tutor. You must do TWO things at once for the student's message below:
1. Judge whether the message is a knowledge attempt (a claim/answer to evaluate) or not (a question, acknowledgment, etc.), and if it is, whether it's correct.
2. Generate a helpful tutor response to the student.

TOPIC: {topic_title}

RELEVANT CURRICULUM CONTEXT:
{context}

STUDENT LEVEL: {level_instruction}

STUDENT MESSAGE: "{student_message}"

Respond with ONLY a JSON object in this exact format, no other text, no markdown fences:
{{"is_attempt": true or false, "correct": true, false, or null, "tutor_response": "your response text here"}}

Rules:
- If is_attempt is true, correct MUST be true or false (never null).
- If is_attempt is false, correct MUST be null.
- tutor_response should directly address the student's message, using the curriculum context, matching the student's level.

Output:"""


def single_agent_interact(student_message: str, topic_title: str, context: str, p_know: float) -> dict:
    prompt = build_single_agent_prompt(student_message, topic_title, context, p_know)

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
        options={"temperature": 0},
    )
    raw_text = response["response"].strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return {"is_attempt": None, "correct": None, "tutor_response": None, "error": "no JSON found"}

    try:
        parsed = json.loads(match.group())
    except json.JSONDecodeError as e:
        return {"is_attempt": None, "correct": None, "tutor_response": None, "error": f"JSON parse error: {e}"}

    return {
        "is_attempt": parsed.get("is_attempt"),
        "correct": parsed.get("correct"),
        "tutor_response": parsed.get("tutor_response"),
        "error": None,
    }