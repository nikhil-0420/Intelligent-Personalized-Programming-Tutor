"""
False-negative test: real knowledge attempts that should be caught as
is_attempt=True. Split into REAL_CORRECT and REAL_INCORRECT so you can see
if the assessor is more likely to miss one type than the other.
"""

from app.services.assessor import assess_message

TOPIC_TITLE = "Recursion"
CONTEXT = (
    "Recursion requires a base case that stops the recursion. Without one, "
    "the function calls itself forever until the stack overflows."
)

REAL_CORRECT_ATTEMPTS = [
    "A base case stops the recursion from running forever.",
    "Recursion needs a base case or it'll cause a stack overflow.",
    "Without a base case, the function keeps calling itself and the stack overflows.",
    "The base case is what tells the recursive function when to stop.",
]

REAL_INCORRECT_ATTEMPTS = [
    "Recursion doesn't need a base case, it just runs until it's done.",
    "A base case is what makes the function call itself more times.",
    "Recursion never causes a stack overflow, that's only for loops.",
    "You don't need to stop recursion, it stops automatically on its own.",
    # Moved from the hard FP test -- these are confidently wrong assertions,
    # not idle chatter, so they belong here as real (incorrect) attempts.
    "recursion is basically the same thing as a for loop",
    "eh, recursion is just a fancy loop, doesn't really matter",
    "I don't think base cases actually matter that much",
]


def run_fn_test(label, messages, expected_correct):
    total = 0
    false_negatives = 0
    misjudged = 0

    print(f"\n=== {label} ===")
    for msg in messages:
        result = assess_message(msg, TOPIC_TITLE, CONTEXT)
        total += 1

        if result["is_attempt"] is not True:
            false_negatives += 1
            flag = "FALSE NEGATIVE (missed attempt)"
        elif result["correct"] != expected_correct:
            misjudged += 1
            flag = "MISJUDGED (wrong correctness verdict)"
        else:
            flag = "ok"

        print(f"[{flag}] \"{msg}\"")
        print(f"    -> is_attempt={result['is_attempt']}, correct={result['correct']}")
        print(f"    -> reasoning: {result['reasoning']}")

    return total, false_negatives, misjudged


def run_all():
    total_c, fn_c, mis_c = run_fn_test("REAL_CORRECT_ATTEMPTS", REAL_CORRECT_ATTEMPTS, expected_correct=True)
    total_i, fn_i, mis_i = run_fn_test("REAL_INCORRECT_ATTEMPTS", REAL_INCORRECT_ATTEMPTS, expected_correct=False)

    print("\n" + "=" * 50)
    print("FALSE-NEGATIVE SUMMARY")
    print("=" * 50)
    print(f"Correct attempts:   {fn_c}/{total_c} missed, {mis_c}/{total_c} misjudged")
    print(f"Incorrect attempts: {fn_i}/{total_i} missed, {mis_i}/{total_i} misjudged")

    total = total_c + total_i
    total_fn = fn_c + fn_i
    total_mis = mis_c + mis_i
    print(f"\nOVERALL: {total_fn}/{total} false negatives ({total_fn/total*100:.1f}%), "
          f"{total_mis}/{total} misjudged ({total_mis/total*100:.1f}%)")


if __name__ == "__main__":
    run_all()