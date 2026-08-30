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
from models.skill import Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from main import run_migrations, app
from fastapi.testclient import TestClient

# Ensure database tables and seed
run_migrations()
db = SessionLocal()
seed_database(db, force=True)
db.close()

client = TestClient(app)

def test_full_stack_milestone_decomposition_and_aligned_assessments():
    db = SessionLocal()
    print("\n================================================================================")
    print(" 1. FULL STACK WEB DEVELOPMENT: ROADMAP DECOMPOSITION & ASSESSMENT ALIGNMENT")
    print("================================================================================")
    
    learner = Learner(name="Alex FullStack Tester", experience_level="beginner", weekly_hours=20)
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    goal = create_goal(db, learner.id, "Full Stack Web Development", "Full Stack Developer", timeline_months=6)
    roadmap = generate_roadmap(db, learner.id)
    assert roadmap is not None, "Failed to generate roadmap"
    
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    
    print(f"Generated {len(milestones)} granular milestones for Full Stack Web Development:")
    for idx, m in enumerate(milestones):
        print(f"  Step {idx+1:02d}: {m.title} (Status: {m.status}, Estimated: {m.estimated_hours}h)")
        
    # Requirement: Multi-milestone granular decomposition (e.g. >= 12 milestones for Full Stack)
    assert len(milestones) >= 12, f"Expected at least 12 granular milestones, got {len(milestones)}"
    assert milestones[0].status == "available"
    assert milestones[1].status == "locked"
    assert milestones[2].status == "locked"
    
    # --------------------------------------------------------------------------
    # TEST MILESTONE 1 (HTML): Must NOT contain React / Backend / SQL questions
    # --------------------------------------------------------------------------
    print("\n--- Testing Milestone 1 (HTML Fundamentals) Assessment Alignment ---")
    res_m1 = client.post(f"/api/assessments/generate?learner_id={learner.id}", json={"milestone_id": milestones[0].id})
    assert res_m1.status_code == 200
    m1_data = res_m1.json()
    m1_questions = m1_data.get("questions", [])
    print(f"Assessment Title: {m1_data.get('title')}")
    print(f"Total Questions: {len(m1_questions)}")
    assert len(m1_questions) >= 10, "Expected at least 10 questions"
    
    # Check that M1 questions test HTML and do NOT leak future topics (React, Backend, SQL, Docker)
    m1_texts = " ".join([q["question_text"].lower() + " " + " ".join(q["options"]).lower() for q in m1_questions])
    print(f"Sample M1 Q1: {m1_questions[0]['question_text']}")
    print(f"Sample M1 Q2: {m1_questions[1]['question_text']}")
    
    assert "html" in m1_texts or "article" in m1_texts or "element" in m1_texts, "M1 should focus on HTML concepts"
    # Strict Future Exclusion
    assert "react" not in m1_texts, "M1 assessment must NOT contain future React questions"
    assert "docker" not in m1_texts, "M1 assessment must NOT contain future Docker questions"
    assert "jwt" not in m1_texts, "M1 assessment must NOT contain future Auth/JWT questions"
    
    # --------------------------------------------------------------------------
    # COMPLETE MILESTONE 1 TASKS & VERIFY MILESTONE 2 UNLOCKS
    # --------------------------------------------------------------------------
    print("\n--- Testing Task Completion & Sequential Unlocking ---")
    m1_items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == milestones[0].id).all()
    for it in m1_items:
        res_comp = client.post(f"/api/learners/{learner.id}/roadmap/items/{it.id}/complete")
        assert res_comp.status_code == 200
        
    db.expire_all()
    m1_refreshed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == milestones[0].id).first()
    m2_refreshed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == milestones[1].id).first()
    m3_refreshed = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == milestones[2].id).first()
    
    print(f"Milestone 1 Status after tasks complete: {m1_refreshed.status}")
    print(f"Milestone 2 Status after Milestone 1 complete: {m2_refreshed.status}")
    print(f"Milestone 3 Status (still dependent): {m3_refreshed.status}")
    
    assert m1_refreshed.status == "completed", "Milestone 1 should be completed"
    assert m2_refreshed.status == "available", "Milestone 2 should be unlocked (available)"
    assert m3_refreshed.status == "locked", "Milestone 3 should remain locked"
    
    # --------------------------------------------------------------------------
    # TEST MILESTONE 4 (JavaScript Fundamentals): Prerequisite reinforcement without future React/Backend leakage
    # --------------------------------------------------------------------------
    js_milestone = next((m for m in milestones if "JavaScript" in m.title), None)
    if js_milestone:
        print(f"\n--- Testing Milestone ({js_milestone.title}) Assessment Alignment ---")
        res_js = client.post(f"/api/assessments/generate?learner_id={learner.id}", json={"milestone_id": js_milestone.id})
        assert res_js.status_code == 200
        js_data = res_js.json()
        js_questions = js_data.get("questions", [])
        print(f"Assessment Title: {js_data.get('title')}")
        print(f"Total Questions: {len(js_questions)}")
        assert len(js_questions) >= 10
        
        js_texts = " ".join([q["question_text"].lower() + " " + " ".join(q["options"]).lower() for q in js_questions])
        print(f"Sample JS Q1: {js_questions[0]['question_text']}")
        print(f"Sample JS Q2: {js_questions[1]['question_text']}")
        
        assert "javascript" in js_texts or "closure" in js_texts or "equality" in js_texts or "function" in js_texts
        assert "docker" not in js_texts, "JS assessment must NOT contain future Docker questions"
        assert "jwt" not in js_texts, "JS assessment must NOT contain future JWT questions"
        
    print("\n Full Stack Web Development tests passed with 100% precision!")
    db.close()

def test_other_diverse_goals_roadmap_decomposition():
    db = SessionLocal()
    print("\n================================================================================")
    print(" 2. VERIFYING ROADMAP DECOMPOSITION & ALIGNED ASSESSMENTS FOR 4 OTHER GOALS")
    print("================================================================================")
    
    test_cases = [
        ("Data Analytics Mastery", "Data Analyst", 8, "SQL Fundamentals", ["pytorch", "neural"]),
        ("Cloud & Container DevOps", "DevOps Engineer", 8, "Linux Command Line", ["kubernetes orchestration", "terraform"]),
        ("Enterprise Java Architecture", "Java Developer", 8, "Java Fundamentals", ["docker", "microservices"]),
        ("Applied Machine Learning", "Machine Learning Engineer", 10, "Python Basics", ["pytorch", "mlops"]),
    ]
    
    for title, role, min_milestones, first_skill, future_forbidden in test_cases:
        print(f"\nTesting Goal: '{title}' ({role})")
        print("-" * 75)
        
        learner = Learner(name=f"Tester {role}", experience_level="intermediate", weekly_hours=15)
        db.add(learner)
        db.commit()
        db.refresh(learner)
        
        goal = create_goal(db, learner.id, title, role, timeline_months=6)
        roadmap = generate_roadmap(db, learner.id)
        assert roadmap is not None
        
        milestones = db.query(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id
        ).order_by(RoadmapMilestone.order_index).all()
        
        print(f"Generated {len(milestones)} milestones (Target >= {min_milestones}):")
        for i, m in enumerate(milestones[:4]):
            print(f"  [{i+1}] {m.title}")
        print(f"  ... and {len(milestones) - 4} more milestones")
        
        assert len(milestones) >= min_milestones, f"Expected >= {min_milestones} milestones for {role}, got {len(milestones)}"
        
        # Test Milestone 1 Assessment Alignment
        res_m1 = client.post(f"/api/assessments/generate?learner_id={learner.id}", json={"milestone_id": milestones[0].id})
        assert res_m1.status_code == 200
        m1_data = res_m1.json()
        questions = m1_data.get("questions", [])
        assert len(questions) >= 10
        
        q_texts = " ".join([q["question_text"].lower() for q in questions])
        print(f"Milestone 1 Assessment: '{m1_data.get('title')}' with {len(questions)} questions")
        print(f"  Q1 [{questions[0]['difficulty'].upper()}]: {questions[0]['question_text']}")
        print(f"  Q10 [{questions[9]['difficulty'].upper()}]: {questions[9]['question_text']}")
        
        # Verify 0% future topic leakage
        for forbidden in future_forbidden:
            assert forbidden not in q_texts, f"Milestone 1 leaked future topic '{forbidden}'!"
            
        print(f" Goal '{role}' verified: multi-milestone decomposition + aligned assessment.")
        
    print("\n================================================================================")
    print(" ALL 5 GOALS PASSED ROADMAP DECOMPOSITION & ASSESSMENT ALIGNMENT! [100%]")
    print("================================================================================\n")
    db.close()

if __name__ == "__main__":
    test_full_stack_milestone_decomposition_and_aligned_assessments()
    test_other_diverse_goals_roadmap_decomposition()
