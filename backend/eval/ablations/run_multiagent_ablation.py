"""
Single-agent vs multi-agent ablation. Two comparisons:
  1. Response quality -- 120 test cases (10 topics x 4 mastery levels x
     3 questions), judge-scored Correctness/Pedagogical Fit, multi-agent's
     Tutor output vs single-agent's combined output.
  2. Assessment accuracy -- labeled test cases across all 10 topics,
     checking whether single-agent's combined is_attempt/correct judgment
     is as reliable as the dedicated Assessor. Phase 7 found a 13-20%
     cross-topic mismatch when the Assessor's recursion-tuned hardening
     was tested outside recursion -- this checks whether that holds now.
"""

from scipy import stats
import json
import os
import time
CHECKPOINT_PATH = "response_quality_checkpoint.jsonl"
from app.database import SessionLocal
from app.services.retrieval import retrieve_relevant_chunks
from app.services.generation import generate_response
from app.services.assessor import assess_message
from app.services.single_agent import single_agent_interact
from app.services.judge import judge_interaction

TRUSTED_DIMENSIONS = ["correctness", "pedagogical_fit"]

# 120 cases: 10 topics x 4 mastery levels x 3 questions
RESPONSE_QUALITY_CASES = [
    {"topic": "arrays", "query": 'why is accessing an array element O(1)', "p_know": 0.15},
    {"topic": "arrays", "query": 'why is inserting into the middle of an array slow', "p_know": 0.5},
    {"topic": "arrays", "query": 'when does a dynamic array\'s resize actually cost O(n)', "p_know": 0.8},
    {"topic": "arrays", "query": 'why doesn\'t out-of-bounds array access always throw an error', "p_know": 0.3},
    {"topic": "recursion", "query": 'why do I need a base case in a recursive function', "p_know": 0.15},
    {"topic": "recursion", "query": 'why does naive recursive Fibonacci get so slow for large n', "p_know": 0.5},
    {"topic": "recursion", "query": 'when is recursion actually better than iteration', "p_know": 0.8},
    {"topic": "recursion", "query": 'why does my recursive function cause a stack overflow', "p_know": 0.3},
    {"topic": "sorting", "query": 'what\'s the difference between bubble sort and selection sort', "p_know": 0.15},
    {"topic": "sorting", "query": 'why does quicksort degrade to O(n^2) on sorted input', "p_know": 0.5},
    {"topic": "sorting", "query": 'what does it mean for a sort to be stable', "p_know": 0.8},
    {"topic": "sorting", "query": 'why does merge sort need O(n) extra space', "p_know": 0.3},
    {"topic": "graphs", "query": 'when should I use BFS instead of DFS', "p_know": 0.15},
    {"topic": "graphs", "query": 'why did my DFS get stuck in an infinite loop', "p_know": 0.5},
    {"topic": "graphs", "query": 'how do I detect a cycle in a directed graph', "p_know": 0.8},
    {"topic": "graphs", "query": 'why do I need to mark nodes as visited during traversal', "p_know": 0.3},
    {"topic": "searching", "query": 'can I use binary search on an unsorted array', "p_know": 0.15},
    {"topic": "searching", "query": 'how do I find the first occurrence of a duplicate target', "p_know": 0.5},
    {"topic": "searching", "query": 'how does binary search work on a rotated sorted array', "p_know": 0.8},
    {"topic": "searching", "query": 'why can mid = (low+high)/2 cause a bug in some languages', "p_know": 0.3},
    {"topic": "arrays", "query": 'why is prepending to an array slower than appending', "p_know": 0.15},
    {"topic": "arrays", "query": 'is array access really O(1) if the array is huge', "p_know": 0.15},
    {"topic": "arrays", "query": 'what actually happens in memory when I shift elements after a middle insert', "p_know": 0.5},
    {"topic": "arrays", "query": 'why does deleting from the middle of an array also cost O(n)', "p_know": 0.5},
    {"topic": "arrays", "query": 'why does a dynamic array double capacity instead of growing by 1 each time', "p_know": 0.8},
    {"topic": "arrays", "query": 'how is amortized O(1) append actually justified mathematically', "p_know": 0.8},
    {"topic": "arrays", "query": 'why does my program crash instead of erroring on an out-of-bounds write in some languages', "p_know": 0.3},
    {"topic": "arrays", "query": 'is out-of-bounds behavior the same in every programming language', "p_know": 0.3},
    {"topic": "recursion", "query": 'what happens if I forget to return the recursive call result', "p_know": 0.15},
    {"topic": "recursion", "query": 'can a recursive function have more than one base case', "p_know": 0.15},
    {"topic": "recursion", "query": 'how many times does naive Fibonacci recompute the same subproblem', "p_know": 0.5},
    {"topic": "recursion", "query": 'why does memoization fix naive recursive Fibonacci\'s slowness', "p_know": 0.5},
    {"topic": "recursion", "query": 'why is recursion often preferred for tree and graph traversal specifically', "p_know": 0.8},
    {"topic": "recursion", "query": 'when would an iterative solution actually outperform a recursive one', "p_know": 0.8},
    {"topic": "recursion", "query": 'why does not reducing the input size cause a stack overflow', "p_know": 0.3},
    {"topic": "recursion", "query": 'is a stack overflow the same thing as an infinite loop', "p_know": 0.3},
    {"topic": "sorting", "query": 'why is selection sort always O(n^2) even on nearly sorted input', "p_know": 0.15},
    {"topic": "sorting", "query": 'how many comparisons does bubble sort do in the worst case', "p_know": 0.15},
    {"topic": "sorting", "query": 'why does quicksort perform well on random input despite the worst case', "p_know": 0.5},
    {"topic": "sorting", "query": 'how does pivot choice affect quicksort\'s worst-case behavior', "p_know": 0.5},
    {"topic": "sorting", "query": 'why does stability matter when sorting objects by multiple keys', "p_know": 0.8},
    {"topic": "sorting", "query": 'is quicksort a stable sort', "p_know": 0.8},
    {"topic": "sorting", "query": 'why can\'t merge sort easily be done in-place like quicksort', "p_know": 0.3},
    {"topic": "sorting", "query": 'does merge sort\'s O(n) space requirement matter for large datasets', "p_know": 0.3},
    {"topic": "graphs", "query": 'why does BFS find the shortest path in an unweighted graph but DFS doesn\'t', "p_know": 0.15},
    {"topic": "graphs", "query": 'what data structure does BFS use internally that DFS doesn\'t', "p_know": 0.15},
    {"topic": "graphs", "query": 'why does DFS get stuck even if I\'m marking visited nodes, in some cases', "p_know": 0.5},
    {"topic": "graphs", "query": 'can an infinite loop happen in DFS on an undirected graph specifically', "p_know": 0.5},
    {"topic": "graphs", "query": 'why does cycle detection differ between directed and undirected graphs', "p_know": 0.8},
    {"topic": "graphs", "query": 'what role does a recursion stack play in detecting cycles in directed graphs', "p_know": 0.8},
    {"topic": "graphs", "query": 'what actually goes wrong if I don\'t mark nodes visited during BFS', "p_know": 0.3},
    {"topic": "graphs", "query": 'is marking visited nodes necessary on a tree-shaped graph', "p_know": 0.3},
    {"topic": "searching", "query": 'what actually happens if I run binary search on unsorted data', "p_know": 0.15},
    {"topic": "searching", "query": 'why does binary search require sorted input in the first place', "p_know": 0.15},
    {"topic": "searching", "query": 'how do I modify binary search to find the first occurrence instead of any occurrence', "p_know": 0.5},
    {"topic": "searching", "query": 'what changes in binary search logic when duplicates are present', "p_know": 0.5},
    {"topic": "searching", "query": 'why does rotated sorted array search still run in O(log n)', "p_know": 0.8},
    {"topic": "searching", "query": 'how do I decide which half of a rotated array is actually sorted', "p_know": 0.8},
    {"topic": "searching", "query": 'why does (low+high)/2 overflow in some languages but not others', "p_know": 0.3},
    {"topic": "searching", "query": 'what\'s the fix for the mid-calculation overflow bug', "p_know": 0.3},
    {"topic": "trees", "query": 'what\'s the difference between depth and height in a tree', "p_know": 0.15},
    {"topic": "trees", "query": 'why do I need a base case when writing a recursive tree traversal', "p_know": 0.15},
    {"topic": "trees", "query": 'what happens if my traversal function doesn\'t check for a null node', "p_know": 0.15},
    {"topic": "trees", "query": 'what\'s the difference between inorder, preorder, and postorder traversal', "p_know": 0.5},
    {"topic": "trees", "query": 'why does BST search take O(log n) on average', "p_know": 0.5},
    {"topic": "trees", "query": 'how does the BST ordering property actually speed up search', "p_know": 0.5},
    {"topic": "trees", "query": 'why does inserting sorted values into a BST degrade performance to O(n)', "p_know": 0.8},
    {"topic": "trees", "query": 'how should a BST handle duplicate values', "p_know": 0.8},
    {"topic": "trees", "query": 'why does an unbalanced BST behave like a linked list in the worst case', "p_know": 0.8},
    {"topic": "trees", "query": 'is depth measured from the root or from the node itself', "p_know": 0.3},
    {"topic": "trees", "query": 'why does my recursive height function crash on an empty tree', "p_know": 0.3},
    {"topic": "trees", "query": 'what should a height function return for a single-node tree', "p_know": 0.3},
    {"topic": "hashing", "query": 'why is hash table lookup considered O(1)', "p_know": 0.15},
    {"topic": "hashing", "query": 'what is a collision in a hash table and why does it happen', "p_know": 0.15},
    {"topic": "hashing", "query": 'why can two different keys end up at the same index', "p_know": 0.15},
    {"topic": "hashing", "query": 'how does chaining resolve hash collisions', "p_know": 0.5},
    {"topic": "hashing", "query": 'what\'s the difference between chaining and open addressing', "p_know": 0.5},
    {"topic": "hashing", "query": 'why does using a hash set beat a nested loop for duplicate detection', "p_know": 0.5},
    {"topic": "hashing", "query": 'why does a hash table resize once load factor crosses a threshold', "p_know": 0.8},
    {"topic": "hashing", "query": 'how is resizing amortized to still be O(1) per insert on average', "p_know": 0.8},
    {"topic": "hashing", "query": 'why does clustering make linear probing degrade faster than chaining', "p_know": 0.8},
    {"topic": "hashing", "query": 'is hash table lookup always O(1) no matter what', "p_know": 0.3},
    {"topic": "hashing", "query": 'what happens to lookup time if the hash function is bad', "p_know": 0.3},
    {"topic": "hashing", "query": 'why do I need to handle collisions instead of just overwriting the slot', "p_know": 0.3},
    {"topic": "dynamic_programming", "query": 'what makes a problem a good fit for dynamic programming', "p_know": 0.15},
    {"topic": "dynamic_programming", "query": 'what does overlapping subproblems actually mean', "p_know": 0.15},
    {"topic": "dynamic_programming", "query": 'what\'s the difference between memoization and tabulation', "p_know": 0.15},
    {"topic": "dynamic_programming", "query": 'why does memoization fix the exponential blowup in naive recursive Fibonacci', "p_know": 0.5},
    {"topic": "dynamic_programming", "query": 'why would I choose tabulation over memoization for a given problem', "p_know": 0.5},
    {"topic": "dynamic_programming", "query": 'how does the coin change DP table actually get filled in', "p_know": 0.5},
    {"topic": "dynamic_programming", "query": 'why does DP fail silently on a problem without optimal substructure', "p_know": 0.8},
    {"topic": "dynamic_programming", "query": 'how do I recognize when a problem doesn\'t actually benefit from DP', "p_know": 0.8},
    {"topic": "dynamic_programming", "query": 'why can memoization risk a stack overflow that tabulation avoids', "p_know": 0.8},
    {"topic": "dynamic_programming", "query": 'is dynamic programming just recursion with extra steps', "p_know": 0.3},
    {"topic": "dynamic_programming", "query": 'why do I need a base case in the DP table, same as in recursion', "p_know": 0.3},
    {"topic": "dynamic_programming", "query": 'what happens if I fill the DP table in the wrong order', "p_know": 0.3},
    {"topic": "linked_lists", "query": 'why can\'t I randomly access the 5th element of a linked list like I can with an array', "p_know": 0.15},
    {"topic": "linked_lists", "query": 'what is a node in a linked list made of', "p_know": 0.15},
    {"topic": "linked_lists", "query": 'why does my traversal loop never end when I check the wrong condition', "p_know": 0.15},
    {"topic": "linked_lists", "query": 'why is inserting into the middle of a linked list O(1) but inserting into the middle of an array O(n)', "p_know": 0.5},
    {"topic": "linked_lists", "query": 'what is the risk of losing the head pointer while traversing', "p_know": 0.5},
    {"topic": "linked_lists", "query": 'how do I traverse a linked list without breaking the chain', "p_know": 0.5},
    {"topic": "linked_lists", "query": 'why does a doubly linked list use more memory per node than singly linked', "p_know": 0.8},
    {"topic": "linked_lists", "query": 'when would I choose a doubly linked list over singly linked', "p_know": 0.8},
    {"topic": "linked_lists", "query": 'why is deleting a node from a doubly linked list easier given just a reference to it', "p_know": 0.8},
    {"topic": "linked_lists", "query": 'why do I need to save the next pointer before reassigning it when reversing a list', "p_know": 0.3},
    {"topic": "linked_lists", "query": 'what happens if I reverse a linked list\'s pointers in the wrong order', "p_know": 0.3},
    {"topic": "linked_lists", "query": 'why does my reversed list only have one node when I am done', "p_know": 0.3},
    {"topic": "stacks_queues", "query": 'what is the difference between a stack and a queue', "p_know": 0.15},
    {"topic": "stacks_queues", "query": 'why is push/pop from a stack O(1)', "p_know": 0.15},
    {"topic": "stacks_queues", "query": 'what does LIFO actually mean', "p_know": 0.15},
    {"topic": "stacks_queues", "query": 'why is popping from the front of an array-based queue O(n)', "p_know": 0.5},
    {"topic": "stacks_queues", "query": 'how does a stack help check for balanced parentheses', "p_know": 0.5},
    {"topic": "stacks_queues", "query": 'what data structure should I use to reverse the order of elements', "p_know": 0.5},
    {"topic": "stacks_queues", "query": 'how does implementing a queue with two stacks achieve amortized O(1) operations', "p_know": 0.8},
    {"topic": "stacks_queues", "query": 'why is the call stack during recursion literally a stack data structure', "p_know": 0.8},
    {"topic": "stacks_queues", "query": 'why does BFS use a queue while DFS uses a stack', "p_know": 0.8},
    {"topic": "stacks_queues", "query": 'why does a stack overflow happen during deep recursion specifically', "p_know": 0.3},
    {"topic": "stacks_queues", "query": 'can any recursive algorithm be rewritten iteratively using an explicit stack', "p_know": 0.3},
    {"topic": "stacks_queues", "query": 'what happens if I use a stack instead of a queue for BFS by mistake', "p_know": 0.3},
]

def _load_checkpoint():
    """Returns dict of {case_index: result_dict} for already-completed cases."""
    completed = {}
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                completed[rec["case_index"]] = rec
    return completed


def _append_checkpoint(rec):
    with open(CHECKPOINT_PATH, "a") as f:
        f.write(json.dumps(rec) + "\n")


def run_response_quality_comparison():
    print("=" * 70)
    print("PART 1: RESPONSE QUALITY (multi-agent Tutor vs single-agent combined)")
    print("=" * 70)

    db = SessionLocal()
    completed = _load_checkpoint()
    if completed:
        print(f"Resuming from checkpoint: {len(completed)}/{len(RESPONSE_QUALITY_CASES)} cases already done.")

    for i, case in enumerate(RESPONSE_QUALITY_CASES):
        if i in completed:
            continue  # already done, skip re-running it

        print(f"Running [{i+1}/{len(RESPONSE_QUALITY_CASES)}]: [{case['topic']}] {case['query'][:50]}...")

        for attempt in range(3):
            try:
                retrieved = retrieve_relevant_chunks(db, case["query"], case["topic"], top_k=3)
                chunk_texts = [c["content"] for c in retrieved]
                context_text = "\n".join(chunk_texts)

                multi_response = generate_response(case["query"], retrieved, case["p_know"])
                single_result = single_agent_interact(case["query"], case["topic"], context_text, case["p_know"])
                single_response = single_result["tutor_response"] or ""

                multi_judge = judge_interaction(case["query"], chunk_texts, case["p_know"], multi_response)
                single_judge = judge_interaction(case["query"], chunk_texts, case["p_know"], single_response)

                rec = {
                    "case_index": i,
                    "topic": case["topic"],
                    "query": case["query"],
                    "multi_scores": {dim: multi_judge[dim]["score"] for dim in TRUSTED_DIMENSIONS},
                    "single_scores": {dim: single_judge[dim]["score"] for dim in TRUSTED_DIMENSIONS},
                }
                _append_checkpoint(rec)
                break  # success, stop retrying

            except Exception as e:
                print(f"  [ERROR on attempt {attempt+1}/3] {type(e).__name__}: {str(e)[:200]}")
                if attempt < 2:
                    print("  Waiting 15s before retry (gives Ollama a moment to recover)...")
                    time.sleep(15)
                else:
                    print(f"  Giving up on case {i} after 3 attempts. Progress up to this point is saved.")
                    print(f"  Re-run the script to resume from case {i} once Ollama is restarted.")
                    raise  # re-raise so you know it stopped, but checkpoint file is intact

    # Aggregate from checkpoint file (covers cases from this run + any prior resumed runs)
    completed = _load_checkpoint()
    multi_scores = {dim: [] for dim in TRUSTED_DIMENSIONS}
    single_scores = {dim: [] for dim in TRUSTED_DIMENSIONS}
    for rec in completed.values():
        for dim in TRUSTED_DIMENSIONS:
            if rec["multi_scores"][dim] is not None:
                multi_scores[dim].append(rec["multi_scores"][dim])
            if rec["single_scores"][dim] is not None:
                single_scores[dim].append(rec["single_scores"][dim])

    print(f"\n--- Response Quality Summary ({len(completed)}/{len(RESPONSE_QUALITY_CASES)} cases) ---")
    for dim in TRUSTED_DIMENSIONS:
        if len(multi_scores[dim]) == len(single_scores[dim]) and len(multi_scores[dim]) > 1:
            t, p = stats.ttest_rel(multi_scores[dim], single_scores[dim])
            multi_mean = sum(multi_scores[dim]) / len(multi_scores[dim])
            single_mean = sum(single_scores[dim]) / len(single_scores[dim])
            print(f"  {dim}: multi-agent={multi_mean:.2f}  single-agent={single_mean:.2f}  "
                  f"t={t:.3f}, p={p:.4f}")
        else:
            print(f"  {dim}: mismatched or insufficient valid scores, skipping stats")

# Assessment accuracy test sets across all 10 topics. Phase 7's original
# hardening was tuned on recursion only, and cross-topic testing at the
# time found a 13-20% mismatch rate outside it -- this checks whether
# that gap has changed.
ASSESSMENT_TEST_SETS = [
    {
        "topic": "Recursion",
        "context": (
            "Recursion requires a base case that stops the recursion. Without one, "
            "the function calls itself forever until the stack overflows."
        ),
        "correct": [
            "A base case stops the recursion from running forever.",
            "Recursion needs a base case or it'll cause a stack overflow.",
            "Without a base case, the function keeps calling itself and the stack overflows.",
            "The base case is what tells the recursive function when to stop.",
        ],
        "incorrect": [
            "Recursion doesn't need a base case, it just runs until it's done.",
            "A base case is what makes the function call itself more times.",
            "Recursion never causes a stack overflow, that's only for loops.",
            "You don't need to stop recursion, it stops automatically on its own.",
            "recursion is basically the same thing as a for loop",
            "eh, recursion is just a fancy loop, doesn't really matter",
            "I don't think base cases actually matter that much",
        ],
        "non_attempts": [
            "ok", "got it", "I see", "thanks",
            "what do you mean by stack overflow?",
            "can you give me another example?",
            "is it something to do with the base case?",
            "does it have to do with the stack somehow?",
        ],
    },
    {
        "topic": "Arrays",
        "context": (
            "Accessing an array element by index is O(1) because the memory address "
            "is computed directly from the base address plus an offset. Inserting or "
            "deleting in the middle of an array is O(n) because all subsequent elements "
            "must shift."
        ),
        "correct": [
            "Array access is O(1) because you can calculate the memory address directly.",
            "Inserting in the middle of an array is O(n) since everything after it has to shift over.",
            "You can jump straight to an index in an array without searching for it.",
            "Deleting from the middle of an array is slow because of all the shifting.",
        ],
        "incorrect": [
            "Array access is O(n) because you have to search through it.",
            "Inserting in the middle of an array is O(1), it doesn't require any shifting.",
            "Arrays don't need shifting when you delete elements.",
            "Array indexing works by searching one by one until you find the right spot.",
            "arrays are basically the same as linked lists for insertion speed",
        ],
        "non_attempts": [
            "ok", "makes sense",
            "what's an offset exactly?",
            "can you give an example?",
            "is that true for all array types?",
            "does that apply to sorted arrays too?",
        ],
    },
    {
        "topic": "Sorting",
        "context": (
            "Bubble sort and selection sort are both O(n^2) in the worst case. Merge "
            "sort is O(n log n) but requires O(n) extra space. A sort is stable if it "
            "preserves the relative order of equal elements."
        ),
        "correct": [
            "Bubble sort and selection sort are both O(n^2) in the worst case.",
            "Merge sort needs extra space because it copies elements during merging.",
            "A stable sort keeps equal elements in their original relative order.",
            "Merge sort is O(n log n) which is faster than bubble sort's O(n^2).",
        ],
        "incorrect": [
            "Merge sort doesn't need any extra memory, it sorts in place.",
            "Bubble sort is actually faster than merge sort for large inputs.",
            "A stable sort means the algorithm runs the same speed every time.",
            "Selection sort is O(n log n) in the worst case.",
            "stability doesn't matter for sorting numbers, only for objects",
        ],
        "non_attempts": [
            "got it", "thanks for explaining",
            "why does merge sort need extra space specifically?",
            "can you show me an example of unstable sorting?",
            "is quicksort stable too?",
            "what about insertion sort?",
        ],
    },
    {
        "topic": "Searching",
        "context": (
            "Binary search requires sorted input and runs in O(log n) by repeatedly "
            "halving the search range. It does not work correctly on unsorted data."
        ),
        "correct": [
            "Binary search only works if the array is already sorted.",
            "Binary search is O(log n) because it cuts the search space in half each time.",
            "Running binary search on unsorted data can give wrong results.",
            "Binary search compares the middle element and eliminates half the remaining elements.",
        ],
        "incorrect": [
            "Binary search works fine on unsorted arrays too.",
            "Binary search is O(n) because it checks every element.",
            "Binary search doesn't need the data to be sorted, that's linear search.",
            "Binary search always checks the first element before doing anything else.",
            "sorting doesn't matter for binary search to work correctly",
        ],
        "non_attempts": [
            "ok thanks", "makes sense now",
            "what happens with duplicate values?",
            "can you explain mid = (low+high)/2?",
            "does it work on linked lists?",
            "how is that different from linear search?",
        ],
    },
    {
        "topic": "Graphs",
        "context": (
            "BFS uses a queue and explores level by level, useful for shortest paths "
            "in unweighted graphs. DFS uses a stack or recursion and explores as deep "
            "as possible before backtracking. Both require marking visited nodes to "
            "avoid infinite loops."
        ),
        "correct": [
            "BFS uses a queue and explores level by level.",
            "DFS goes as deep as possible before backtracking.",
            "You need to mark nodes as visited to avoid infinite loops during traversal.",
            "BFS is good for finding the shortest path in an unweighted graph.",
        ],
        "incorrect": [
            "DFS uses a queue just like BFS does.",
            "You don't need to mark visited nodes if the graph has no cycles.",
            "BFS explores as deep as possible before backtracking.",
            "Marking visited nodes is optional for correctness in any graph.",
            "DFS always finds the shortest path, same as BFS",
        ],
        "non_attempts": [
            "ok got it", "that clears it up",
            "why does DFS use a stack specifically?",
            "can you walk through an example?",
            "what about weighted graphs?",
            "does this apply to trees too?",
        ],
    },
    {
        "topic": "Trees",
        "context": (
            "A binary search tree keeps left subtree values smaller and right subtree "
            "values larger than the node, giving O(log n) search on average. Height is "
            "the longest path from a node to a leaf; depth is distance from the root."
        ),
        "correct": [
            "In a BST, everything in the left subtree is smaller than the node.",
            "BST search is O(log n) on average because of the ordering property.",
            "Height is measured from a node down to the deepest leaf.",
            "Depth is how far a node is from the root.",
        ],
        "incorrect": [
            "A BST doesn't need any particular ordering between left and right subtrees.",
            "BST search is always O(log n) no matter how it's built.",
            "Height and depth mean the same exact thing.",
            "The right subtree in a BST has smaller values than the node.",
            "BSTs don't need a root, any node can start the tree",
        ],
        "non_attempts": [
            "ok that makes sense", "thanks",
            "what happens with duplicate values in a BST?",
            "can unbalanced trees still work?",
            "how is this different from a linked list?",
            "what's a leaf node again?",
        ],
    },
    {
        "topic": "Hashing",
        "context": (
            "Hash tables give average-case O(1) lookup by mapping keys to indices "
            "with a hash function. Collisions happen when two keys hash to the same "
            "index, and must be resolved, e.g. with chaining."
        ),
        "correct": [
            "Hash tables give O(1) average lookup by computing an index directly.",
            "A collision happens when two different keys hash to the same index.",
            "Chaining resolves collisions by storing a list of items at each index.",
            "Hash table performance depends on the quality of the hash function.",
        ],
        "incorrect": [
            "Hash tables are always O(1) no matter how many collisions happen.",
            "Collisions never happen if you use a big enough table.",
            "Chaining means overwriting the old value with the new one.",
            "Hash tables don't need any collision handling at all.",
            "the hash function doesn't affect performance at all",
        ],
        "non_attempts": [
            "got it, thanks", "makes sense",
            "what's open addressing?",
            "why does load factor matter?",
            "can you explain resizing?",
            "is this different from a dictionary?",
        ],
    },
    {
        "topic": "Dynamic Programming",
        "context": (
            "Dynamic programming solves problems with overlapping subproblems and "
            "optimal substructure by storing subproblem results. Memoization is "
            "top-down; tabulation is bottom-up."
        ),
        "correct": [
            "DP works when a problem has overlapping subproblems.",
            "Memoization is top-down and tabulation is bottom-up.",
            "DP avoids recomputing the same subproblem multiple times.",
            "Optimal substructure means the best overall solution comes from combining best sub-solutions.",
        ],
        "incorrect": [
            "DP always makes any recursive solution faster, even without overlapping subproblems.",
            "Memoization is bottom-up and tabulation is top-down.",
            "DP doesn't need optimal substructure to work correctly.",
            "Tabulation uses more call stack space than memoization.",
            "dynamic programming and recursion are completely unrelated concepts",
        ],
        "non_attempts": [
            "ok thanks", "that helps",
            "can you give an example?",
            "what's the coin change problem?",
            "why does order matter when filling the table?",
            "is this the same as greedy algorithms?",
        ],
    },
    {
        "topic": "Linked Lists",
        "context": (
            "A linked list stores nodes with a value and a pointer to the next node. "
            "Insertion and deletion at a known position is O(1) since it only requires "
            "relinking pointers, unlike arrays which require shifting."
        ),
        "correct": [
            "Linked lists don't support O(1) random access like arrays do.",
            "Inserting into a linked list at a known position is O(1) because you just relink pointers.",
            "Each node in a linked list has a value and a pointer to the next node.",
            "Deleting a node is fast if you already have a reference to it.",
        ],
        "incorrect": [
            "Linked lists support O(1) random access just like arrays.",
            "Inserting into a linked list requires shifting elements, same as an array.",
            "A linked list node only stores a value, no pointer.",
            "Deleting from a linked list is always O(n) regardless of the situation.",
            "linked lists and arrays have identical performance characteristics",
        ],
        "non_attempts": [
            "ok got it", "thanks for the explanation",
            "what's a doubly linked list?",
            "can you show me how reversal works?",
            "why do I need to save the next pointer?",
            "is this different from an array list?",
        ],
    },
    {
        "topic": "Stacks and Queues",
        "context": (
            "A stack is LIFO; a queue is FIFO. BFS uses a queue, DFS uses a stack or "
            "recursion. The call stack during recursion is literally a stack."
        ),
        "correct": [
            "A stack is LIFO, last in first out.",
            "A queue is FIFO, first in first out.",
            "BFS uses a queue while DFS uses a stack or recursion.",
            "The call stack during recursion works like a stack data structure.",
        ],
        "incorrect": [
            "A stack is FIFO, first in first out.",
            "BFS uses a stack, not a queue.",
            "A queue and a stack behave exactly the same way.",
            "The call stack has nothing to do with an actual stack data structure.",
            "dequeuing from the front of a queue is always O(n) no matter the implementation",
        ],
        "non_attempts": [
            "ok that makes sense", "thanks",
            "why is popping from an array-based queue slow?",
            "can you explain the two-stack queue trick?",
            "what's an example of using a stack?",
            "does this relate to recursion somehow?",
        ],
    },
]


def run_assessment_accuracy_comparison():
    print("\n" + "=" * 70)
    print("PART 2: ASSESSMENT ACCURACY (dedicated Assessor vs single-agent's judgment)")
    print("Now across all 10 topics -- Phase 7 found 13-20% cross-topic mismatch")
    print("when the Assessor was tested outside its original recursion tuning.")
    print("=" * 70)

    records = []  # every judgment, saved for reproducible stats later

    def score_labeled_set(messages, expected_attempt, expected_correct, topic, context):
        multi_correct_judgments = 0
        single_correct_judgments = 0

        for msg in messages:
            assessor_result = assess_message(msg, topic, context)
            single_result = single_agent_interact(msg, topic, context, 0.5)

            assessor_ok = (assessor_result["is_attempt"] == expected_attempt) and \
                          (expected_attempt is False or assessor_result["correct"] == expected_correct)
            single_ok = (single_result["is_attempt"] == expected_attempt) and \
                        (expected_attempt is False or single_result["correct"] == expected_correct)

            records.append({
                "topic": topic,
                "message": msg,
                "expected_attempt": expected_attempt,
                "expected_correct": expected_correct,
                "assessor_ok": assessor_ok,
                "single_ok": single_ok,
            })

            if assessor_ok:
                multi_correct_judgments += 1
            if single_ok:
                single_correct_judgments += 1

            if assessor_ok != single_ok:
                print(f"  [DIVERGENCE] [{topic}] \"{msg[:50]}\" -- Assessor correct={assessor_ok}, Single-agent correct={single_ok}")

        return multi_correct_judgments, single_correct_judgments, len(messages)

    grand_total_assessor = 0
    grand_total_single = 0
    grand_total_n = 0
    per_topic_results = []

    for test_set in ASSESSMENT_TEST_SETS:
        topic = test_set["topic"]
        context = test_set["context"]
        print(f"\n--- {topic} ---")

        a1, s1, n1 = score_labeled_set(test_set["correct"], True, True, topic, context)
        a2, s2, n2 = score_labeled_set(test_set["incorrect"], True, False, topic, context)
        a3, s3, n3 = score_labeled_set(test_set["non_attempts"], False, None, topic, context)

        topic_assessor = a1 + a2 + a3
        topic_single = s1 + s2 + s3
        topic_n = n1 + n2 + n3

        print(f"  {topic}: Assessor {topic_assessor}/{topic_n} ({topic_assessor/topic_n*100:.1f}%), "
              f"Single-agent {topic_single}/{topic_n} ({topic_single/topic_n*100:.1f}%)")

        per_topic_results.append({"topic": topic, "assessor_acc": topic_assessor / topic_n,
                                   "single_acc": topic_single / topic_n, "n": topic_n})

        grand_total_assessor += topic_assessor
        grand_total_single += topic_single
        grand_total_n += topic_n

    # Save every record for reproducible stats
    with open("assessment_accuracy_records.jsonl", "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    print(f"\nSaved {len(records)} judgment records -> assessment_accuracy_records.jsonl")

    print(f"\n--- Assessment Accuracy Summary (all 10 topics) ---")
    print(f"  Dedicated Assessor: {grand_total_assessor}/{grand_total_n} ({grand_total_assessor/grand_total_n*100:.1f}%)")
    print(f"  Single-agent:       {grand_total_single}/{grand_total_n} ({grand_total_single/grand_total_n*100:.1f}%)")

    non_recursion = [r for r in per_topic_results if r["topic"] != "Recursion"]
    if non_recursion:
        avg = sum(r["assessor_acc"] for r in non_recursion) / len(non_recursion)
        print(f"\n  Assessor accuracy on non-recursion topics (avg): {avg*100:.1f}%")
        print(f"  (compare against Phase 7's documented 13-20% cross-topic mismatch)")


if __name__ == "__main__":
    run_response_quality_comparison()
    run_assessment_accuracy_comparison()