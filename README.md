# 🧠 NeuronPath AI

> **AI-Powered Personalized Learning Path Recommender, Milestone Roadmap Generator, and Skill Mastery Platform.**

---

## 🌐 Live Demo

- **Application URL**: [https://neuronpath-ai.vercel.app/](https://neuronpath-ai.vercel.app/)

---

## 📖 What is NeuronPath AI?

**NeuronPath AI** is an intelligent, full-stack career acceleration and learning roadmap platform. It takes a learner's natural language career ambition, analyzes baseline proficiencies against required target skills, synthesizes custom prerequisite-ordered milestone roadmaps, curates multi-format learning resources, and adapts dynamically through technical assessments and conversational AI coaching.

---

## ✨ Key Features

- **🗺️ Personalized Learning Roadmaps**: Dynamically generates fine-grained milestones decomposed with strict topological prerequisite ordering based on the user's chosen track.
- **🗣️ AI-Powered Onboarding**: Conversational goal extraction powered by Google Gemini LLM to automatically parse target roles, timelines, and known skills.
- **🎯 Career & Learning Goals**: Target role alignment with estimated timelines, proficiency benchmarks, and personalized milestones.
- **📊 Skill Gap Analysis**: Real-time evaluation comparing current learner proficiencies with target industry requirements.
- **📚 Curated Learning Resources**: Verified courses, official documentation, video masterclasses, interactive coding sandboxes, and canonical industry textbooks mapped to specific milestones.
- **📝 Assessments & Progress Tracking**: Milestone-aligned quizzes with automated scoring, adaptive feedback ($\ge 70\%$ mastery threshold), and comprehensive visual analytics.
- **🤖 Context-Aware AI Learning Coach**: Real-time conversational guidance with live learner context injection (active goal, current milestone, and skill gaps).
- **🔀 Multi-Goal Management & Switching**: Supports up to 3 distinct learning goals with instant 1-click switching, isolated roadmap progression, and safe goal deletion.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Zustand (State Management), Lucide React (Icons), Recharts (Visualizations), Axios (API Client)
- **Backend**: FastAPI, Python 3.10+, SQLAlchemy ORM, Pydantic v2, Uvicorn, PyJWT (Authentication), bcrypt (Password Hashing)
- **Database**: PostgreSQL (Supabase in production) / SQLite (Local development)
- **AI / LLM**: Google Gemini API (`gemini-2.0-flash` via `google-generativeai`), with provider fallback architecture
- **Deployment**: Vercel (Frontend SPA), Render (Backend API Service)

---

## 🏗️ Architecture & How It Works

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
   │ PostgreSQL / SQLite   │  │ Google Gemini API       │
   └───────────────────────┘  └─────────────────────────┘
```

### User Flow
1. **Sign Up & Onboarding**: The user signs up and enters their learning ambition in natural language.
2. **Goal Extraction**: The AI extracts the target role, experience level, and timeline, creating their initial goal.
3. **Roadmap Generation**: A Directed Acyclic Graph (DAG) organizes sequential milestones with curated learning resources.
4. **Learning & Milestone Assessments**: The learner works through milestone items and completes technical quizzes to validate mastery and unlock next steps.
5. **Multi-Goal Switching & AI Coach**: Learners can add up to 3 distinct goals, switch active paths seamlessly, and chat with the AI coach for contextual guidance.

---

## 🚀 Local Setup

### Prerequisites
- **Node.js 18+** & **npm**
- **Python 3.10+**

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

# Run FastAPI backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The backend API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000) (Interactive Swagger Docs at `/docs`).

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev
```

The frontend application will be accessible at [http://localhost:5173](http://localhost:5173).

---

## 🌐 Production & Deployment

- **Frontend**: Hosted on [Vercel](https://vercel.com) ([https://neuronpath-ai.vercel.app/](https://neuronpath-ai.vercel.app/))
- **Backend**: Hosted on [Render](https://render.com) ([https://neuronpath-api.onrender.com/](https://neuronpath-api.onrender.com/))

---

## ⚠️ Important Note — Cold Start

> The deployed backend runs on a free-tier service and may enter a sleep state. The first request after inactivity can take approximately 60 seconds to wake up. Subsequent requests should respond normally.

---

## 📁 Project Structure

```text
PathFinder AI/
├── backend/
│   ├── ai/               # LLM provider integration & onboarding extraction
│   ├── api/              # FastAPI routers (auth, goals, roadmap, skills, etc.)
│   ├── core/             # Security, JWT, and authentication dependencies
│   ├── models/           # SQLAlchemy ORM models
│   ├── recommendation/   # Prerequisite graph and recommendation scoring
│   ├── schemas/          # Pydantic validation schemas
│   ├── services/         # Business logic (goals, roadmaps, assessments)
│   ├── tests/            # Pytest test suites
│   ├── main.py           # Application entrypoint & middleware configuration
│   └── requirements.txt  # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios API client functions
│   │   ├── components/   # UI components (goals dropdown, modals, cards)
│   │   ├── pages/        # Route views (Dashboard, Roadmap, Skills, Coach, etc.)
│   │   ├── store/        # Zustand state store with localStorage persistence
│   │   └── types/        # TypeScript interfaces and data types
│   ├── package.json      # Node.js dependencies and scripts
│   └── vite.config.ts    # Vite bundler configuration
└── README.md             # Project documentation
```

---

## 🔐 Security & Environment Variables

All sensitive API keys and secrets (e.g., `LLM_API_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`) must be stored in environment variables and never committed to version control. 

Example environment configuration for backend:
```env
LLM_PROVIDER=google
LLM_MODEL=gemini-2.0-flash
LLM_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./neuronpath.db
JWT_SECRET_KEY=your_jwt_secret_key_here
```

---

## 📄 License

MIT License — free for educational and commercial use.
