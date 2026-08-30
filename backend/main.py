from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from api import routers
from seed import seed_database
from database import SessionLocal
from contextlib import asynccontextmanager
from sqlalchemy import text

def run_migrations():
    """Ensure newly added columns exist in sqlite tables."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE learning_activities ADD COLUMN description TEXT"))
            conn.commit()
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run table creation and column migrations
    run_migrations()
    
    # Auto seed if empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="NeuronPath API",
    description="Backend for AI-Powered Personalized Learning Path Recommender",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.onrender\.com)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router, prefix, tags in routers:
    app.include_router(router, prefix=prefix, tags=tags)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
