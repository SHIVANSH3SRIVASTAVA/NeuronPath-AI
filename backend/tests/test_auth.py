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

def test_delete_account_and_isolation():
    # Cleanup any old test accounts
    db = SessionLocal()
    for em in ["delete_me@test.com", "keep_me@test.com"]:
        old = db.query(Learner).filter(Learner.email == em).first()
        if old:
            db.delete(old)
    db.commit()
    db.close()

    # 1. Register User A and User B
    res_a = client.post("/api/auth/register", json={
        "name": "User To Delete",
        "email": "delete_me@test.com",
        "password": "Password123!"
    })
    assert res_a.status_code == 201
    user_a_id = res_a.json()["learner"]["id"]
    token_a = res_a.json()["access_token"]

    res_b = client.post("/api/auth/register", json={
        "name": "User To Keep",
        "email": "keep_me@test.com",
        "password": "Password123!"
    })
    assert res_b.status_code == 201
    user_b_id = res_b.json()["learner"]["id"]
    token_b = res_b.json()["access_token"]

    # 2. User B tries to delete User A -> 403 Forbidden
    forbidden_del = client.delete(f"/api/learners/{user_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert forbidden_del.status_code == 403

    # 3. User A deletes own account -> 200 OK
    del_res = client.delete(f"/api/learners/{user_a_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 4. Verify User A no longer exists in database
    db = SessionLocal()
    assert db.query(Learner).filter(Learner.id == user_a_id).first() is None
    # 5. Verify User B is completely untouched and intact
    assert db.query(Learner).filter(Learner.id == user_b_id).first() is not None
    db.close()

    # 6. Trying to login with User A fails (401)
    login_deleted = client.post("/api/auth/login", json={
        "email": "delete_me@test.com",
        "password": "Password123!"
    })
    assert login_deleted.status_code == 401



