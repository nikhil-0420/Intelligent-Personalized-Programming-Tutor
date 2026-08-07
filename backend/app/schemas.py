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
    topic_slug: Optional[str] = None   # if None, planner agent should infer it


class InteractionResponse(BaseModel):
    tutor_response: str
    topic_slug: Optional[str]
    p_know_before: Optional[float]
    p_know_after: Optional[float]
    agent_trace: List[Dict[str, Any]] = []
    retrieved_chunk_ids: List[int] = []
    is_grounded: Optional[bool]

class AttemptRequest(BaseModel):
    correct: bool

class AttemptResponse(BaseModel):
    topic_slug: str
    p_know_before: float
    p_know_after: float
    attempts: int
    correct: int