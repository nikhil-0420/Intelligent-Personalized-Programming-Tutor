from app.database import SessionLocal
from app.services.retrieval import retrieve_relevant_chunks

db = SessionLocal()
results = retrieve_relevant_chunks(db, "why does my recursive function crash", "recursion", top_k=3)

for r in results:
    print(f'{r["similarity"]:.3f} | {r["chunk_type"]} | {r["content"][:80]}...')