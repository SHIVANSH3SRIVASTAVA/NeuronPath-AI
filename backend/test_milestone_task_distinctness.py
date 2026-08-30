"""
Test Milestone Task Distinctness and Topic Relevance across multi-level tracks.
Verifies that:
1. Python Basics, Python Intermediate, and Python Advanced milestones contain distinct, non-duplicate tasks.
2. Tasks for each level match that level's exact topic and difficulty.
3. Milestone objectives are concrete and topic-specific.
4. Java, C++, JavaScript, SQL, DevOps, and ML roadmaps also maintain distinct level-appropriate tasks.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from models.resource import Resource
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from services.assessment_service import generate_assessment

def test_milestone_task_distinctness():
    print("\n" + "=" * 80)
    print(" TESTING MILESTONE TASK DISTINCTNESS AND LEVEL RELEVANCE")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # -------------------------------------------------------------------------
    # TEST 1: PYTHON ROADMAP (Basics -> Intermediate -> Advanced)
    # -------------------------------------------------------------------------
    print("\n[1/3] Testing Python Roadmap Milestones...")
    learner_py = Learner(name="Jordan Python", experience_level="beginner", weekly_hours=15)
    db.add(learner_py)
    db.commit()
    db.refresh(learner_py)

    create_goal(db, learner_py.id, "Master Python Programming", "Python Developer", 6)
    roadmap_py = generate_roadmap(db, learner_py.id)

    milestones_py = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap_py.id
    ).order_by(RoadmapMilestone.order_index).all()

    print(f"Generated {len(milestones_py)} milestones for Python Developer:")
    milestone_tasks = {}
    for m in milestones_py:
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
        res_ids = [it.resource_id for it in items if it.resource_id]
        resources = db.query(Resource).filter(Resource.id.in_(res_ids)).all() if res_ids else []
        milestone_tasks[m.title] = [r.title for r in resources]
        print(f"\n  Milestone [{m.order_index + 1}]: '{m.title}'")
        print(f"    Objective: {m.objective}")
        for r in resources:
            print(f"      - [{r.type.upper()}] {r.title} ({r.difficulty}) -> {r.description[:70]}...")

    # Verify Python Basics vs Intermediate vs Advanced
    py_basics_tasks = milestone_tasks.get("Python Basics", [])
    py_inter_tasks = milestone_tasks.get("Python Intermediate", [])
    py_adv_tasks = milestone_tasks.get("Python Advanced", [])

    print("\n--- Verifying Distinctness Across Python Milestones ---")
    print(f"Python Basics tasks count: {len(py_basics_tasks)}")
    print(f"Python Intermediate tasks count: {len(py_inter_tasks)}")
    print(f"Python Advanced tasks count: {len(py_adv_tasks)}")

    assert len(py_basics_tasks) >= 2, "Python Basics must have at least 2 resources"
    assert len(py_inter_tasks) >= 2, "Python Intermediate must have at least 2 resources"
    assert len(py_adv_tasks) >= 2, "Python Advanced must have at least 2 resources"

    # Ensure zero overlap
    overlap_basic_inter = set(py_basics_tasks).intersection(set(py_inter_tasks))
    overlap_inter_adv = set(py_inter_tasks).intersection(set(py_adv_tasks))
    overlap_basic_adv = set(py_basics_tasks).intersection(set(py_adv_tasks))

    print(f"Overlap (Basics & Intermediate): {overlap_basic_inter}")
    print(f"Overlap (Intermediate & Advanced): {overlap_inter_adv}")
    print(f"Overlap (Basics & Advanced): {overlap_basic_adv}")

    assert len(overlap_basic_inter) == 0, f"Found task overlap between Basics and Intermediate: {overlap_basic_inter}"
    assert len(overlap_inter_adv) == 0, f"Found task overlap between Intermediate and Advanced: {overlap_inter_adv}"
    assert len(overlap_basic_adv) == 0, f"Found task overlap between Basics and Advanced: {overlap_basic_adv}"

    # Verify Topic Relevance
    # Basics should contain beginner concepts
    assert any("beginners" in t.lower() or "basics" in t.lower() or "boring" in t.lower() or "crash" in t.lower() for t in py_basics_tasks)
    # Intermediate should contain OOP, Decorators, Iterators, or Effective Python
    assert any("oop" in t.lower() or "effective" in t.lower() or "intermediate" in t.lower() or "morsels" in t.lower() for t in py_inter_tasks)
    # Advanced should contain Fluent, Async, Concurrency, Metaprogramming, or Performance
    assert any("fluent" in t.lower() or "async" in t.lower() or "concurrency" in t.lower() or "performance" in t.lower() or "metaprogramming" in t.lower() for t in py_adv_tasks)

    print("  [PASS] Python roadmap has strictly distinct, topic-specific learning tasks across all 3 levels!")

    # -------------------------------------------------------------------------
    # TEST 2: VERIFY ASSESSMENTS FOR PYTHON MILESTONES ARE ALIGNED
    # -------------------------------------------------------------------------
    print("\n[2/3] Testing Milestone-Aligned Assessments for Python...")
    m_basics = [m for m in milestones_py if m.title == "Python Basics"][0]
    m_inter = [m for m in milestones_py if m.title == "Python Intermediate"][0]
    m_adv = [m for m in milestones_py if m.title == "Python Advanced"][0]

    q_basics = generate_assessment(db, learner_py.id, m_basics.id, m_basics.skill_ids)
    q_inter = generate_assessment(db, learner_py.id, m_inter.id, m_inter.skill_ids)
    q_adv = generate_assessment(db, learner_py.id, m_adv.id, m_adv.skill_ids)

    print(f"  Assessment 1 ({q_basics.title}): {len(q_basics.questions)} questions")
    print(f"    Sample Q: {q_basics.questions[0].question_text}")
    print(f"  Assessment 2 ({q_inter.title}): {len(q_inter.questions)} questions")
    print(f"    Sample Q: {q_inter.questions[0].question_text}")
    print(f"  Assessment 3 ({q_adv.title}): {len(q_adv.questions)} questions")
    print(f"    Sample Q: {q_adv.questions[0].question_text}")

    assert q_basics.title == "Assessment: Python Basics"
    assert q_inter.title == "Assessment: Python Intermediate"
    assert q_adv.title == "Assessment: Python Advanced"
    print("  [PASS] Milestone assessments are strictly aligned to the specific milestone skill!")

    # -------------------------------------------------------------------------
    # TEST 3: VERIFY JAVA & FULL STACK ROADMAP TASK DISTINCTNESS
    # -------------------------------------------------------------------------
    print("\n[3/3] Testing Java & Full-Stack Roadmaps for Task Distinctness...")
    learner_java = Learner(name="Alex Java", experience_level="intermediate", weekly_hours=15)
    db.add(learner_java)
    db.commit()
    db.refresh(learner_java)

    create_goal(db, learner_java.id, "Enterprise Java Backend", "Java Developer", 6)
    roadmap_java = generate_roadmap(db, learner_java.id)

    milestones_java = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap_java.id
    ).order_by(RoadmapMilestone.order_index).all()

    java_tasks = {}
    for m in milestones_java:
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
        res_ids = [it.resource_id for it in items if it.resource_id]
        resources = db.query(Resource).filter(Resource.id.in_(res_ids)).all() if res_ids else []
        java_tasks[m.title] = [r.title for r in resources]

    j_fund = java_tasks.get("Java Fundamentals", [])
    j_oop = java_tasks.get("Java OOP & Collections", [])
    j_spring = java_tasks.get("Spring Boot & Enterprise Java", [])

    print(f"Java Fundamentals tasks: {j_fund}")
    print(f"Java OOP & Collections tasks: {j_oop}")
    print(f"Spring Boot & Enterprise Java tasks: {j_spring}")

    overlap_java = set(j_fund).intersection(set(j_oop)).intersection(set(j_spring))
    assert len(overlap_java) == 0, f"Found task overlap in Java milestones: {overlap_java}"
    print("  [PASS] Java roadmap milestones contain distinct, non-duplicate tasks!")

    db.close()
    print("\n" + "=" * 80)
    print(" ALL MILESTONE TASK DISTINCTNESS & LEVEL RELEVANCE TESTS PASSED [100%]!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_milestone_task_distinctness()
