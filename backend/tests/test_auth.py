import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models.learner import Learner
from core.security import create_access_token

client = TestClient(app)

def test_register_and_login_flow():
    # 1. Register new user
    email = "test_user_flow@neuronpath.dev"
    reg_payload = {
        "name": "Alex Flow Test",
        "email": email,
        "password": "Password123!"
    }
    
    # Cleanup previous test if needed
    db = SessionLocal()
    existing = db.query(Learner).filter(Learner.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["learner"]["email"] == email
    user_id = data["learner"]["id"]
    token = data["access_token"]

    # 2. Duplicate registration with exact email should fail with 409 Conflict
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["detail"]

    # 3. Duplicate registration with uppercase email variation should also fail with 409
    dup_res_upper = client.post("/api/auth/register", json={
        "name": "Alex Duplicate",
        "email": email.upper(),
        "password": "DifferentPassword456!"
    })
    assert dup_res_upper.status_code == 409
    assert "already exists" in dup_res_upper.json()["detail"]

    # Verify no duplicate user record was created in the DB
    db = SessionLocal()
    records = db.query(Learner).filter(Learner.email == email).all()
    assert len(records) == 1
    db.close()

    # 4. Login with correct password
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["learner"]["id"] == user_id

    # 4. Login with incorrect password
    bad_login = client.post("/api/auth/login", json={
        "email": email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 5. /api/auth/me with valid token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["id"] == user_id

    # 6. /api/auth/me without token
    unauth_me = client.get("/api/auth/me")
    assert unauth_me.status_code == 401

def test_learner_ownership_protection():
    # Create two distinct learners
    token_user1 = create_access_token(data={"sub": "1001", "email": "user1@test.com"})
    token_user2 = create_access_token(data={"sub": "1002", "email": "user2@test.com"})

    # User 1 attempting to access User 2's learner profile should return 403 Forbidden
    res = client.get("/api/learners/1002", headers={"Authorization": f"Bearer {token_user1}"})
    assert res.status_code == 403
    assert "Access forbidden" in res.json()["detail"]


