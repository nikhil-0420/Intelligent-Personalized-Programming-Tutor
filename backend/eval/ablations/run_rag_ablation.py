"""
Runs the RAG-vs-no-RAG ablation with judge scoring (correctness,
pedagogical_fit) PLUS the grounding.py heuristic (cosine similarity) --
since the LLM judge is known unreliable on groundedness specifically,
but grounding.py's embedding-similarity approach is a validated,
independent way to measure the dimension RAG is actually designed to affect.
"""

from app.database import SessionLocal
from app.services.retrieval import retrieve_relevant_chunks
from app.services.generation import generate_response
from app.services.generation_no_rag import generate_response_no_rag
from app.services.judge import judge_interaction
from app.services.grounding import compute_grounding_score

TRUSTED_DIMENSIONS = ["correctness", "pedagogical_fit"]

TEST_CASES = [
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


def score_condition(query, retrieved_chunks, p_know, response_text):
    result = judge_interaction(
        student_message=query,
        retrieved_chunks=retrieved_chunks,
        p_know=p_know,
        tutor_response=response_text,
    )
    return {dim: result[dim]["score"] for dim in TRUSTED_DIMENSIONS}


def run():
    db = SessionLocal()

    rag_scores = {dim: [] for dim in TRUSTED_DIMENSIONS}
    no_rag_scores = {dim: [] for dim in TRUSTED_DIMENSIONS}
    rag_grounding_scores = []
    no_rag_grounding_scores = []
    per_case_results = []

    for case in TEST_CASES:
        print(f"Running: [{case['topic']}] {case['query'][:50]}...")

        retrieved = retrieve_relevant_chunks(db, case["query"], case["topic"], top_k=3)
        chunk_texts = [c["content"] for c in retrieved]

        rag_response = generate_response(case["query"], retrieved, case["p_know"])
        no_rag_response = generate_response_no_rag(case["query"], case["topic"], case["p_know"])

        rag_result = score_condition(case["query"], chunk_texts, case["p_know"], rag_response)
        no_rag_result = score_condition(case["query"], chunk_texts, case["p_know"], no_rag_response)

        # Grounding: same retrieved chunks used as the reference for BOTH
        # conditions, even though no-RAG never saw them -- we're asking
        # "how similar is this response to the curriculum's actual content,"
        # not "did it use what it was given."
        rag_grounding = compute_grounding_score(rag_response, retrieved)
        no_rag_grounding = compute_grounding_score(no_rag_response, retrieved)

        for dim in TRUSTED_DIMENSIONS:
            if rag_result[dim] is not None:
                rag_scores[dim].append(rag_result[dim])
            if no_rag_result[dim] is not None:
                no_rag_scores[dim].append(no_rag_result[dim])

        rag_grounding_scores.append(rag_grounding)
        no_rag_grounding_scores.append(no_rag_grounding)

        per_case_results.append({
            "topic": case["topic"],
            "query": case["query"],
            "p_know": case["p_know"],
            "rag": rag_result,
            "no_rag": no_rag_result,
            "rag_grounding": rag_grounding,
            "no_rag_grounding": no_rag_grounding,
        })

    print("\n" + "=" * 70)
    print("PER-CASE RESULTS")
    print("=" * 70)
    for r in per_case_results:
        print(f"\n[{r['topic']}, p_know={r['p_know']}] {r['query']}")
        print(f"  RAG:    judge={r['rag']}  grounding={r['rag_grounding']:.3f}")
        print(f"  No-RAG: judge={r['no_rag']}  grounding={r['no_rag_grounding']:.3f}")

    print("\n" + "=" * 70)
    print(f"SUMMARY -- mean scores (n={len(TEST_CASES)})")
    print("=" * 70)
    for dim in TRUSTED_DIMENSIONS:
        rag_mean = sum(rag_scores[dim]) / len(rag_scores[dim]) if rag_scores[dim] else None
        no_rag_mean = sum(no_rag_scores[dim]) / len(no_rag_scores[dim]) if no_rag_scores[dim] else None
        delta = (rag_mean - no_rag_mean) if (rag_mean is not None and no_rag_mean is not None) else None
        print(f"  {dim}: RAG={rag_mean:.2f}  No-RAG={no_rag_mean:.2f}  Delta={delta:+.2f}" if delta is not None
              else f"  {dim}: RAG={rag_mean}  No-RAG={no_rag_mean}")

    rag_g_mean = sum(rag_grounding_scores) / len(rag_grounding_scores)
    no_rag_g_mean = sum(no_rag_grounding_scores) / len(no_rag_grounding_scores)
    print(f"  grounding (cosine sim): RAG={rag_g_mean:.3f}  No-RAG={no_rag_g_mean:.3f}  "
          f"Delta={rag_g_mean - no_rag_g_mean:+.3f}")


if __name__ == "__main__":
    run()