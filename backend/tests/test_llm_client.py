from app.services.llm_client import generate_text

response = generate_text("Explain recursion in one sentence.", temperature=0.7)
print(response)