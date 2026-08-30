import sys
import os
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from database import SessionLocal, engine, Base
from seed import seed_database
from models.learner import Learner
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from main import run_migrations, app
from fastapi.testclient import TestClient

# Ensure tables and migrations exist
run_migrations()
db = SessionLocal()
seed_database(db)
db.close()

client = TestClient(app)

def test_dashboard_full_completion_synchronization():
    db = SessionLocal()
    print("\n=======================================================")
    print(" 1. CREATE LEARNER WITH ACTIVE GOAL & ROADMAP")
    print("=======================================================")
    
    learner = Learner(name="Jordan Completed Learner", experience_level="intermediate", weekly_hours=20)
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    goal = create_goal(db, learner.id, "Cloud & DevOps Architect", "DevOps Engineer", timeline_months=6)
    roadmap = generate_roadmap(db, learner.id)
    assert roadmap is not None, "Failed to generate roadmap"
    
    # 2. Query all milestones
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    print(f"Generated {len(milestones)} milestones for roadmap")
    
    print("\n=======================================================")
    print(" 2. COMPLETE EVERY TASK ACROSS ALL MILESTONES")
    print("=======================================================")
    
    for m_idx, m in enumerate(milestones):
        # If milestone is available, start it
        client.post(f"/api/learners/{learner.id}/roadmap/milestones/{m.id}/start")
        
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
        for it in items:
            res_comp = client.post(f"/api/learners/{learner.id}/roadmap/items/{it.id}/complete")
            assert res_comp.status_code == 200, f"Task completion failed: {res_comp.text}"
            
        # Verify milestone is now completed
        db.expire_all()
        m_check = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == m.id).first()
        print(f"Milestone {m_idx + 1}/{len(milestones)} '{m.title}' Status: {m_check.status}")
        assert m_check.status == "completed", f"Milestone {m.id} should be completed, got {m_check.status}"

    print("\n=======================================================")
    print(" 3. VERIFY DASHBOARD ENDPOINTS AFTER 100% COMPLETION")
    print("=======================================================")
    
    # Check Roadmap Endpoint (must not 404)
    res_roadmap = client.get(f"/api/learners/{learner.id}/roadmap")
    assert res_roadmap.status_code == 200, f"Roadmap fetch failed: {res_roadmap.text}"
    roadmap_data = res_roadmap.json()
    print(f"Roadmap Status: {roadmap_data.get('status')}")
    assert roadmap_data.get("status") == "completed", f"Roadmap status should be 'completed', got {roadmap_data.get('status')}"
    assert len(roadmap_data.get("milestones", [])) == len(milestones)
    
    # Check Progress Endpoint
    res_progress = client.get(f"/api/learners/{learner.id}/progress")
    assert res_progress.status_code == 200, f"Progress fetch failed: {res_progress.text}"
    prog_data = res_progress.json()
    print(f"Overall Progress: {prog_data.get('overall_progress')}%")
    print(f"Milestones Completed: {prog_data.get('milestones_completed')}/{prog_data.get('milestones_total')}")
    print(f"Skills Mastered: {prog_data.get('skills_mastered')}")
    print(f"Recent Activities count: {len(prog_data.get('recent_activity', []))}")
    
    assert prog_data.get("overall_progress") == 100.0, f"Expected 100% progress, got {prog_data.get('overall_progress')}"
    assert prog_data.get("milestones_completed") == len(milestones)
    assert prog_data.get("skills_mastered") > 0, "Expected at least 1 mastered skill"
    assert len(prog_data.get("recent_activity", [])) > 0, "Expected recent activities"
    
    # Check Next Action Endpoint (must not show 'create_goal')
    res_action = client.get(f"/api/learners/{learner.id}/next-action")
    assert res_action.status_code == 200, f"Next action fetch failed: {res_action.text}"
    action_data = res_action.json()
    print(f"Next Action Type: {action_data.get('action')}")
    print(f"Next Action Title: {action_data.get('title', '').encode('ascii', 'ignore').decode()}")
    print(f"Next Action Description: {action_data.get('description', '').encode('ascii', 'ignore').decode()}")
    
    assert action_data.get("action") == "all_completed", f"Expected 'all_completed', got {action_data.get('action')}"
    assert "set your goal" not in (action_data.get("title") or "").lower()
    
    print("\n=======================================================")
    print(" 4. VERIFY PERSISTENCE AFTER SIMULATED REFRESH")
    print("=======================================================")
    
    # Simulate fresh request
    res_prog_refresh = client.get(f"/api/learners/{learner.id}/progress")
    assert res_prog_refresh.json().get("overall_progress") == 100.0
    
    print("\n=======================================================")
    print(" DASHBOARD FULL COMPLETION SYNC TESTS PASSED! [100%]")
    print("=======================================================\n")
    db.close()

if __name__ == "__main__":
    test_dashboard_full_completion_synchronization()
