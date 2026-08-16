"""
Runs judge_interaction() against VALIDATION_CASES and checks whether
scores land in the expected ranges. Run this BEFORE trusting the judge
on real ablation data.

Run from backend/:
    python judge_validation_runner.py
"""

from app.services.judge import judge_interaction
from judge_validation_set import VALIDATION_CASES


def run():
    total_checks = 0
    failed_checks = 0

    for case in VALIDATION_CASES:
        print(f"\n=== {case['name']} ===")
        print(f"why: {case['why']}")

        result = judge_interaction(
            student_message=case["student_message"],
            retrieved_chunks=case["retrieved_chunks"],
            p_know=case["p_know"],
            tutor_response=case["tutor_response"],
        )

        for dim, (low, high) in case["expected"].items():
            total_checks += 1
            score = result[dim]["score"]
            reasoning = result[dim]["reasoning"]

            if score is None:
                failed_checks += 1
                print(f"  [FAIL] {dim}: judge returned no valid score ({reasoning})")
                continue

            in_range = low <= score <= high
            if not in_range:
                failed_checks += 1

            flag = "ok" if in_range else "FAIL"
            print(f"  [{flag}] {dim}: expected {low}-{high}, got {score}")
            print(f"        reasoning: {reasoning}")

        # Print the two unchecked dimensions too, just for visibility
        unchecked = [d for d in result if d not in case["expected"]]
        if unchecked:
            print("  (unchecked dimensions, for reference:)")
            for dim in unchecked:
                print(f"    {dim}: {result[dim]['score']} -- {result[dim]['reasoning']}")

    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    passed = total_checks - failed_checks
    print(f"{passed}/{total_checks} dimension checks passed")
    if failed_checks:
        print(f"{failed_checks} check(s) failed -- review the rubric wording for those dimensions before trusting judge scores on real data.")
    else:
        print("All checks passed -- judge is behaving as expected on known cases.")


if __name__ == "__main__":
    run()