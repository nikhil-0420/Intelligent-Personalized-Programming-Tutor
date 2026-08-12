"""
Measures the Assessor Agent's false-positive rate: how often it wrongly
labels a message as is_attempt=True when the message is NOT actually an
attempt to answer/explain something (acknowledgments, small talk,
clarifying questions, greetings, off-topic remarks).

Ground truth here is "known by construction" -- every message in
NON_ATTEMPT_MESSAGES was deliberately written to NOT be a knowledge
attempt, so any is_attempt=True on these is a false positive by definition.

Run from backend/:
    python test_assessor_fp_rate.py
"""

from app.services.assessor import assess_message

TOPIC_TITLE = "Recursion"
CONTEXT = (
    "Recursion requires a base case that stops the recursion. Without one, "
    "the function calls itself forever until the stack overflows."
)

# Every message here is deliberately NOT a knowledge attempt.
# Grouped by category so you can see if certain categories fail more than others.
NON_ATTEMPT_MESSAGES = {
    "acknowledgments": [
        "ok",
        "got it",
        "I see",
        "makes sense",
        "thanks",
        "cool, thank you",
        "alright",
    ],
    "clarifying_questions": [
        "wait, what do you mean by stack overflow?",
        "can you give me another example?",
        "is that the same as a loop?",
        "what's the difference between recursion and iteration?",
    ],
    "greetings_smalltalk": [
        "hey",
        "hi there",
        "can we move on to the next topic?",
        "I'm a bit confused, can we slow down?",
    ],
    "meta_statements": [
        "I don't understand this at all",
        "this is hard",
        "can you explain it differently?",
        "I need a minute to think about this",
    ],
    "adjacent_but_not_an_attempt": [
        # Mentions recursion-related words WITHOUT actually explaining/attempting
        # anything -- these are the trickiest, most realistic false-positive bait.
        "recursion sounds complicated",
        "so recursion is one of the topics in this course?",
        "I read about recursion online yesterday",
    ],
}


def run():
    total = 0
    false_positives = 0
    results_by_category = {}

    for category, messages in NON_ATTEMPT_MESSAGES.items():
        cat_total = 0
        cat_fp = 0
        print(f"\n=== {category} ===")

        for msg in messages:
            result = assess_message(msg, TOPIC_TITLE, CONTEXT)
            total += 1
            cat_total += 1

            is_fp = result["is_attempt"] is True
            if is_fp:
                false_positives += 1
                cat_fp += 1

            flag = "FALSE POSITIVE" if is_fp else "ok"
            print(f"[{flag}] \"{msg}\"")
            print(f"    -> is_attempt={result['is_attempt']}, correct={result['correct']}")
            print(f"    -> reasoning: {result['reasoning']}")

        results_by_category[category] = (cat_fp, cat_total)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for category, (fp, cat_total) in results_by_category.items():
        rate = fp / cat_total * 100
        print(f"{category:30s} {fp}/{cat_total} false positives ({rate:.1f}%)")

    overall_rate = false_positives / total * 100
    print(f"\nOVERALL: {false_positives}/{total} false positives ({overall_rate:.1f}%)")


if __name__ == "__main__":
    run()