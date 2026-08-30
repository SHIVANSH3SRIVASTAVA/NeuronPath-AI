from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from api import routers
from seed import seed_database
from database import SessionLocal
from contextlib import asynccontextmanager
from sqlalchemy import text, inspect

def run_migrations():
    """Ensure newly added columns exist in database tables across PostgreSQL and SQLite."""
    Base.metadata.create_all(bind=engine)
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # 1. Learners table migration
        if "learners" in tables:
            cols = [c["name"] for c in inspector.get_columns("learners")]
            if "hashed_password" not in cols:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("ALTER TABLE learners ADD COLUMN hashed_password VARCHAR"))
                except Exception as e:
                    print(f"Migration error learners.hashed_password: {e}")
            if "email" not in cols:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("ALTER TABLE learners ADD COLUMN email VARCHAR"))
                except Exception as e:
                    print(f"Migration error learners.email: {e}")
                    
        # 2. Learning activities table migration
        if "learning_activities" in tables:
            act_cols = [c["name"] for c in inspector.get_columns("learning_activities")]
            if "description" not in act_cols:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("ALTER TABLE learning_activities ADD COLUMN description TEXT"))
                except Exception as e:
                    print(f"Migration error learning_activities.description: {e}")
    except Exception as e:
        print(f"Migration inspect error: {e}")

# Run migrations on module load to guarantee schema readiness
run_migrations()

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
    if prefix.startswith("/api/"):
        alt_prefix = prefix[4:]
        app.include_router(router, prefix=alt_prefix, tags=tags)

@app.get("/health", tags=["health"])
@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}
