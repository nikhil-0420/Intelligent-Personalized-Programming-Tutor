"""
Main FastAPI app.

Currently live: student creation, topic listing, skill-state lookup.
Stubbed (raises NotImplementedError intentionally): /tutor/interact --
this is where the BKT model (#3), RAG (#5), and agents (#7) plug in.
Leaving it as an explicit stub rather than a fake response so it's obvious
in testing what's real vs. not yet built.
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

    if not req.topic_slug:
        raise HTTPException(status_code=400, detail="topic_slug is required for now (Curriculum Planner Agent comes later in #7)")

    topic = db.query(Topic).filter(Topic.slug == req.topic_slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get current skill state (or defaults if first interaction on this topic)
    state = (
        db.query(SkillState)
        .filter(SkillState.student_id == req.student_id, SkillState.topic_id == topic.id)
        .first()
    )
    p_know = state.p_know if state else 0.1

    # Retrieval
    retrieved = retrieve_relevant_chunks(db, req.message, req.topic_slug, top_k=3)

    # Generation
    response_text = generate_response(req.message, retrieved, p_know)

    # Grounding audit
    grounding_score = compute_grounding_score(response_text, retrieved)
    grounded = is_grounded(response_text, retrieved)

    # Log everything
    interaction = Interaction(
        student_id=req.student_id,
        topic_id=topic.id,
        student_input=req.message,
        tutor_response=response_text,
        retrieved_chunk_ids=[c["chunk_id"] for c in retrieved],
        is_grounded=grounded,
        grounding_score=grounding_score,
        agent_trace=[{
            "agent": "tutor",
            "retrieved_count": len(retrieved),
            "top_similarity": retrieved[0]["similarity"] if retrieved else None,
            "grounding_score": grounding_score,
        }],
    )
    db.add(interaction)
    db.commit()

    return schemas.InteractionResponse(
        tutor_response=response_text,
        topic_slug=req.topic_slug,
        p_know_before=p_know,
        p_know_after=p_know,  # unchanged here -- this endpoint doesn't grade correctness, /attempt does that
        agent_trace=interaction.agent_trace,
        retrieved_chunk_ids=interaction.retrieved_chunk_ids,
        is_grounded=grounded,
    )