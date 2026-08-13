"""
LLM-as-judge scoring for tutor interactions.
Uses a separate model (Mistral) from the generator (Llama 3.1 8B) to
mitigate self-preference bias.
"""

import json
import re
import ollama

JUDGE_MODEL = "mistral"

DIMENSIONS = ["groundedness", "correctness", "pedagogical_fit", "clarity"]


def build_judge_prompt(
    student_message: str,
    retrieved_chunks: list[str],
    p_know: float,
    tutor_response: str,
) -> str:
    context = "\n".join(f"- {c}" for c in retrieved_chunks)
    mastery_label = (
        "beginner (near-zero mastery)" if p_know < 0.3
        else "partial mastery" if p_know < 0.7
        else "strong mastery"
    )

    return f"""You are an evaluation judge for a programming tutor system. Respond only in English. Score the TUTOR'S RESPONSE below on four dimensions, using ONLY the retrieved context and the student's mastery level as your reference.

STUDENT MESSAGE:
{student_message}

RETRIEVED CURRICULUM CONTEXT (the only source the tutor should have relied on):
{context}

STUDENT'S CURRENT MASTERY LEVEL: {p_know:.2f} ({mastery_label})

TUTOR'S RESPONSE TO EVALUATE:
{tutor_response}

Score each dimension from 1 (worst) to 5 (best):
1. groundedness -- relies ONLY on the retrieved context, no fabricated or outside-knowledge claims.
2. correctness -- technically accurate, judged independently of groundedness.
3. pedagogical_fit -- explanation's complexity matches the student's mastery level.
4. clarity -- well-structured and easy to follow, judged independently of correctness.

STUDY THESE FIVE EXAMPLES CAREFULLY -- each isolates a different failure mode. Match your scoring behavior to these patterns:

Example 1 (all dimensions high -- the ideal response):
Response: "A base case is what tells the recursive function when to stop. Without one, it keeps calling itself until the stack overflows."
{{"groundedness": {{"score": 5, "reasoning": "Every claim directly restates the retrieved context, nothing added."}}, "correctness": {{"score": 5, "reasoning": "Accurately restates the base case's purpose."}}, "pedagogical_fit": {{"score": 4, "reasoning": "Clear, direct language appropriate for most levels."}}, "clarity": {{"score": 5, "reasoning": "Short, direct, well-structured."}}}}

Example 2 (fabrication -- groundedness AND correctness must BOTH drop, even though part of the response is accurate):
Response: "Base cases were invented in the 1960s and are optional in Python. Without one, recursion can cause a stack overflow."
{{"groundedness": {{"score": 1, "reasoning": "The invention date and 'optional' claims are NOT in the retrieved context -- fabricated additions."}}, "correctness": {{"score": 1, "reasoning": "Base cases are NOT optional -- this directly contradicts the retrieved context. One correct sentence does not offset a false claim; correctness scores on the response's reliability as a whole, not an average of its parts."}}, "pedagogical_fit": {{"score": 2, "reasoning": "The false claims undermine any pedagogical value regardless of tone."}}, "clarity": {{"score": 3, "reasoning": "Grammatically fine but mixes true and false claims without distinction."}}}}

Example 3 (rambling but accurate -- clarity must drop even though correctness stays high):
Response: "so basically like stack overflow happens right and also the function keeps going and going and there's this thing called a base case and it stops it and yeah without it bad things happen basically it just keeps calling itself over and over"
{{"groundedness": {{"score": 4, "reasoning": "Content matches the retrieved context, though loosely expressed."}}, "correctness": {{"score": 4, "reasoning": "The underlying claims are accurate despite poor delivery."}}, "pedagogical_fit": {{"score": 2, "reasoning": "Disorganized delivery makes it hard for a student at any level to actually learn from."}}, "clarity": {{"score": 1, "reasoning": "Run-on, no structure, no punctuation separating ideas -- a reader has to work hard to extract the meaning. THIS is what a clarity score of 1 looks like: not wrong content, just badly delivered."}}}}

Example 4 (jargon mismatch -- pedagogical_fit must drop for a beginner even though correctness is high):
Response: "The base case is the terminating condition in the recursive invariant that prevents unbounded stack frame allocation."
Student mastery: beginner (near-zero mastery)
{{"groundedness": {{"score": 5, "reasoning": "Matches retrieved context."}}, "correctness": {{"score": 5, "reasoning": "Technically accurate."}}, "pedagogical_fit": {{"score": 1, "reasoning": "Dense jargon ('terminating condition', 'recursive invariant', 'stack frame allocation') is inappropriate for a near-zero-mastery beginner, even though it's correct."}}, "clarity": {{"score": 3, "reasoning": "Grammatically clear sentence structure, but clarity to WHOM matters less here than pedagogical_fit -- this example shows the two dimensions can diverge."}}}}

Example 5 (short and vague -- low on multiple dimensions for different reasons):
Response: "Yeah recursion needs that thing to stop it I think."
{{"groundedness": {{"score": 2, "reasoning": "Too vague to confirm it's actually drawing from the retrieved context."}}, "correctness": {{"score": 2, "reasoning": "Doesn't actually name or explain the base case -- too vague to verify as correct."}}, "pedagogical_fit": {{"score": 2, "reasoning": "Provides no actual teaching content regardless of level."}}, "clarity": {{"score": 2, "reasoning": "Vague and uncommitted, doesn't clearly state anything."}}}}

IMPORTANT RULES:
- Do not average partial credit. A single fabricated or contradicted claim caps groundedness AND correctness at 3, regardless of what else is accurate.
- clarity and pedagogical_fit are judged independently of correctness -- a technically correct response can still score low on either.
- Respond with ONLY the JSON object, no other text, no markdown fences, matching the exact structure shown above.

NOW SCORE THE TUTOR'S RESPONSE ABOVE. Output:"""

def judge_interaction(
    student_message: str,
    retrieved_chunks: list[str],
    p_know: float,
    tutor_response: str,
) -> dict:
    prompt = build_judge_prompt(student_message, retrieved_chunks, p_know, tutor_response)

    response = ollama.generate(
        model=JUDGE_MODEL,
        prompt=prompt,
        options={"temperature": 0},
    )
    raw_text = response["response"].strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return _fallback_result("no JSON object found in judge output")

    try:
        parsed = json.loads(match.group())
    except json.JSONDecodeError as e:
        return _fallback_result(f"JSON parse error: {e}")

    result = {}
    for dim in DIMENSIONS:
        dim_data = parsed.get(dim)
        if not isinstance(dim_data, dict) or "score" not in dim_data:
            result[dim] = {"score": None, "reasoning": f"missing or malformed '{dim}' field"}
            continue

        score = dim_data.get("score")
        if not isinstance(score, (int, float)) or not (1 <= score <= 5):
            result[dim] = {"score": None, "reasoning": f"invalid score value: {score!r}"}
            continue

        result[dim] = {
            "score": int(score),
            "reasoning": dim_data.get("reasoning", ""),
        }

    return result


def _fallback_result(error_msg: str) -> dict:
    return {dim: {"score": None, "reasoning": error_msg} for dim in DIMENSIONS}