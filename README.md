# 🧠 NeuronPath AI — Adaptive Learning Path Platform

> **AI-Powered Personalized Learning Path Recommender, Milestone Roadmap Generator, and Skill Mastery Engine**

---

## 🌟 Overview

**NeuronPath AI** is an intelligent, full-stack learning platform designed to take learners from their current skill set to their dream career goals. It analyzes natural-language learning objectives, maps domain-specific skill graphs, generates fine-grained prerequisite-aware roadmaps, recommends curated multi-format resources, and provides adaptive assessments that unlock progressive milestones.

---

## ✨ Key Features

- **🗣️ Natural Language AI Onboarding**: Conversational goal extraction powered by Google Gemini LLM with structured profile synthesis and real-time parameter editing.
- **🗺️ Granular Milestone Roadmap Generator**: Dynamically decomposes career tracks into 6–16 sequential milestones with strict topological prerequisite ordering.
- **📚 Curated Multi-Format Resource Catalog**: 200+ verified courses, official documentation, video masterclasses, interactive coding sandboxes (LeetCode, Killercoda, Play with Docker), and canonical industry textbooks (CLRS, DDIA, Fluent Python, Clean Code).
- **📝 Milestone-Aligned Assessments**: 10-question technical quizzes per milestone featuring balanced option length parity, randomized answer positioning, and automated grading.
- **🔄 Dynamic Adaptive Feedback Loop**: Real-time mastery scoring ($\ge 70\%$ threshold) that dynamically updates skill confidence, unlocks subsequent milestones, and triggers remediation where needed.
- **📊 Interactive Skill Proficiency Matrix**: Real-time tracking of Mastered, Developing, Weak, and Missing skills with glassmorphism detail modals.
- **🤖 Context-Aware AI Learning Coach**: Conversational guidance with live learner state injection (current milestone, active skill gaps, and recent assessment performance).
- **🌓 Accessible Dark & Light Modes**: WCAG AA-compliant high-contrast theme system with persistent local storage.

---

## 🛠️ Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│                   Frontend (Client)                    │
│      React 18 • TypeScript • Tailwind CSS • Vite       │
│        Zustand (State) • Lucide Icons • Axios          │
└───────────────────────────┬────────────────────────────┘
                            │ REST APIs (/api/*)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Backend (Server)                     │
│           FastAPI • Uvicorn • Pydantic v2              │
│       SQLAlchemy ORM • Directed Acyclic Graph          │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
   ┌───────────────────────┐  ┌─────────────────────────┐
   │ Database Storage      │  │ LLM Intelligence        │
   │ SQLite / PostgreSQL   │  │ Google Gemini API       │
   └───────────────────────┘  └─────────────────────────┘
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure environment variables in backend/.env
# LLM_API_KEY=your_gemini_api_key
# DATABASE_URL=sqlite:///./neuronpath.db

# Run FastAPI backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Run Vite dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Running Automated Tests

```bash
cd backend
python test_real_learner_e2e.py
python test_milestone_task_distinctness.py
python test_roadmap_milestone_aligned_assessments.py
```

---

## 📄 License

MIT License — free for educational and production use.
