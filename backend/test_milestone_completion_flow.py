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
from services.roadmap_service import generate_roadmap, recalculate_roadmap_milestone_statuses
from fastapi.testclient import TestClient
from main import app

# Ensure tables are created and base seed exists
Base.metadata.create_all(bind=engine)
db = SessionLocal()
seed_database(db)
db.close()

client = TestClient(app)

def test_milestone_completion_and_locking():
    db = SessionLocal()
    print("\n=======================================================")
    print(" 1. SETTING UP TEST LEARNER & ROADMAP")
    print("=======================================================")
    
    # 1. Create a fresh learner
    learner = Learner(name="Test Roadmap Flow Learner", experience_level="beginner", weekly_hours=15)
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    # 2. Create goal for Machine Learning Engineer
    create_goal(db, learner.id, "Machine Learning Engineer", "Machine Learning Engineer", timeline_months=6)
    
    # 3. Generate Roadmap
    roadmap = generate_roadmap(db, learner.id)
    assert roadmap is not None, "Roadmap generation failed"
    
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    
    assert len(milestones) >= 2, f"Expected at least 2 milestones, got {len(milestones)}"
    step1 = milestones[0]
    step2 = milestones[1]
    
    print(f"Step 1 Title: '{step1.title}' - Initial Status: {step1.status}")
    print(f"Step 2 Title: '{step2.title}' - Initial Status: {step2.status}")
    
    assert step1.status in ["available", "in_progress"], f"Step 1 should be available/in_progress, got {step1.status}"
    assert step2.status == "locked", f"Step 2 should initially be locked, got {step2.status}"
    
    step1_items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == step1.id).all()
    step2_items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == step2.id).all()
    
    print(f"Step 1 Task Count: {len(step1_items)}")
    print(f"Step 2 Task Count: {len(step2_items)}")
    assert len(step1_items) > 0, "Step 1 has no tasks"
    assert len(step2_items) > 0, "Step 2 has no tasks"
    
    print("\n=======================================================")
    print(" 2. TESTING REJECTION OF TASK COMPLETION ON LOCKED STEP 2")
    print("=======================================================")
    
    locked_item = step2_items[0]
    res = client.post(f"/api/learners/{learner.id}/roadmap/items/{locked_item.id}/complete")
    print(f"Attempt complete locked task -> Status: {res.status_code}, Response: {res.text}")
    assert res.status_code == 400, f"Expected 400 Bad Request for locked item, got {res.status_code}"
    assert "locked" in res.text.lower(), "Expected error message mentioning locked milestone"
    
    print("\n=======================================================")
    print(" 3. TESTING REJECTION OF STARTING LOCKED STEP 2")
    print("=======================================================")
    
    res_start = client.post(f"/api/learners/{learner.id}/roadmap/milestones/{step2.id}/start")
    print(f"Attempt start locked milestone -> Status: {res_start.status_code}, Response: {res_start.text}")
    assert res_start.status_code == 400, f"Expected 400 Bad Request for starting locked milestone, got {res_start.status_code}"
    
    print("\n=======================================================")
    print(" 4. COMPLETING STEP 1 TASKS SEQUENTIALLY")
    print("=======================================================")
    
    for i, it in enumerate(step1_items):
        print(f"Completing Step 1 Task {i+1}/{len(step1_items)} (ID: {it.id}, Type: {it.item_type})...")
        res_comp = client.post(f"/api/learners/{learner.id}/roadmap/items/{it.id}/complete")
        assert res_comp.status_code == 200, f"Failed to complete task {it.id}: {res_comp.text}"
        data = res_comp.json()
        print(f"  -> Task status: {data.get('item_status')}, Milestone status: {data.get('milestone_status')}")
    
    # Refresh database records
    db.expire_all()
    step1_refreshed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == step1.id).first()
    step2_refreshed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == step2.id).first()
    
    print("\n=======================================================")
    print(" 5. VERIFYING STEP 1 AUTO-COMPLETION & STEP 2 UNLOCKING")
    print("=======================================================")
    
    print(f"Step 1 Status after all tasks complete: {step1_refreshed.status}")
    print(f"Step 2 Status after Step 1 complete: {step2_refreshed.status}")
    
    assert step1_refreshed.status == "completed", f"Step 1 should automatically be 'completed', got {step1_refreshed.status}"
    assert step2_refreshed.status == "available", f"Step 2 should automatically unlock to 'available', got {step2_refreshed.status}"
    
    print("\n=======================================================")
    print(" 6. VERIFYING STEP 2 CAN NOW BE STARTED AND COMPLETED")
    print("=======================================================")
    
    # Start Step 2
    res_start2 = client.post(f"/api/learners/{learner.id}/roadmap/milestones/{step2.id}/start")
    assert res_start2.status_code == 200, f"Failed to start unlocked Step 2: {res_start2.text}"
    print(f"Start Step 2 Result: {res_start2.json()}")
    
    # Complete Step 2 Tasks
    for i, it in enumerate(step2_items):
        print(f"Completing Step 2 Task {i+1}/{len(step2_items)} (ID: {it.id}, Type: {it.item_type})...")
        res_comp2 = client.post(f"/api/learners/{learner.id}/roadmap/items/{it.id}/complete")
        assert res_comp2.status_code == 200, f"Failed to complete task {it.id}: {res_comp2.text}"
    
    db.expire_all()
    step2_completed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == step2.id).first()
    print(f"Step 2 Status after all tasks complete: {step2_completed.status}")
    assert step2_completed.status == "completed", f"Step 2 should be 'completed', got {step2_completed.status}"
    
    print("\n=======================================================")
    print(" 7. VERIFYING PROGRESS ENDPOINT REFLECTS MILESTONE ADVANCEMENT")
    print("=======================================================")
    
    res_prog = client.get(f"/api/learners/{learner.id}/progress")
    assert res_prog.status_code == 200
    prog_data = res_prog.json()
    print(f"Overall Progress: {prog_data.get('overall_progress')}%")
    print(f"Milestones Completed: {prog_data.get('milestones_completed')}/{prog_data.get('milestones_total')}")
    assert prog_data.get('milestones_completed') == 2, f"Expected 2 milestones completed, got {prog_data.get('milestones_completed')}"
    assert prog_data.get('overall_progress') > 0, "Progress percentage should be > 0"
    
    print("\n=======================================================")
    print(" ALL MILESTONE COMPLETION & LOCKING TESTS PASSED! [100%]")
    print("=======================================================\n")
    db.close()

if __name__ == "__main__":
    test_milestone_completion_and_locking()
