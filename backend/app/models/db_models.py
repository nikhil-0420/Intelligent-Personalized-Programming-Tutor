"""
Database models for the Intelligent Personalized Programming Tutor.

Design notes:
- SkillState is deliberately separate from Student — one row per (student, topic) pair.
  This is what the BKT/IRT layer reads and writes. Keeping it separate (rather than a
  JSON blob on Student) means we can query/aggregate mastery trends per topic later,
  which the transparency dashboard and eval framework both depend on.
- Interaction stores EVERYTHING about a single tutor exchange, including the raw
  retrieved RAG chunks and which agent(s) touched it. This is what the grounding audit
  and ablation studies query against later — build this logging in now, not later.
"""

from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    skill_states = relationship("SkillState", back_populates="student")
    interactions = relationship("Interaction", back_populates="student")

class ChatSession(Base):
    """
    Groups a sequence of Interactions into one named conversation,
    the same way Claude groups messages into a saved chat.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String, default="New chat")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", backref="chat_sessions")

class Topic(Base):
    """
    A single curriculum unit (e.g. 'recursion', 'binary_search').
    Topics can have prerequisites -- this is what the Curriculum Planner Agent
    will later use to decide what's teachable next given current mastery.
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)       # e.g. "recursion"
    title = Column(String, nullable=False)                    # e.g. "Recursion"
    description = Column(Text)
    difficulty_level = Column(Integer, default=1)             # 1=intro .. 5=advanced
    prerequisites = Column(JSON, default=list)                 # list of topic slugs

    skill_states = relationship("SkillState", back_populates="topic")


class SkillState(Base):
    """
    One row per (student, topic). This is the BKT/IRT layer's persistent state.

    BKT fields (if using Bayesian Knowledge Tracing):
      p_know        - current probability the student has mastered this topic
      p_transit     - probability of learning it on a single attempt (learn rate)
      p_slip        - probability of a correct answer despite not knowing it (careless error)
      p_guess       - probability of an incorrect answer despite knowing it

    IRT fields (if using Item Response Theory instead/also):
      theta         - student ability estimate for this topic

    attempts / correct are raw counts, kept alongside the probabilistic estimate
    so you can sanity-check the model against ground truth during development.
    """
    __tablename__ = "skill_states"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    p_know = Column(Float, default=0.1)        # BKT: prior probability of mastery
    p_transit = Column(Float, default=0.3)     # BKT: learn rate
    p_slip = Column(Float, default=0.1)        # BKT: slip probability
    p_guess = Column(Float, default=0.2)       # BKT: guess probability

    theta = Column(Float, default=0.0)         # IRT: ability estimate (optional, if used)

    attempts = Column(Integer, default=0)
    correct = Column(Integer, default=0)

    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="skill_states")
    topic = relationship("Topic", back_populates="skill_states")


class Interaction(Base):
    """
    Full log of a single tutor exchange. This is the backbone of your
    grounding audit, decision transparency layer, and eval/ablation studies --
    log generously now, since you can't reconstruct this retroactively.
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student_input = Column(Text, nullable=False)
    tutor_response = Column(Text, nullable=False)

    # --- RAG / grounding audit fields ---
    retrieved_chunk_ids = Column(JSON, default=list)   # which curriculum chunks were retrieved
    is_grounded = Column(Boolean, default=None)         # did response actually use retrieved content?
    grounding_score = Column(Float, default=None)       # optional continuous score
    interaction_type = Column(String, default="explanation")  # "explanation" | "question"

    # --- agent / decision transparency fields ---
    agent_trace = Column(JSON, default=list)
    # e.g. [{"agent": "planner", "decision": "review recursion", "confidence": 0.82,
    #        "reason": "p_know=0.34, below mastery threshold 0.6"}, ...]

    # --- skill update fields (what changed as a result of this interaction) ---
    was_correct = Column(Boolean, default=None)
    p_know_before = Column(Float, default=None)
    p_know_after = Column(Float, default=None)

    # --- eval fields (filled in later by LLM-as-judge / human eval pass) ---
    judge_score = Column(Float, default=None)
    judge_rationale = Column(Text, default=None)
    human_eval_score = Column(Float, default=None)
    extracted_features = Column(JSON, default=None)

    student = relationship("Student", back_populates="interactions")


class CurriculumChunk(Base):
    """
    A single retrievable unit of curriculum content for RAG.
    Kept in the DB (not just files) so retrieval can be logged by chunk ID
    for the grounding audit, and so difficulty/topic filters can be applied
    at query time.
    """
    __tablename__ = "curriculum_chunks"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    content = Column(Text, nullable=False)
    difficulty_level = Column(Integer, default=1)
    chunk_type = Column(String, default="explanation")  # explanation | example | practice_problem
    source_file = Column(String, nullable=True)
    embedding = Column(JSON, nullable=True)  # pre-computed embedding vector, list[float]
