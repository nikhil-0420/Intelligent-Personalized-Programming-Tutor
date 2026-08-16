"""
Round 2: harder false-positive stress test.
Only contains messages that are genuinely NOT knowledge attempts --
"dismissive_wrong_statements" was removed because those messages turned
out to be real (incorrect) attempts, not non-attempts. See
test_assessor_fn_rate.py's REAL_INCORRECT_ATTEMPTS for those.
"""

from app.services.assessor import assess_message

TOPIC_TITLE = "Recursion"
CONTEXT = (
    "Recursion requires a base case that stops the recursion. Without one, "
    "the function calls itself forever until the stack overflows."
)

HARD_NON_ATTEMPT_MESSAGES = {
    "ambiguous_half_attempt": [
        "I think it stops when it hits the base case, right?",
        "so it's like... the function keeps calling itself until something stops it?",
        "is it something to do with the base case?",
        "does it have to do with the stack somehow?",
    ],
    "short_fragments": [
        "base case",
        "stack overflow",
        "infinite recursion",
        "recursive call",
    ],
}

# NOTE: "I think it stops when it hits the base case, right?" and "so it's
# like... the function keeps calling itself until something stops it?" are
# INTENTIONALLY hedged claims that DO assert a mechanism -- these SHOULD be
# is_attempt=True after the prompt fix. Only "is it something to do with
# the base case?" and "does it have to do with the stack somehow?" are pure
# questions with no asserted mechanism and should stay is_attempt=False.
EXPECTED_ATTEMPT = {
    "I think it stops when it hits the base case, right?": True,
    "so it's like... the function keeps calling itself until something stops it?": True,
    "is it something to do with the base case?": False,
    "does it have to do with the stack somehow?": False,
    "base case": False,
    "stack overflow": False,
    "infinite recursion": False,
    "recursive call": False,
}


def run_hard_fp_test():
    total = 0
    mismatches = 0
    results_by_category = {}

    for category, messages in HARD_NON_ATTEMPT_MESSAGES.items():
        cat_total = 0
        cat_mismatch = 0
        print(f"\n=== {category} ===")

        for msg in messages:
            result = assess_message(msg, TOPIC_TITLE, CONTEXT)
            total += 1
            cat_total += 1

            expected = EXPECTED_ATTEMPT[msg]
            is_mismatch = result["is_attempt"] != expected
            if is_mismatch:
                mismatches += 1
                cat_mismatch += 1

            flag = "MISMATCH" if is_mismatch else "ok"
            print(f"[{flag}] \"{msg}\" (expected is_attempt={expected})")
            print(f"    -> is_attempt={result['is_attempt']}, correct={result['correct']}")
            print(f"    -> reasoning: {result['reasoning']}")

        results_by_category[category] = (cat_mismatch, cat_total)

    print("\n" + "=" * 50)
    print("HARD FALSE-POSITIVE SUMMARY (vs. expected labels)")
    print("=" * 50)
    for category, (mismatch, cat_total) in results_by_category.items():
        rate = mismatch / cat_total * 100
        print(f"{category:30s} {mismatch}/{cat_total} mismatches ({rate:.1f}%)")

    overall_rate = mismatches / total * 100
    print(f"\nOVERALL: {mismatches}/{total} mismatches ({overall_rate:.1f}%)")


if __name__ == "__main__":
    run_hard_fp_test()