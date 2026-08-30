# NeuronPath — Architecture & AI Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    │
│  │ Land │ │Onbrd │ │ Dash │ │Roadm │ │Coach │ │Assmt │    │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘    │
│     └────────┴────────┴────────┴────────┴────────┘          │
│                      ↕ Axios HTTP                            │
├─────────────────────────────────────────────────────────────┤
│                  Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                  API Layer (api/)                    │     │
│  │  learners │ roadmap │ skills │ coach │ assessments  │     │
│  │  recommendations │ resources │ progress │ demo      │     │
│  └─────────────────────┬───────────────────────────────┘     │
│                        │                                     │
│  ┌─────────────────────┴───────────────────────────────┐     │
│  │              Service Layer (services/)               │     │
│  │  learner │ goal │ skill │ roadmap │ assessment       │     │
│  │  progress │ adaptation                               │     │
│  └─────────┬───────────────────────────┬───────────────┘     │
│            │                           │                     │
│  ┌─────────┴─────────┐  ┌─────────────┴───────────────┐     │
│  │ Recommendation     │  │    AI Module (ai/)           │     │
│  │ Engine             │  │  coach │ onboarding          │     │
│  │  engine.py         │  │  provider │ fallback         │     │
│  │  skill_gap.py      │  │                              │     │
│  │  prerequisite.py   │  │  Intent Detection            │     │
│  │  explainer.py      │  │  Context Retrieval           │     │
│  └────────────────────┘  │  LLM Orchestration           │     │
│                          └──────────────────────────────┘     │
│                        ↕                                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │           Data Layer (SQLAlchemy + SQLite)           │     │
│  │  Learner │ Skill │ Resource │ Roadmap │ Assessment  │     │
│  │  ChatMessage │ LearningActivity │ GoalRequirements  │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## AI/ML Design

### 1. Recommendation Engine (`recommendation/engine.py`)

**Multi-Factor Weighted Scoring Algorithm:**

Each resource receives a score from 0-100 based on 7 weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Goal Relevance | 0.25 | Does the resource teach skills required for the learner's goal? |
| Skill Gap Coverage | 0.25 | Does it target the learner's weakest areas? Uses `gap × weight` |
| Prerequisite Readiness | 0.15 | Has the learner mastered prerequisites for this resource? |
| Difficulty Match | 0.15 | Is the difficulty appropriate for the learner's level? |
| Format Preference | 0.05 | Does it match the learner's preferred formats? |
| Quality Score | 0.10 | Provider quality rating |
| Time Fit | 0.05 | Does the duration fit the learner's weekly availability? |

**Why this approach:**
- Deterministic and explainable (no black-box ML)
- Differentiates between learner profiles (verified: beginner gets 24 gaps, intermediate gets 22)
- Each factor is independently testable
- Score breakdown can be shown to the user for transparency

### 2. Skill Gap Analysis (`recommendation/skill_gap.py`)

```
Priority = Gap × Weight × (1 + Prerequisite Urgency)

where:
  Gap = max(0, Required Proficiency - Current Proficiency)
  Weight = importance of this skill for the goal (from GoalSkillRequirement)
  Prerequisite Urgency = min(0.5, dependent_count × 0.1)
```

**Prerequisite Urgency** gives bonus priority to foundational skills that many other required skills depend on. For example, "Python Basics" has high urgency because Linear Algebra, NumPy, Pandas, etc. all depend on it.

### 3. Prerequisite Graph (`recommendation/prerequisite.py`)

- Builds a directed acyclic graph (DAG) from skill prerequisites
- Uses **Kahn's topological sort** to determine optimal learning order
- Filters out already-mastered skills (system_confidence ≥ 70)
- Ensures a learner never encounters a skill before its prerequisites

### 4. System Confidence Calculation

```python
if demonstrated_level is None:
    confidence = self_reported × 0.7    # Discounted (unverified)
else:
    confidence = 0.4 × self_reported + 0.6 × demonstrated
```

Self-reported levels are discounted by 30%. Once a learner takes an assessment, the demonstrated score carries 60% weight.

### 5. Adaptive Learning (`services/adaptation_service.py`)

After each assessment submission, the system applies three-tier adaptation:

| Score | Action | Roadmap Effect |
|-------|--------|----------------|
| < 50% | **Remediation** | Adds beginner resources for weak skills, keeps milestone open |
| 50-70% | **Practice** | Adds intermediate practice resources, milestone stays in progress |
| ≥ 70% | **Acceleration** | Completes milestone, marks all items done, unlocks next milestone |
| ≥ 90% | **Fast Track** | Same as ≥70% plus acceleration suggestion |

This creates a closed feedback loop: Learn → Assess → Adapt → Learn.

### 6. AI Coach (`ai/coach.py`)

**Architecture:**
1. **Intent Detection** — Keyword matching classifies messages into 10 intents
2. **Context Retrieval** — Based on intent, fetches relevant learner data:
   - SKILL_QUERY → skill gaps, current levels
   - ROADMAP_QUERY → current milestone, progress
   - PROGRESS_QUERY → completion stats, assessment history
3. **System Prompt Construction** — Injects all learner context into the LLM prompt
4. **LLM Generation** — Sends to Google Gemini with context + chat history
5. **Fallback** — If LLM unavailable, generates context-aware template responses
6. **Persistence** — All messages saved to ChatMessage table

### 7. Goal Extraction (`ai/onboarding.py`)

Extracts structured data from free-text goals:
- `title` — Goal description
- `target_role` — Career target
- `experience_level` — beginner/intermediate/advanced
- `known_skills` — Skills the learner already has
- `weekly_hours` — Time commitment
- `timeline_months` — Target completion time

Falls back to keyword matching when LLM is unavailable.

---

## Data Model

### Core Entities

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **Learner** | User profile | name, experience_level, weekly_hours, learning_style |
| **Skill** | Knowledge unit | name, category, description |
| **SkillPrerequisite** | DAG edges | skill_id → prerequisite_id, strength |
| **LearnerSkill** | Progress tracking | self_reported, demonstrated, system_confidence |
| **LearnerGoal** | Career target | title, target_role, timeline_months |
| **GoalSkillRequirement** | What a goal needs | skill_id, required_proficiency, weight |
| **Roadmap** | Learning path | learner_id, goal_id, status |
| **RoadmapMilestone** | Path segment | title, objective, status, skill_ids |
| **MilestoneItem** | Learning task | resource_id, item_type, status |
| **Resource** | Learning content | title, type, difficulty, duration_hours |
| **Assessment** | Knowledge test | skill_ids, questions (relationship) |
| **AssessmentQuestion** | Quiz item | question_text, options, correct_answer_index |
| **AssessmentAttempt** | Test result | score, skill_scores (per-skill) |
| **ChatMessage** | Coach history | role, content, intent |

### Seed Data

- **35 skills** across 7 categories (Programming, Math, Data, ML, Advanced ML, MLOps, Soft Skills)
- **45 prerequisite relationships** forming a proper DAG
- **37 resources** across types (video, article, interactive, project)
- **10 projects** from beginner to advanced
- **30+ assessment questions** mapped to specific skills
- **2 demo learners** with distinct profiles and skill levels

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/learners` | Create new learner |
| GET | `/api/learners/{id}` | Get learner profile |
| PUT | `/api/learners/{id}` | Update learner |
| POST | `/api/learners/{id}/onboard` | AI-powered onboarding |
| GET | `/api/learners/{id}/roadmap` | Get active roadmap |
| POST | `/api/learners/{id}/roadmap` | Generate new roadmap |
| GET | `/api/learners/{id}/roadmap/next-action` | Next best action |
| GET | `/api/learners/{id}/skills` | Get learner skills |
| GET | `/api/learners/{id}/skills/gaps` | Skill gap analysis |
| GET | `/api/learners/{id}/recommendations` | Personalized recommendations |
| GET | `/api/learners/{id}/progress` | Full progress analytics |
| POST | `/api/learners/{id}/coach/chat` | AI coach message |
| GET | `/api/learners/{id}/coach/history` | Chat history |
| POST | `/api/assessments/generate` | Generate assessment |
| GET | `/api/assessments/{id}` | Get assessment |
| POST | `/api/assessments/{id}/submit` | Submit + adapt |
| GET | `/api/resources` | List all resources |
| POST | `/api/demo/load` | Load demo data |
