from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.learner import Learner
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_learner(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Learner:
    """Retrieve and validate the currently authenticated learner from JWT."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        learner_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return learner

def get_optional_learner(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Optional[Learner]:
    """Retrieve the current learner if token is present, otherwise return None without raising 401."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        learner_id = int(payload["sub"])
        return db.query(Learner).filter(Learner.id == learner_id).first()
    except Exception:
        return None

def verify_learner_access(
    learner_id: int, 
    token: Optional[str] = Depends(oauth2_scheme)
):
    """Enforce ownership: Authenticated user cannot access another learner's records."""
    if not token:
        return None
        
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        try:
            token_sub = int(payload["sub"])
            if token_sub != learner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: You cannot access or modify another learner's learning profile."
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token credentials."
            )
    return None

