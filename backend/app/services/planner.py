"""
Curriculum Planner Agent -- rule-based, not an LLM call.

Deciding "what topic next" from mastery scores + prerequisites is a
deterministic calculation. An LLM call here would be slower and less
reliable for zero benefit -- this is a defensible architecture choice,
not a shortcut.
"""

from sqlalchemy.orm import Session
from app.models.db_models import Topic, SkillState

MASTERY_THRESHOLD = 0.6


def get_student_mastery_map(db: Session, student_id: int) -> dict[str, float]:
    """Returns {topic_slug: p_know} for every topic, defaulting to 0.1 (prior) if never attempted."""
    all_topics = db.query(Topic).all()
    states = db.query(SkillState).filter(SkillState.student_id == student_id).all()
    state_by_topic_id = {s.topic_id: s.p_know for s in states}

    return {
        topic.slug: state_by_topic_id.get(topic.id, 0.1)
        for topic in all_topics
    }


def plan_next_topic(db: Session, student_id: int) -> dict:
    """
    Returns the recommended next topic + reasoning, in the same
    transparency-first style as the BKT logging.
    """
    all_topics = db.query(Topic).all()
    mastery = get_student_mastery_map(db, student_id)

    ready_topics = []
    blocked_topics = []

    for topic in all_topics:
        prereqs = topic.prerequisites or []
        unmet = [p for p in prereqs if mastery.get(p, 0.1) < MASTERY_THRESHOLD]

        if not unmet:
            ready_topics.append(topic)
        else:
            blocked_topics.append((topic, unmet))

    if not ready_topics:
        fallback = min(all_topics, key=lambda t: len(t.prerequisites or []))
        return {
            "recommended_topic": fallback.slug,
            "reasoning": "No topics currently have every prerequisite met yet — starting with "
                         f"{fallback.title or fallback.slug.replace('_', ' ')}, which has the fewest prerequisites.",
            "student_mastery": mastery,
        }

    # Among ready topics, recommend the one the student knows LEAST
    # (weakest thing they're actually prepared to learn)
    
    next_topic = min(ready_topics, key=lambda t: mastery.get(t.slug, 0.1))

    topic_display = next_topic.title or next_topic.slug.replace("_", " ").title()
    pct = round(mastery.get(next_topic.slug, 0.1) * 100)

    if next_topic.prerequisites:
        prereq_names = [p.replace("_", " ") for p in next_topic.prerequisites]
        if len(prereq_names) == 1:
            prereq_text = prereq_names[0]
        else:
            prereq_text = ", ".join(prereq_names[:-1]) + f" and {prereq_names[-1]}"
        reasoning = (
            f"{topic_display} is a good next step — you've built up enough of a foundation in "
            f"{prereq_text} to take this on, and at {pct}% mastery it's your weakest topic that's "
            f"currently unlocked."
        )
    else:
        reasoning = (
            f"{topic_display} has no prerequisites, and at {pct}% mastery it's your weakest topic "
            f"overall — a good place to start."
        )

    return {
        "recommended_topic": next_topic.slug,
        "reasoning": reasoning,
        "student_mastery": mastery,
        "blocked_topics": [
            {"topic": t.slug, "blocked_by": unmet} for t, unmet in blocked_topics
        ],
    }