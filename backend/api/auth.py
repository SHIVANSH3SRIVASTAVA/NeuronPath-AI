import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db
from models.learner import Learner
from core.security import hash_password, verify_password, create_access_token
from core.deps import get_current_learner

router = APIRouter()

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1)

def learner_to_dict(learner: Learner) -> dict:
    return {
        "id": learner.id,
        "name": learner.name,
        "email": learner.email,
        "experience_level": learner.experience_level,
        "weekly_hours": learner.weekly_hours,
        "learning_style": learner.learning_style,
        "preferred_formats": learner.preferred_formats or [],
        "created_at": learner.created_at.isoformat() if learner.created_at else None
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new learner account with email and password."""
    clean_email = payload.email.strip().lower()
    
    if not EMAIL_REGEX.match(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format. Please enter a valid email."
        )
    
    existing = db.query(Learner).filter(Learner.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )
        
    hashed = hash_password(payload.password)
    learner = Learner(
        name=payload.name.strip(),
        email=clean_email,
        hashed_password=hashed,
        experience_level="beginner",
        weekly_hours=10.0,
        learning_style="visual_and_interactive",
        preferred_formats=["course", "practice", "documentation"]
    )
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    token = create_access_token(data={"sub": str(learner.id), "email": learner.email})
    
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "learner": learner_to_dict(learner)
    }

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate learner via email and password, returning a JWT access token."""
    clean_email = payload.email.strip().lower()
    learner = db.query(Learner).filter(Learner.email == clean_email).first()
    
    if not learner or not learner.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(payload.password, learner.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = create_access_token(data={"sub": str(learner.id), "email": learner.email})
    
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "learner": learner_to_dict(learner)
    }

@router.get("/me")
def get_current_profile(current_learner: Learner = Depends(get_current_learner)):
    """Return the profile of the currently authenticated learner."""
    return learner_to_dict(current_learner)

