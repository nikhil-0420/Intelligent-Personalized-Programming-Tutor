"""
Assessor Agent.

Kept as a separate LLM call from the Tutor Agent on purpose: the tutor's job
is to explain, the assessor's job is to judge correctness. This separation
means a bug or bias in how the tutor phrases things doesn't contaminate the
correctness judgment used to update BKT.
"""

import ollama
import json
import re

MODEL_NAME = "llama3.1:8b"


def build_assessor_prompt(student_message: str, topic_title: str, retrieved_context: str) -> str:
    return f"""You are an assessment agent for a programming tutor. Judge ONLY the student's message below. Do not explain or teach anything.

TOPIC: {topic_title}

RELEVANT CURRICULUM CONTEXT:
{retrieved_context}

EXAMPLES OF CORRECT OUTPUT FORMAT:

Student message: "What is a base case?"
Output: {{"is_attempt": false, "correct": null, "reasoning": "This is a question, not an attempt to answer or explain anything."}}

Student message: "A base case stops the recursion from running forever."
Output: {{"is_attempt": true, "correct": true, "reasoning": "This correctly describes the purpose of a base case."}}

Student message: "Recursion never needs a stopping point, it just runs until the answer is found."
Output: {{"is_attempt": true, "correct": false, "reasoning": "This is incorrect -- recursion requires a base case to stop, contradicting the context."}}

NOW ASSESS THIS MESSAGE:
Student message: "{student_message}"

Rules:
- If is_attempt is true, correct MUST be true or false (never null).
- If is_attempt is false, correct MUST be null.
- Respond with ONLY the JSON object, no other text, no markdown fences.

Output:"""


def _extract_json(text: str) -> dict:
    """
    LLMs sometimes wrap JSON in markdown fences or add stray text despite
    instructions. Extract the first {...} block defensively.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in assessor response: {text}")
    return json.loads(match.group(0))


def assess_message(student_message: str, topic_title: str, retrieved_context: str) -> dict:
    prompt = build_assessor_prompt(student_message, topic_title, retrieved_context)

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
        options={"temperature": 0},
    )
    raw_text = response["response"]

    try:
        parsed = _extract_json(raw_text)
    except (ValueError, json.JSONDecodeError):
        return {
            "is_attempt": False,
            "correct": None,
            "reasoning": f"Assessor parse failure, defaulted to not-an-attempt. Raw: {raw_text[:100]}",
        }

    is_attempt = bool(parsed.get("is_attempt", False))
    correct = parsed.get("correct", None)

    # Consistency guard: if the model says it's an attempt but left correct
    # as null (the exact bug we just saw), don't silently accept it --
    # treat as an assessor failure rather than propagating bad data into BKT.
    if is_attempt and correct is None:
        return {
            "is_attempt": False,
            "correct": None,
            "reasoning": f"Assessor inconsistency (is_attempt=true but correct=null), defaulted to not-an-attempt. Raw: {raw_text[:150]}",
        }

    return {
        "is_attempt": is_attempt,
        "correct": correct,
        "reasoning": parsed.get("reasoning", ""),
    }