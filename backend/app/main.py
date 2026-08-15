"""
Main FastAPI app.

Live: student creation, topic listing, skill-state lookup, and
/tutor/interact -- a full 3-agent pipeline (Planner, Assessor, Tutor)
with RAG retrieval, BKT skill updates, grounding audit, LLM-as-judge
scoring, and classical-scorer feature extraction, all logged per
interaction via agent_trace and extracted_features.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.skill_tracker import record_attempt
from app.database import get_db, init_db
from app.models.db_models import Student, Topic, SkillState
from app import schemas
from app.services.retrieval import retrieve_relevant_chunks
from app.services.generation import generate_response
from app.services.grounding import compute_grounding_score, is_grounded
from app.models.db_models import SkillState, Interaction
from app.services.assessor import assess_message
from app.services.bkt import update_p_know
from app.services.planner import plan_next_topic
from app.services.feature_extraction import extract_features

app = FastAPI(title="Intelligent Personalized Programming Tutor")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(name=student.name)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/topics", response_model=list[schemas.TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).all()


@app.get("/students/{student_id}/skills", response_model=list[schemas.SkillStateOut])
def get_skill_states(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    states = db.query(SkillState).filter(SkillState.student_id == student_id).all()
    return [
        schemas.SkillStateOut(
            topic_slug=s.topic.slug,
            p_know=s.p_know,
            attempts=s.attempts,
            correct=s.correct,
            last_updated=s.last_updated,
        )
        for s in states
    ]

@app.post("/students/{student_id}/topics/{topic_slug}/attempt", response_model=schemas.AttemptResponse)
def submit_attempt(
    student_id: int, topic_slug: str, req: schemas.AttemptRequest, db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        result = record_attempt(db, student_id, topic_slug, req.correct)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result

@app.post("/tutor/interact", response_model=schemas.InteractionResponse)
def tutor_interact(req: schemas.InteractionRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    planner_reasoning = None
    topic_slug = req.topic_slug

    if not topic_slug:
        plan = plan_next_topic(db, req.student_id)
        topic_slug = plan["recommended_topic"]
        planner_reasoning = plan["reasoning"]

    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get or create skill state
    state = (
        db.query(SkillState)
        .filter(SkillState.student_id == req.student_id, SkillState.topic_id == topic.id)
        .first()
    )
    if not state:
        state = SkillState(student_id=req.student_id, topic_id=topic.id)
        db.add(state)
        db.flush()

    p_know_before = state.p_know

    # Retrieval
    retrieved = retrieve_relevant_chunks(db, req.message, topic_slug, top_k=3)
    context_text = "\n".join(c["content"] for c in retrieved)

    # Assessor Agent: is this an attempt, and is it correct?
    assessment = assess_message(req.message, topic.title, context_text)

    # BKT update -- ONLY if the assessor judged this as a real attempt
    p_know_after = p_know_before
    if assessment["is_attempt"] and assessment["correct"] is not None:
        p_know_after = update_p_know(
            p_know=p_know_before,
            correct=assessment["correct"],
            p_slip=state.p_slip,
            p_transit=state.p_transit,
            p_guess=state.p_guess,
        )
        state.p_know = p_know_after
        state.attempts += 1
        if assessment["correct"]:
            state.correct += 1

    # Tutor Agent: generate the actual response
    response_text = generate_response(req.message, retrieved, p_know_after)

    # Grounding audit
    grounding_score = compute_grounding_score(response_text, retrieved)
    grounded = is_grounded(response_text, retrieved)

    features = extract_features(
        student_message=req.message,
        retrieved_chunks=[c["content"] for c in retrieved],
        p_know=p_know_after,
        tutor_response=response_text,
    )

    # Log everything, including BOTH agents' reasoning
    interaction = Interaction(
        student_id=req.student_id,
        topic_id=topic.id,
        student_input=req.message,
        tutor_response=response_text,
        retrieved_chunk_ids=[c["chunk_id"] for c in retrieved],
        is_grounded=grounded,
        grounding_score=grounding_score,
        was_correct=assessment["correct"],
        p_know_before=p_know_before,
        p_know_after=p_know_after,
        extracted_features=features,
        agent_trace=[
            *([{
                "agent": "planner",
                "recommended_topic": topic_slug,
                "reasoning": planner_reasoning,
            }] if planner_reasoning else []),
            {
                "agent": "assessor",
                "is_attempt": assessment["is_attempt"],
                "correct": assessment["correct"],
                "reasoning": assessment["reasoning"],
            },
            {
                "agent": "tutor",
                "retrieved_count": len(retrieved),
                "top_similarity": retrieved[0]["similarity"] if retrieved else None,
                "grounding_score": grounding_score,
            },
            
        ],
    )
    db.add(interaction)
    db.commit()

    return schemas.InteractionResponse(
        tutor_response=response_text,
        topic_slug=topic_slug,
        p_know_before=p_know_before,
        p_know_after=p_know_after,
        extracted_features=features,
        agent_trace=interaction.agent_trace,
        retrieved_chunk_ids=interaction.retrieved_chunk_ids,
        is_grounded=grounded,
    )