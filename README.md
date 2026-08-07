# Intelligent Personalized Programming Tutor — Design Project

Agentic RAG tutoring system with BKT/IRT skill modeling, decision transparency,
multi-agent architecture, LoRA fine-tuning, and LLM-as-judge evaluation.

## Current Status: Phase 1 Complete (Foundation)

Built so far:
- **Curriculum data** (`backend/curriculum_data/dsa_topics.json`) — 5 DSA/C topics
  (arrays, recursion, sorting, searching, graphs) with prerequisites and content
  chunks tagged by type (explanation / example / practice_problem) and difficulty.
- **DB schema** (`backend/app/models/db_models.py`) — Student, Topic, SkillState,
  CurriculumChunk, Interaction. `SkillState` and `Interaction` are built with the
  *entire rest of the project* in mind: BKT fields, agent traces, and grounding-audit
  fields are already present as columns, not bolted on later.
- **FastAPI skeleton** (`backend/app/main.py`) — student creation, topic listing,
  skill-state lookup, and a deliberately stubbed `/tutor/interact` endpoint.
- Verified end-to-end: DB creation, curriculum seeding (5 topics / 15 chunks loaded
  successfully), and all API endpoints tested live.

## Project Structure
```
backend/
  app/
    models/db_models.py     # SQLAlchemy models (Student, Topic, SkillState, Interaction, CurriculumChunk)
    curriculum/seed.py       # loads dsa_topics.json into DB
    routers/                 # (empty -- split main.py here as it grows)
    services/                # (empty -- BKT model, RAG, agents go here next)
    database.py               # DB session setup
    schemas.py                 # Pydantic request/response models
    main.py                     # FastAPI app entrypoint
  curriculum_data/
    dsa_topics.json            # source curriculum content
  requirements.txt
frontend/                       # (not started yet)
```

## Running It
```bash
cd backend
pip install -r requirements.txt
python -m app.curriculum.seed   # seeds the DB with curriculum content
uvicorn app.main:app --reload
```
Then visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Next Build Step: Phase 2 — BKT/IRT Skill Model (#3)
This is the critical-path item everything else depends on. Goal: implement
Bayesian Knowledge Tracing so that `SkillState.p_know` updates correctly based
on whether a student's answer was correct, using the standard BKT update
equations (p_transit, p_slip, p_guess already scaffolded in the model).

Do not proceed to RAG (#5) or agents (#7) until this produces sane, testable
mastery estimates on a few manual scenarios.
