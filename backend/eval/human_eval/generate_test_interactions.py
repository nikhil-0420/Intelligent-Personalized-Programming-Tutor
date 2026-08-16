"""
Fires a batch of varied test interactions across all 5 topics to build up
enough volume/diversity for the phase 11 rating sample. Expanded to 5
distinct messages per topic (no repeats) after the first pass surfaced
significant message duplication in the exported sample.

Run from backend/ (make sure uvicorn is running in another window):
    python generate_test_interactions.py
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"
STUDENT_ID = 1  # adjust to match your actual student ID

TOPIC_MESSAGES = {
    "recursion": [
        "what is a base case?",
        "a base case stops the recursion from running forever",
        "recursion doesn't need a base case, it just runs until it's done",
        "why does my recursive function keep calling itself if I already have a base case?",
        "recursion and iteration are basically the same thing, just different syntax",
    ],
    "arrays": [
        "what does O(1) mean for array access?",
        "array access by index is O(1) because it's a direct memory offset",
        "inserting into the middle of an array is O(1) since you just overwrite that spot",
        "why does appending to a dynamic array sometimes take longer than other times?",
        "a 2D array traversal is O(n) no matter how big the matrix is",
    ],
    "sorting": [
        "why is bubble sort O(n^2)?",
        "bubble sort compares adjacent elements and swaps them if they're out of order",
        "bubble sort only needs one pass through the list no matter the size",
        "what does it mean for a sorting algorithm to be stable?",
        "quicksort is always faster than merge sort since it's in-place",
    ],
    "searching": [
        "what's the difference between linear and binary search?",
        "binary search only works on sorted data and repeatedly halves the search space",
        "binary search works on any array whether it's sorted or not",
        "why would binary search give me the wrong answer on this array?",
        "if there are duplicate values, binary search will always find the first occurrence",
    ],
    "graphs": [
        "what's the difference between BFS and DFS?",
        "BFS explores level by level using a queue, DFS goes deep first using a stack or recursion",
        "BFS and DFS always visit nodes in the exact same order",
        "why did my DFS get stuck in an infinite loop on this graph?",
        "you should always use DFS for finding the shortest path in a graph",
    ],
}


def run():
    for topic_slug, messages in TOPIC_MESSAGES.items():
        print(f"\n=== {topic_slug} ===")
        for msg in messages:
            resp = requests.post(
                f"{BASE_URL}/tutor/interact",
                json={
                    "student_id": STUDENT_ID,
                    "topic_slug": topic_slug,
                    "message": msg,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"  [ok] \"{msg[:50]}...\" -> p_know {data['p_know_before']:.2f} -> {data['p_know_after']:.2f}")
            else:
                print(f"  [FAIL {resp.status_code}] \"{msg[:50]}...\" -> {resp.text[:200]}")

            time.sleep(0.5)

    print("\nDone. Now re-run export_rating_sample.py to pull the expanded set.")


if __name__ == "__main__":
    run()