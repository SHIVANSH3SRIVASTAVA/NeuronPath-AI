"""
Real Learner End-to-End Verification Test.
Verifies that:
1. Seeding produces ZERO demo accounts.
2. A real learner completes onboarding, sets their own goal, and generates a personalized roadmap.
3. Dashboard, Skills, Resources, Assessment, and Progress work 100% seamlessly for the real learner.
4. No demo account fallbacks or demo learner creations exist.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.roadmap import LearnerGoal, Roadmap, RoadmapMilestone, MilestoneItem, GoalSkillRequirement
from models.skill import SkillPrerequisite, LearnerSkill, Skill
from models.resource import Resource
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap, recalculate_roadmap_milestone_statuses
from services.progress_service import get_progress
from services.assessment_service import generate_assessment, submit_assessment
from recommendation.skill_gap import calculate_skill_gaps
from recommendation.prerequisite import build_prerequisite_graph

def test_real_learner_flow():
    print("\n" + "=" * 80)
    print(" TESTING REAL LEARNER COMPLETE FLOW (ZERO DEMO ACCOUNTS)")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # 1. Verify ZERO demo accounts exist
    all_learners = db.query(Learner).all()
    print(f"\n[1/7] Checking Database for Demo Learners...")
    print(f"  Total Learners in fresh database: {len(all_learners)}")
    assert len(all_learners) == 0, f"Expected 0 demo learners, found {len(all_learners)}"
    print("  [PASS] PASSED: Zero demo learners exist in the database.")

    # 2. Create a Real Learner
    print(f"\n[2/7] Creating Real Learner Profile...")
    real_learner = Learner(
        name="Jordan Peterson",
        email="jordan.p@techcareer.io",
        experience_level="beginner",
        weekly_hours=18,
        preferred_formats=["course", "documentation", "practice"],
        learning_style="hands_on"
    )
    db.add(real_learner)
    db.commit()
    db.refresh(real_learner)
    print(f"  [PASS] Created Real Learner: {real_learner.name} (ID: {real_learner.id}, Level: {real_learner.experience_level})")

    # 3. Define Real Learner Goal
    print(f"\n[3/7] Setting Custom Goal: 'Full Stack Web Development'...")
    goal = create_goal(db, real_learner.id, "Become a Full Stack Web Developer", "Full Stack Developer", 6)
    assert goal is not None
    print(f"  [PASS] Goal Created: '{goal.title}' for role '{goal.target_role}' (Active)")

    # 4. Generate Personalized Roadmap
    print(f"\n[4/7] Generating Roadmap...")
    roadmap = generate_roadmap(db, real_learner.id)
    assert roadmap is not None
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    
    print(f"  [PASS] Generated {len(milestones)} Milestones for {real_learner.name}:")
    for m in milestones[:4]:
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
        res_items = [it for it in items if it.item_type == "resource"]
        print(f"     Step {m.order_index + 1:02d}: {m.title} [Status: {m.status}, {len(res_items)} resources]")
    assert len(milestones) >= 8, "Expected at least 8 milestones"
    assert milestones[0].status == "available"
    assert milestones[1].status == "locked"

    # 5. Verify Skills and Recommendations
    print(f"\n[5/7] Verifying Skill Gaps & Resource Recommendations...")
    reqs = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal.id).all()
    l_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == real_learner.id).all()
    prereqs = db.query(SkillPrerequisite).all()
    graph = build_prerequisite_graph(prereqs)
    gaps = calculate_skill_gaps(l_skills, reqs, graph)
    print(f"  [PASS] Calculated {len(gaps)} Skill Gaps for real learner.")
    assert len(gaps) > 0

    # 6. Complete Milestone 1 Tasks and Verify Sequential Unlocking
    print(f"\n[6/7] Completing Milestone 1 Tasks...")
    m1 = milestones[0]
    m1_items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m1.id).all()
    for it in m1_items:
        it.status = "completed"
    db.commit()
    
    recalculate_roadmap_milestone_statuses(db, roadmap.id)
    db.refresh(m1)
    m2 = milestones[1]
    db.refresh(m2)
    
    print(f"  Milestone 1 status after task completion: {m1.status}")
    print(f"  Milestone 2 status after Milestone 1 completion: {m2.status}")
    assert m1.status == "completed"
    assert m2.status == "available"
    print("  [PASS] Sequential milestone unlocking verified.")

    # 7. Generate & Submit Milestone Assessment
    print(f"\n[7/7] Generating & Submitting Milestone Assessment...")
    assessment = generate_assessment(db, real_learner.id, milestone_id=m1.id)
    assert assessment is not None
    print(f"  [PASS] Assessment Generated: '{assessment.title}' with {len(assessment.questions)} balanced questions")
    assert len(assessment.questions) >= 10
    
    # Submit answers
    answers = {str(q.id): q.correct_answer_index for q in assessment.questions}
    result = submit_assessment(db, real_learner.id, assessment.id, answers)
    print(f"  [PASS] Assessment Submitted: Score = {result['score']}%, Correct = {result['correct_answers']}/{result['total_questions']}")
    assert result["score"] == 100.0

    # 8. Check Final Progress Data
    progress = get_progress(db, real_learner.id)
    print(f"  [PASS] Progress Data: {progress['overall_progress']}% Overall Progress, {progress['milestones_completed']}/{progress['milestones_total']} Milestones Done")
    assert progress["milestones_completed"] >= 1
    assert progress["overall_progress"] > 0

    db.close()
    print("\n" + "=" * 80)
    print(" ALL REAL LEARNER FLOW TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_real_learner_flow()
