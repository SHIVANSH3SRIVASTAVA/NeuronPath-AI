import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models.learner import Learner
from models.roadmap import LearnerGoal, Roadmap

client = TestClient(app)

def test_multi_goal_lifecycle():
    email = 'multi_goal_test@neuronpath.dev'
    db = SessionLocal()
    existing = db.query(Learner).filter(Learner.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    res_reg = client.post('/api/auth/register', json={
        'name': 'Multi Goal Tester',
        'email': email,
        'password': 'MultiPassword123!'
    })
    assert res_reg.status_code == 201
    token = res_reg.json()['access_token']
    lid = res_reg.json()['learner']['id']
    headers = {'Authorization': f'Bearer {token}'}

    # 1. Complete Onboarding with Goal 1: Machine Learning Engineer
    res_onboard = client.post(f'/api/learners/{lid}/onboard', json={
        'goal_text': 'I want to become a Machine Learning Engineer'
    }, headers=headers)
    assert res_onboard.status_code == 200
    goal1_id = res_onboard.json()['goal_id']

    # Verify Goal 1 is active and listed
    res_goals1 = client.get('/api/goals', headers=headers)
    assert res_goals1.status_code == 200
    goals1 = res_goals1.json()
    assert len(goals1) == 1
    assert goals1[0]['id'] == goal1_id
    assert goals1[0]['status'] == 'active'

    # Verify Roadmap for Goal 1 exists
    res_rm1 = client.get(f'/api/learners/{lid}/roadmap', headers=headers)
    assert res_rm1.status_code == 200
    assert res_rm1.json()['goal_id'] == goal1_id

    # 2. Add Goal 2: Full Stack Developer
    res_add = client.post('/api/goals', json={
        'title': 'Full Stack Developer Path',
        'target_role': 'Full Stack Developer',
        'timeline_months': 8,
        'set_active': True
    }, headers=headers)
    assert res_add.status_code == 201
    goal2_id = res_add.json()['id']

    # Verify both goals exist, Goal 2 is active, Goal 1 is inactive
    res_goals2 = client.get('/api/goals', headers=headers)
    assert res_goals2.status_code == 200
    goals2 = res_goals2.json()
    assert len(goals2) == 2
    active_g = next(g for g in goals2 if g['status'] == 'active')
    inactive_g = next(g for g in goals2 if g['status'] == 'inactive')
    assert active_g['id'] == goal2_id
    assert inactive_g['id'] == goal1_id

    # Verify Roadmap now loads Goal 2
    res_rm2 = client.get(f'/api/learners/{lid}/roadmap', headers=headers)
    assert res_rm2.status_code == 200
    assert res_rm2.json()['goal_id'] == goal2_id

    # 3. Switch back to Goal 1
    res_switch = client.put(f'/api/goals/{goal1_id}/activate', headers=headers)
    assert res_switch.status_code == 200
    assert res_switch.json()['status'] == 'active'

    # Verify Goal 1 roadmap loads again
    res_rm_switch = client.get(f'/api/learners/{lid}/roadmap', headers=headers)
    assert res_rm_switch.status_code == 200
    assert res_rm_switch.json()['goal_id'] == goal1_id

    # 4. Delete Goal 1 (Active Goal) -> verify Goal 2 becomes active automatically
    res_del1 = client.delete(f'/api/goals/{goal1_id}', headers=headers)
    assert res_del1.status_code == 200
    del_data = res_del1.json()
    assert del_data['deleted_goal_id'] == goal1_id
    assert del_data['active_goal'] is not None
    assert del_data['active_goal']['id'] == goal2_id
    assert len(del_data['remaining_goals']) == 1

    # Verify Goal 2 roadmap loads
    res_rm_after_del = client.get(f'/api/learners/{lid}/roadmap', headers=headers)
    assert res_rm_after_del.status_code == 200
    assert res_rm_after_del.json()['goal_id'] == goal2_id

    # 5. Delete Goal 2 (Last Goal)
    res_del2 = client.delete(f'/api/goals/{goal2_id}', headers=headers)
    assert res_del2.status_code == 200
    del2_data = res_del2.json()
    assert del2_data['deleted_goal_id'] == goal2_id
    assert del2_data['active_goal'] is None
    assert len(del2_data['remaining_goals']) == 0

    # Clean up
    db = SessionLocal()
    l_clean = db.query(Learner).filter(Learner.id == lid).first()
    if l_clean:
        db.delete(l_clean)
        db.commit()
    db.close()

def test_goal_content_isolation_and_switching():
    email = 'isolation_test@neuronpath.dev'
    db = SessionLocal()
    existing = db.query(Learner).filter(Learner.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    res_reg = client.post('/api/auth/register', json={
        'name': 'Isolation Tester',
        'email': email,
        'password': 'Password123!'
    })
    assert res_reg.status_code == 201
    token = res_reg.json()['access_token']
    lid = res_reg.json()['learner']['id']
    headers = {'Authorization': f'Bearer {token}'}

    # 1. Onboard with Goal 1: C Developer
    res_onb = client.post(f'/api/learners/{lid}/onboard', json={
        'goal_text': 'I want to master C Programming and embedded systems'
    }, headers=headers)
    assert res_onb.status_code == 200
    g_c_id = res_onb.json()['goal_id']

    # 2. Add Goal 2: Full Stack Developer
    res_add = client.post('/api/goals', json={
        'title': 'Full Stack Developer',
        'target_role': 'Full Stack Developer',
        'timeline_months': 6,
        'set_active': True
    }, headers=headers)
    assert res_add.status_code == 201
    g_fs_id = res_add.json()['id']

    # 3. Check that Full Stack Developer (Active) displays Full Stack content
    res_rm_fs = client.get(f'/api/learners/{lid}/roadmap?goal_id={g_fs_id}', headers=headers)
    assert res_rm_fs.status_code == 200
    assert res_rm_fs.json()['goal_id'] == g_fs_id

    res_prog_fs = client.get(f'/api/learners/{lid}/progress?goal_id={g_fs_id}', headers=headers)
    assert res_prog_fs.status_code == 200
    fs_skills = [s['name'] for s in res_prog_fs.json()['categorized_skills']['missing'] + res_prog_fs.json()['categorized_skills']['developing'] + res_prog_fs.json()['categorized_skills']['weak'] + res_prog_fs.json()['categorized_skills']['mastered']]
    # Verify web/full stack skills are present and not only C
    assert any('JavaScript' in s or 'HTML' in s or 'React' in s or 'CSS' in s or 'SQL' in s for s in fs_skills)

    # 4. Switch to C Developer and verify content switches to C
    client.put(f'/api/goals/{g_c_id}/activate', headers=headers)
    res_rm_c = client.get(f'/api/learners/{lid}/roadmap?goal_id={g_c_id}', headers=headers)
    assert res_rm_c.status_code == 200
    assert res_rm_c.json()['goal_id'] == g_c_id

    # Clean up
    db = SessionLocal()
    l_clean = db.query(Learner).filter(Learner.id == lid).first()
    if l_clean:
        db.delete(l_clean)
        db.commit()
    db.close()

