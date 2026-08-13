"""
Validation set for judge_interaction() -- known-property test cases.
Each case is constructed so at least one dimension has an obvious,
non-debatable expected score. Run these BEFORE trusting the judge on
real ablation data.
"""

VALIDATION_CASES = [
    {
        "name": "clearly_ungrounded",
        "student_message": "why do we need a base case in recursion?",
        "retrieved_chunks": [
            "Recursion requires a base case that stops the recursion. "
            "Without one, the function calls itself forever until the "
            "stack overflows."
        ],
        "p_know": 0.5,
        "tutor_response": (
            "Great question! Recursion was invented by Alan Turing in 1953 "
            "as a way to reduce memory usage on early computers. Base cases "
            "are optional in most modern languages because compilers "
            "automatically detect infinite loops and terminate them safely."
        ),
        "expected": {
            "groundedness": (1, 2),  # low -- fabricated history, contradicts retrieved chunk
            "correctness": (1, 2),   # low -- factually wrong on multiple counts
        },
        "why": (
            "Every specific claim here is fabricated or contradicts the "
            "retrieved chunk directly (base cases are NOT optional, "
            "compilers do NOT auto-terminate infinite recursion). This is "
            "the clearest possible ungrounded+incorrect case."
        ),
    },
    {
        "name": "clearly_grounded_and_correct",
        "student_message": "why do we need a base case in recursion?",
        "retrieved_chunks": [
            "Recursion requires a base case that stops the recursion. "
            "Without one, the function calls itself forever until the "
            "stack overflows."
        ],
        "p_know": 0.5,
        "tutor_response": (
            "A base case is what tells the recursive function when to "
            "stop calling itself. Without one, the function keeps calling "
            "itself endlessly, and eventually the call stack runs out of "
            "space, which causes a stack overflow error."
        ),
        "expected": {
            "groundedness": (4, 5),
            "correctness": (4, 5),
        },
        "why": (
            "This is a direct, accurate restatement of the retrieved "
            "chunk with no added claims beyond it. Should score high on "
            "both dimensions -- if it doesn't, the judge is being too "
            "harsh on paraphrasing."
        ),
    },
    {
        "name": "level_mismatch_jargon_to_beginner",
        "student_message": "what's a base case?",
        "retrieved_chunks": [
            "Recursion requires a base case that stops the recursion. "
            "Without one, the function calls itself forever until the "
            "stack overflows."
        ],
        "p_know": 0.1,  # beginner, near-zero mastery
        "tutor_response": (
            "The base case is the terminating condition in the recursive "
            "invariant that prevents unbounded stack frame allocation "
            "during the call stack's LIFO traversal, thereby avoiding a "
            "segmentation fault from stack exhaustion."
        ),
        "expected": {
            "pedagogical_fit": (1, 2),  # low -- dense jargon to a beginner
            "correctness": (4, 5),      # content is technically accurate
        },
        "why": (
            "Deliberately correct but badly mismatched to p_know=0.1 "
            "(near-zero mastery). Tests whether pedagogical_fit actually "
            "responds to p_know, independent of correctness -- this is "
            "the dimension most likely to be broken if generation.py's "
            "level-aware prompting isn't reaching the judge's context "
            "properly."
        ),
    },
    {
        "name": "level_match_simple_to_beginner",
        "student_message": "what's a base case?",
        "retrieved_chunks": [
            "Recursion requires a base case that stops the recursion. "
            "Without one, the function calls itself forever until the "
            "stack overflows."
        ],
        "p_know": 0.1,
        "tutor_response": (
            "Think of a base case like a stop sign for a function that "
            "calls itself. It's the simple condition that says 'stop "
            "here, don't call yourself again.' Without it, the function "
            "would keep calling itself forever!"
        ),
        "expected": {
            "pedagogical_fit": (4, 5),
            "correctness": (4, 5),
        },
        "why": (
            "Same p_know=0.1 as the previous case, but this time the "
            "explanation actually matches a beginner level (analogy-based, "
            "no jargon). Paired with the previous case, this is the real "
            "test -- same student level, two responses, judge should "
            "clearly separate them on pedagogical_fit."
        ),
    },
    {
        "name": "clear_but_disorganized",
        "student_message": "why do we need a base case in recursion?",
        "retrieved_chunks": [
            "Recursion requires a base case that stops the recursion. "
            "Without one, the function calls itself forever until the "
            "stack overflows."
        ],
        "p_know": 0.5,
        "tutor_response": (
            "so basically like stack overflow happens right and also the "
            "function keeps going and going and there's this thing called "
            "a base case and it stops it and yeah without it bad things "
            "happen basically it just keeps calling itself over and over"
        ),
        "expected": {
            "correctness": (3, 5),   # content is roughly accurate
            "clarity": (1, 2),       # rambling, unstructured
        },
        "why": (
            "Content is correct but delivery is a run-on ramble with no "
            "structure. Tests whether clarity is actually independent of "
            "correctness -- if clarity scores high here too, the judge "
            "isn't distinguishing the two dimensions."
        ),
    },
]