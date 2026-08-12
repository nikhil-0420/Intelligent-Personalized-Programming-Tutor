from app.database import SessionLocal
from app.services.planner import plan_next_topic

db = SessionLocal()
result = plan_next_topic(db, student_id=1)

print("Recommended topic:", result["recommended_topic"])
print("Reasoning:", result["reasoning"])
print("\nMastery map:")
for topic, score in result["student_mastery"].items():
    print(f"  {topic}: {score:.3f}")
print("\nBlocked topics:", result.get("blocked_topics", []))