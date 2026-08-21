"""
Pydantic schemas -- API-facing shapes, kept separate from the SQLAlchemy
models in db_models.py so the DB structure can evolve without breaking the
API contract (and vice versa).
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class StudentCreate(BaseModel):
    name: str


class StudentOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TopicOut(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    difficulty_level: int
    prerequisites: List[str] = []

    class Config:
        from_attributes = True


class SkillStateOut(BaseModel):
    topic_slug: str
    p_know: float
    attempts: int
    correct: int
    last_updated: datetime


class InteractionRequest(BaseModel):
    student_id: int
    message: str
    topic_slug: Optional[str] = None
    session_id: Optional[int] = None


class InteractionResponse(BaseModel):
    tutor_response: str
    topic_slug: Optional[str]
    p_know_before: Optional[float]
    p_know_after: Optional[float]
    agent_trace: List[Dict[str, Any]] = []
    retrieved_chunk_ids: List[int] = []
    is_grounded: Optional[bool]
    extracted_features: Optional[Dict[str, Any]] = None

class AttemptRequest(BaseModel):
    correct: bool

class AttemptResponse(BaseModel):
    topic_slug: str
    p_know_before: float
    p_know_after: float
    attempts: int
    correct: int

class RecommendationOut(BaseModel):
    recommended_topic: str
    reasoning: str
    student_mastery: Dict[str, float]
    blocked_topics: Optional[List[Dict[str, Any]]] = None

class SessionCreate(BaseModel):
    student_id: int


class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionMessageOut(BaseModel):
    student_input: str
    tutor_response: str
    topic_slug: Optional[str]
    timestamp: datetime
    agent_trace: List[Dict[str, Any]] = []

class AskQuestionRequest(BaseModel):
    student_id: int
    topic_slug: str
    session_id: Optional[int] = None


class AskQuestionResponse(BaseModel):
    question: str
    topic_slug: str
    retrieved_chunk_ids: List[int] = []