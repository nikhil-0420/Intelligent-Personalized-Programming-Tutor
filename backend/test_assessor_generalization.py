"""
Full generalization check across multiple topics: recursion (baseline,
already validated), arrays, sorting. Same five message patterns tested
per topic so results are directly comparable across topics.

This closes out the assessor testing for now -- broader, more systematic
coverage is phase 10 (LLM-as-judge eval framework) work, not this script's job.
"""

from app.services.assessor import assess_message

TOPICS = {
    "Recursion": {
        "context": (
            "Recursion requires a base case that stops the recursion. Without "
            "one, the function calls itself forever until the stack overflows."
        ),
        "messages": [
            ("what is a base case?", False, None),
            ("a base case stops the recursion from running forever", True, True),
            ("recursion doesn't need a base case, it just runs until it's done", True, False),
            ("I think it stops when it hits the base case, right?", True, True),
            ("does it have to do with the stack somehow?", False, None),
        ],
    },
    "Arrays": {
        "context": (
            "An array is a fixed-size collection of elements stored in contiguous "
            "memory, accessed by index starting at 0. Accessing an element by index "
            "is O(1), but inserting or deleting from the middle is O(n) because "
            "later elements must shift."
        ),
        "messages": [
            ("what does O(1) mean?", False, None),
            ("array access by index is O(1) because it's just a memory offset calculation", True, True),
            ("inserting into the middle of an array is O(1) since you just overwrite that spot", True, False),
            ("I think deleting from the middle is slow because everything after has to shift, right?", True, True),
            ("does it have something to do with shifting elements?", False, None),
        ],
    },
    "Sorting": {
        "context": (
            "Bubble sort repeatedly steps through the list, compares adjacent "
            "elements, and swaps them if they're in the wrong order. It has a "
            "worst-case time complexity of O(n^2) because it may need n passes "
            "over n elements."
        ),
        "messages": [
            ("why is bubble sort O(n^2)?", False, None),
            ("bubble sort compares adjacent elements and swaps them if they're out of order", True, True),
            ("bubble sort only needs one pass through the list no matter the size", True, False),
            ("I think it's slow because it might need n passes over n elements, right?", True, True),
            ("does it have something to do with how many passes it takes?", False, None),
        ],
    },
}


def run():
    total = 0
    mismatches = 0
    results_by_topic = {}

    for topic_title, spec in TOPICS.items():
        context = spec["context"]
        cat_total = 0
        cat_mismatch = 0
        print(f"\n=== {topic_title} ===")

        for msg, expected_attempt, expected_correct in spec["messages"]:
            result = assess_message(msg, topic_title, context)
            total += 1
            cat_total += 1

            attempt_ok = result["is_attempt"] == expected_attempt
            correct_ok = (not expected_attempt) or (result["correct"] == expected_correct)
            ok = attempt_ok and correct_ok

            if not ok:
                mismatches += 1
                cat_mismatch += 1

            flag = "ok" if ok else "MISMATCH"
            print(f"[{flag}] \"{msg}\"")
            print(f"    expected: is_attempt={expected_attempt}, correct={expected_correct}")
            print(f"    got:      is_attempt={result['is_attempt']}, correct={result['correct']}")
            print(f"    reasoning: {result['reasoning']}")

        results_by_topic[topic_title] = (cat_mismatch, cat_total)

    print("\n" + "=" * 50)
    print("GENERALIZATION SUMMARY")
    print("=" * 50)
    for topic_title, (mismatch, cat_total) in results_by_topic.items():
        rate = mismatch / cat_total * 100
        print(f"{topic_title:15s} {mismatch}/{cat_total} mismatches ({rate:.1f}%)")

    overall_rate = mismatches / total * 100
    print(f"\nOVERALL: {mismatches}/{total} mismatches ({overall_rate:.1f}%)")


if __name__ == "__main__":
    run()