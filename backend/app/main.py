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
from app.models.db_models import ChatSession
from fastapi.middleware.cors import CORSMiddleware
from app.services.question_generator import generate_question

app = FastAPI(title="Intelligent Personalized Programming Tutor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://programmingtutor-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/sessions", response_model=schemas.SessionOut)
def create_session(req: schemas.SessionCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    session = ChatSession(student_id=req.student_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.get("/students/{student_id}/sessions", response_model=list[schemas.SessionOut])
def list_sessions(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ChatSession)
        .filter(ChatSession.student_id == student_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@app.get("/sessions/{session_id}/messages", response_model=list[schemas.SessionMessageOut])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    interactions = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.timestamp.asc())
        .all()
    )

    topic_ids = {i.topic_id for i in interactions if i.topic_id}
    topics_by_id = {
        t.id: t.slug for t in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
    }

    return [
        schemas.SessionMessageOut(
            student_input=i.student_input,
            tutor_response=i.tutor_response,
            topic_slug=topics_by_id.get(i.topic_id),
            timestamp=i.timestamp,
            agent_trace=i.agent_trace or [],
        )
        for i in interactions
    ]

@app.get("/topics", response_model=list[schemas.TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).all()

@app.get("/students/{student_id}/recommend-topic", response_model=schemas.RecommendationOut)
def recommend_topic(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    plan = plan_next_topic(db, student_id)
    return schemas.RecommendationOut(**plan)

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

    # Check if the last interaction in this session was a posed question --
    # if so, the Assessor should judge this message as an answer to it specifically
    posed_question = None
    if req.session_id:
        last_interaction = (
            db.query(Interaction)
            .filter(Interaction.session_id == req.session_id)
            .order_by(Interaction.timestamp.desc())
            .first()
        )
        if last_interaction and last_interaction.interaction_type == "question":
            posed_question = last_interaction.tutor_response

    # Assessor Agent: is this an attempt, and is it correct?
    assessment = assess_message(req.message, topic.title, context_text, posed_question=posed_question)

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
        session_id=req.session_id,
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
        # Auto-title the session from the first message, same pattern as Claude's chat titles
    if req.session_id:
        session_obj = db.query(ChatSession).filter(ChatSession.id == req.session_id).first()
        if session_obj and session_obj.title == "New chat":
            title = req.message.strip()
            session_obj.title = title[:47] + "..." if len(title) > 50 else title
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

@app.post("/tutor/ask-question", response_model=schemas.AskQuestionResponse)
def ask_question(req: schemas.AskQuestionRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    topic = db.query(Topic).filter(Topic.slug == req.topic_slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    state = (
        db.query(SkillState)
        .filter(SkillState.student_id == req.student_id, SkillState.topic_id == topic.id)
        .first()
    )
    p_know = state.p_know if state else 0.1

    retrieved = retrieve_relevant_chunks(db, topic.title, req.topic_slug, top_k=3)
    question = generate_question(topic.title, retrieved, p_know)

    interaction = Interaction(
        student_id=req.student_id,
        topic_id=topic.id,
        session_id=req.session_id,
        student_input="[system] requested practice question",
        tutor_response=question,
        interaction_type="question",
        retrieved_chunk_ids=[c["chunk_id"] for c in retrieved],
        agent_trace=[{"agent": "question_generator", "topic": req.topic_slug, "p_know": p_know}],
    )
    db.add(interaction)
    db.commit()

    return schemas.AskQuestionResponse(
        question=question,
        topic_slug=req.topic_slug,
        retrieved_chunk_ids=[c["chunk_id"] for c in retrieved],
    )