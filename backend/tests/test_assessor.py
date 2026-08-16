from app.services.assessor import assess_message

context = "Recursion requires a base case that stops the recursion. Without one, the function calls itself forever until the stack overflows."

# Test 1: an actual attempt, correct
result1 = assess_message(
    "I think recursion needs a base case or it will crash with a stack overflow",
    "Recursion",
    context,
)
print("Test 1 (should be correct attempt):", result1)

# Test 2: an actual attempt, incorrect
result2 = assess_message(
    "Recursion doesn't need any special stopping condition, it just runs until done",
    "Recursion",
    context,
)
print("Test 2 (should be incorrect attempt):", result2)

# Test 3: not an attempt at all, just a question
result3 = assess_message(
    "What's the difference between recursion and iteration?",
    "Recursion",
    context,
)
print("Test 3 (should be is_attempt=False):", result3)