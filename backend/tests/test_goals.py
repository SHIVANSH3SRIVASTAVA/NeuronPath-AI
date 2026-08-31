import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models.learner import Learner
from models.roadmap import LearnerGoal, Roadmap

client = TestClient(app)

def test_goals_lifecycle_and_constraints():
    email = "goals_tester_lifecycle@neuronpath.dev"
    db = SessionLocal()
    existing = db.query(Learner).filter(Learner.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    # Register
    res_reg = client.post("/api/auth/register", json={
        "name": "Goals Lifecycle Tester",
        "email": email,
        "password": "GoalsPassword123!"
    })
    assert res_reg.status_code == 201
    token = res_reg.json()["access_token"]
    lid = res_reg.json()["learner"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Onboard initial Goal 1: Machine Learning Engineer
    res_onboard = client.post(f"/api/learners/{lid}/onboard", json={
        "goal_text": "I want to become a Machine Learning Engineer"
    }, headers=headers)
    assert res_onboard.status_code == 200
    goal1_id = res_onboard.json()["goal_id"]

    # Verify Goal 1 listed and active
    res_goals = client.get("/api/goals", headers=headers)
    assert res_goals.status_code == 200
    goals = res_goals.json()
    assert len(goals) == 1
    assert goals[0]["id"] == goal1_id
    assert goals[0]["status"] == "active"
    assert "Machine Learning" in goals[0]["target_role"] or "Machine Learning" in goals[0]["title"]

    # Verify Roadmap for Goal 1 exists
    res_rm1 = client.get(f"/api/learners/{lid}/roadmap", headers=headers)
    assert res_rm1.status_code == 200
    assert res_rm1.json()["goal_id"] == goal1_id

    # 2. Add Goal 2: Full Stack Developer
    res_g2 = client.post("/api/goals", json={
        "title": "Full Stack Developer Path",
        "target_role": "Full Stack Developer",
        "timeline_months": 6,
        "set_active": True
    }, headers=headers)
    assert res_g2.status_code == 201
    goal2 = res_g2.json()
    goal2_id = goal2["id"]
    assert goal2["status"] == "active"

    # Verify 2 goals exist, Goal 2 active, Goal 1 inactive
    res_goals2 = client.get("/api/goals", headers=headers)
    assert res_goals2.status_code == 200
    goals2 = res_goals2.json()
    assert len(goals2) == 2
    active_g2 = next(g for g in goals2 if g["status"] == "active")
    inactive_g2 = next(g for g in goals2 if g["status"] == "inactive")
    assert active_g2["id"] == goal2_id
    assert inactive_g2["id"] == goal1_id

    # Verify Roadmap now returns Goal 2
    res_rm2 = client.get(f"/api/learners/{lid}/roadmap", headers=headers)
    assert res_rm2.status_code == 200
    assert res_rm2.json()["goal_id"] == goal2_id

    # 3. Add Goal 3: Data Scientist
    res_g3 = client.post("/api/goals", json={
        "title": "Data Scientist Path",
        "target_role": "Data Scientist",
        "timeline_months": 8,
        "set_active": True
    }, headers=headers)
    assert res_g3.status_code == 201
    goal3_id = res_g3.json()["id"]

    # Verify 3 goals exist
    res_goals3 = client.get("/api/goals", headers=headers)
    assert len(res_goals3.json()) == 3

    # 4. Attempt adding Goal 4 -> MUST fail with 400 (max 3 goals)
    res_g4 = client.post("/api/goals", json={
        "title": "DevOps Engineer Path",
        "target_role": "DevOps Engineer",
        "timeline_months": 6
    }, headers=headers)
    assert res_g4.status_code == 400
    assert "Maximum of 3" in res_g4.json()["detail"]

    # 5. Switch active goal back to Goal 1
    res_act = client.put(f"/api/goals/{goal1_id}/activate", headers=headers)
    assert res_act.status_code == 200
    assert res_act.json()["id"] == goal1_id
    assert res_act.json()["status"] == "active"

    # Verify Goal 1 roadmap is loaded
    res_rm_switch = client.get(f"/api/learners/{lid}/roadmap", headers=headers)
    assert res_rm_switch.status_code == 200
    assert res_rm_switch.json()["goal_id"] == goal1_id

    # 6. Delete Goal 2
    res_del2 = client.delete(f"/api/goals/{goal2_id}", headers=headers)
    assert res_del2.status_code == 200
    del_data2 = res_del2.json()
    assert del_data2["deleted_goal_id"] == goal2_id
    assert len(del_data2["goals"]) == 2

    # 7. Delete Goal 1 (which is currently ACTIVE) -> Goal 3 should become active
    res_del1 = client.delete(f"/api/goals/{goal1_id}", headers=headers)
    assert res_del1.status_code == 200
    del_data1 = res_del1.json()
    assert del_data1["deleted_goal_id"] == goal1_id
    assert del_data1["active_goal"]["id"] == goal3_id
    assert len(del_data1["goals"]) == 1

    # Verify Roadmap now loads Goal 3
    res_rm3 = client.get(f"/api/learners/{lid}/roadmap", headers=headers)
    assert res_rm3.status_code == 200
    assert res_rm3.json()["goal_id"] == goal3_id

    # 8. Attempt deleting Goal 3 (only goal remaining) -> MUST fail with 400
    res_del3 = client.delete(f"/api/goals/{goal3_id}", headers=headers)
    assert res_del3.status_code == 400
    assert "only" in res_del3.json()["detail"].lower()

    # Clean up
    db = SessionLocal()
    l_clean = db.query(Learner).filter(Learner.id == lid).first()
    if l_clean:
        db.delete(l_clean)
        db.commit()
    db.close()
