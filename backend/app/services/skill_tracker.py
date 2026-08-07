"""
Handles fetching/creating SkillState rows and applying BKT updates.
Kept separate from main.py so this logic is reusable by the agents later,
not just the direct /attempt endpoint.
"""

from sqlalchemy.orm import Session
from app.models.db_models import SkillState, Topic
from app.services.bkt import update_p_know
from app.models.db_models import SkillState, Topic, Interaction

def get_or_create_skill_state(db: Session, student_id: int, topic_id: int) -> SkillState:
    state = (
        db.query(SkillState)
        .filter(SkillState.student_id == student_id, SkillState.topic_id == topic_id)
        .first()
    )
    if state:
        return state

    # No prior state -- create with default BKT priors (already set as column defaults)
    state = SkillState(student_id=student_id, topic_id=topic_id)
    db.add(state)
    db.flush()  # get state.id without full commit yet
    return state


def record_attempt(db: Session, student_id: int, topic_slug: str, correct: bool) -> dict:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        raise ValueError(f"Unknown topic slug: {topic_slug}")

    state = get_or_create_skill_state(db, student_id, topic.id)

    p_know_before = state.p_know
    p_know_after = update_p_know(
        p_know=state.p_know,
        correct=correct,
        p_slip=state.p_slip,
        p_transit=state.p_transit,
        p_guess=state.p_guess,
    )

    state.p_know = p_know_after
    state.attempts += 1
    if correct:
        state.correct += 1

    db.commit()
    db.refresh(state)

    db.commit()
    db.refresh(state)

    # Decision transparency: log WHY this update happened, not just the numbers
    reasoning = (
        f"Observed {'correct' if correct else 'incorrect'} attempt on '{topic_slug}'. "
        f"p_know moved {p_know_before:.3f} -> {p_know_after:.3f} "
        f"(slip={state.p_slip}, guess={state.p_guess}, transit={state.p_transit}). "
        f"{'Above' if p_know_after >= 0.6 else 'Below'} mastery threshold (0.6)."
    )

    interaction = Interaction(
        student_id=student_id,
        topic_id=topic.id,
        student_input=f"[attempt] correct={correct}",
        tutor_response="[no tutor response yet -- BKT-only phase]",
        was_correct=correct,
        p_know_before=p_know_before,
        p_know_after=p_know_after,
        agent_trace=[{"agent": "bkt_tracker", "reasoning": reasoning}],
    )
    db.add(interaction)
    db.commit()

    return {
        "topic_slug": topic_slug,
        "p_know_before": p_know_before,
        "p_know_after": p_know_after,
        "attempts": state.attempts,
        "correct": state.correct,
    }