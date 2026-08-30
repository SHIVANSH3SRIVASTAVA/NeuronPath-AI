import sys
import os
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from database import SessionLocal, engine, Base
from seed import seed_database
from models.learner import Learner
from models.roadmap import Roadmap, RoadmapMilestone
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from main import run_migrations, app
from fastapi.testclient import TestClient

run_migrations()
db = SessionLocal()
seed_database(db)
db.close()

client = TestClient(app)

def test_assessment_flow_end_to_end():
    db = SessionLocal()
    print("\n=======================================================")
    print(" 1. CREATE LEARNER WITH ACTIVE GOAL & ROADMAP")
    print("=======================================================")
    
    learner = Learner(name="Morgan Quiz Tester", experience_level="beginner", weekly_hours=15)
    db.add(learner)
    db.commit()
    db.refresh(learner)
    
    goal = create_goal(db, learner.id, "Machine Learning Engineer", "Machine Learning Engineer", timeline_months=6)
    roadmap = generate_roadmap(db, learner.id)
    assert roadmap is not None
    
    print("\n=======================================================")
    print(" 2. AUTO-GENERATE ASSESSMENT FOR CURRENT LEARNER")
    print("=======================================================")
    
    # Request without milestone_id/skill_ids payload (simulating clicking Assessments tab)
    res_gen = client.post(f"/api/assessments/generate?learner_id={learner.id}", json={})
    assert res_gen.status_code == 200, f"Generate assessment failed: {res_gen.text}"
    assessment = res_gen.json()
    
    print(f"Generated Assessment ID: {assessment.get('id')}")
    print(f"Assessment Title: {assessment.get('title')}")
    questions = assessment.get("questions", [])
    print(f"Total Questions Generated: {len(questions)}")
    assert len(questions) > 0, "Expected at least 1 question generated"
    
    for i, q in enumerate(questions):
        print(f"  Q{i+1}: {q.get('question_text')}")
        options = q.get("options", [])
        print(f"       Options ({len(options)}): {options}")
        assert len(options) >= 2, f"Expected at least 2 options for Q{i+1}"
        
    print("\n=======================================================")
    print(" 3. SUBMIT ANSWERS TO THE ASSESSMENT")
    print("=======================================================")
    
    # Provide answer 0 for each question
    answers = {str(q["id"]): 0 for q in questions}
    res_sub = client.post(
        f"/api/assessments/{assessment['id']}/submit?learner_id={learner.id}",
        json={"answers": answers}
    )
    assert res_sub.status_code == 200, f"Submit assessment failed: {res_sub.text}"
    result = res_sub.json()
    
    print(f"Submission Score: {result.get('score')}%")
    print(f"Correct Answers: {result.get('correct_answers')}/{result.get('total_questions')}")
    print(f"Skill Breakdown: {result.get('skill_breakdown')}")
    print(f"Explanations Count: {len(result.get('explanations', []))}")
    print(f"Adaptations Count: {len(result.get('adaptations', []))}")
    
    assert "score" in result
    assert result.get("total_questions") == len(questions)
    assert len(result.get("explanations", [])) == len(questions)
    
    print("\n=======================================================")
    print(" 4. FETCH ASSESSMENT BY ID")
    print("=======================================================")
    
    res_fetch = client.get(f"/api/assessments/{assessment['id']}")
    assert res_fetch.status_code == 200
    fetched_assessment = res_fetch.json()
    assert fetched_assessment.get("id") == assessment["id"]
    assert len(fetched_assessment.get("questions", [])) == len(questions)
    
    print("\n=======================================================")
    print(" ASSESSMENT FLOW END-TO-END TESTS PASSED! [100%]")
    print("=======================================================\n")
    db.close()

if __name__ == "__main__":
    test_assessment_flow_end_to_end()
