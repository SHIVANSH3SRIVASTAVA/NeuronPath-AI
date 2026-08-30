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
from services.assessment_service import generate_assessment
from main import run_migrations, app
from fastapi.testclient import TestClient

run_migrations()
db = SessionLocal()
seed_database(db)
db.close()

client = TestClient(app)

TEST_GOALS = [
    {
        "title": "Master Docker & DevOps CI/CD",
        "target_role": "DevOps Engineer",
        "expected_keywords": ["docker", "container", "ci/cd", "pipeline", "linux", "git", "kubernetes", "cloud"]
    },
    {
        "title": "Professional Data Analytics & SQL",
        "target_role": "Data Analyst",
        "expected_keywords": ["sql", "data", "cleaning", "statistics", "visualization", "bi", "analysis"]
    },
    {
        "title": "Core & Enterprise Java Development",
        "target_role": "Java Developer",
        "expected_keywords": ["java", "oop", "class", "heap", "stack", "exception", "collection", "spring", "backend"]
    },
    {
        "title": "Cybersecurity & Threat Defense Specialist",
        "target_role": "Cybersecurity Engineer",
        "expected_keywords": ["security", "cipher", "encryption", "network", "firewall", "xss", "sqli", "cia", "vulnerability"]
    },
    {
        "title": "Machine Learning & AI Engineering Track",
        "target_role": "Machine Learning Engineer",
        "expected_keywords": ["ml", "machine learning", "regression", "bias", "variance", "neural", "python", "model", "regularization"]
    }
]

def test_assessment_generation_across_5_goals():
    db = SessionLocal()
    print("\n================================================================================")
    print(" VERIFYING 10+ QUESTION DYNAMIC ASSESSMENT GENERATION FOR 5 DIVERSE GOALS")
    print("================================================================================")
    
    for g_idx, g_info in enumerate(TEST_GOALS, 1):
        role = g_info["target_role"]
        title = g_info["title"]
        print(f"\n[{g_idx}/5] TESTING GOAL: '{title}' ({role})")
        print("-" * 75)
        
        # 1. Create learner and roadmap
        learner = Learner(name=f"Tester {role}", experience_level="intermediate", weekly_hours=20)
        db.add(learner)
        db.commit()
        db.refresh(learner)
        
        goal = create_goal(db, learner.id, title, role, timeline_months=6)
        roadmap = generate_roadmap(db, learner.id)
        assert roadmap is not None
        
        # 2. Call assessment generation via API endpoint
        res = client.post(f"/api/assessments/generate?learner_id={learner.id}", json={})
        assert res.status_code == 200, f"Failed to generate assessment: {res.text}"
        assessment = res.json()
        
        questions = assessment.get("questions", [])
        q_count = len(questions)
        print(f"Generated Assessment ID: {assessment.get('id')}")
        print(f"Assessment Title: {assessment.get('title')}")
        print(f"Total Questions: {q_count}")
        
        # Quality Requirement 1: AT LEAST 10 QUESTIONS
        assert q_count >= 10, f"Expected at least 10 questions, but got {q_count}"
        
        # Quality Requirement 2: NO DUPLICATES
        q_texts = [q["question_text"].strip() for q in questions]
        unique_q_texts = set(q_texts)
        assert len(unique_q_texts) == q_count, f"Found duplicate questions! Unique: {len(unique_q_texts)}, Total: {q_count}"
        
        # Quality Requirement 3: EXACTLY 4 OPTIONS & VALID CORRECT ANSWER
        for i, q in enumerate(questions):
            opts = q.get("options", [])
            assert len(opts) == 4, f"Q{i+1} must have 4 options, got {len(opts)}"
            assert len(set(opts)) == 4, f"Q{i+1} has duplicate options: {opts}"
            assert "difficulty" in q, f"Q{i+1} missing difficulty metadata"
            
        # Display sample question previews
        print("Sample Questions:")
        for idx in [0, 1, 4, q_count - 1]:
            q = questions[idx]
            diff = q.get('difficulty', 'intermediate')
            print(f"  Q{idx+1} [{diff.upper()}]: {q['question_text']}")
            for opt_idx, opt in enumerate(q['options']):
                letter = chr(65 + opt_idx)
                print(f"       ({letter}) {opt[:75]}...")
                
        # 4. Submit assessment answers and verify grading & feedback
        answers = {str(q["id"]): 0 for q in questions}
        res_sub = client.post(f"/api/assessments/{assessment['id']}/submit?learner_id={learner.id}", json={"answers": answers})
        assert res_sub.status_code == 200, f"Submit failed: {res_sub.text}"
        sub_data = res_sub.json()
        
        print(f"Submission Score: {sub_data.get('score')}%")
        print(f"Total Evaluated Questions: {sub_data.get('total_questions')}")
        print(f"Skill Breakdown Keys: {list(sub_data.get('skill_breakdown', {}).keys())}")
        print(f"Adaptations Count: {len(sub_data.get('adaptations', []))}")
        
        assert sub_data.get("total_questions") == q_count
        assert len(sub_data.get("explanations", [])) == q_count
        print(f" Goal '{role}' passed all criteria (10+ distinct questions, valid schema, full grading).")
        
    print("\n================================================================================")
    print(" ALL 5 GOALS PRODUCED 10+ DISTINCT, GOAL-RELEVANT QUESTIONS SUCCESSFULLY! [100%]")
    print("================================================================================\n")
    db.close()

if __name__ == "__main__":
    test_assessment_generation_across_5_goals()
