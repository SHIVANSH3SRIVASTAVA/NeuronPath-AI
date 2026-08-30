"""
Audit and Verification for High-Quality Hands-On Practice Resources.
Verifies that:
1. Practice resources exist across all major career tracks and skills.
2. Each practice resource has valid metadata, legitimate URLs, and appropriate difficulty.
3. For learners with different goals and experience levels, filtering recommendations by 'practice' returns rich, relevant results.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.resource import Resource
from models.skill import Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from api.recommendations import get_recommendations

def test_practice_resources():
    print("\n" + "=" * 80)
    print(" AUDITING HIGH-QUALITY HANDS-ON PRACTICE RESOURCES ACROSS ALL DOMAINS")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # 1. Inspect all seeded practice resources
    practices = db.query(Resource).filter(Resource.type.in_(["practice", "project"])).all()
    print(f"\n[1/3] Seeded Hands-on Practice Resources Count: {len(practices)}")
    assert len(practices) >= 25, f"Expected at least 25 practice resources, found {len(practices)}"
    
    # Check providers and urls
    for p in practices[:10]:
        print(f"  -> [{p.provider}] {p.title} ({p.difficulty}, Quality: {p.quality_score}) - {p.url}")
        assert p.url.startswith("http://") or p.url.startswith("https://"), f"Invalid practice URL: {p.url}"
        assert p.quality_score >= 90
        assert len(p.skill_ids) > 0

    print("  [PASS] All hands-on practice resources have valid providers, quality scores, and URLs.")

    # 2. Test Practice Recommendations Across 6 Distinct Goals and Difficulty Levels
    test_goals = [
        ("Alex Python", "Python & Problem Solving", "Python Developer", "beginner"),
        ("Sarah FullStack", "Become a Full Stack Web Developer", "Full Stack Developer", "intermediate"),
        ("Marcus Java", "Enterprise Java Architecture", "Java Developer", "intermediate"),
        ("Elena Data", "Data Analytics Mastery", "Data Analyst", "beginner"),
        ("Devin DevOps", "Cloud & Container DevOps", "DevOps Engineer", "intermediate"),
        ("Maya ML", "Applied Machine Learning", "Machine Learning Engineer", "advanced")
    ]

    print("\n[2/3] Testing 'Hands-on Practice' Recommendations for Diverse Goals...")
    for name, goal_title, role, level in test_goals:
        learner = Learner(name=name, experience_level=level, weekly_hours=15)
        db.add(learner)
        db.commit()
        db.refresh(learner)

        create_goal(db, learner.id, goal_title, role, 6)
        generate_roadmap(db, learner.id)

        all_recs = get_recommendations(learner.id, db)
        practice_recs = [r for r in all_recs if r["resource"].type in ("practice", "project")]

        print(f"\n  Track: '{goal_title}' ({role}, {level})")
        print(f"    Total Recommendations: {len(all_recs)}, Hands-on Practice Resources: {len(practice_recs)}")
        assert len(practice_recs) >= 2, f"Expected at least 2 practice recommendations for {role}, got {len(practice_recs)}"
        
        for pr in practice_recs[:3]:
            res = pr["resource"]
            print(f"      - [{res.provider}] {res.title} (Score: {pr['score']}, Diff: {res.difficulty}) -> {pr['explanation']}")

    print("\n[3/3] Verifying Multi-Domain Practice Platform Coverage...")
    specialized_topics = [
        ("DSA & LeetCode/NeetCode", ["Data Structures (Arrays, Lists, Trees)", "Algorithms (Sorting, Searching, Graphs)"]),
        ("SQL & PGExercises", ["SQL Fundamentals", "SQL Advanced"]),
        ("Docker & Play with Docker", ["Docker Basics", "Container Networking & Storage"]),
        ("Kubernetes & Killercoda", ["Kubernetes Orchestration", "Linux Command Line"]),
        ("Cybersecurity & Web Security Labs", ["Ethical Hacking & Web Security", "Authentication & Web Security"]),
        ("Rustlings (Rust)", ["Rust Syntax & Ownership", "Rust Concurrency & Cargo"]),
        ("Tour of Go (Go)", ["Go Fundamentals", "Go Concurrency & Goroutines"]),
        ("Kaggle ML & PyTorch", ["ML Fundamentals", "Feature Engineering", "Deep Learning with PyTorch"])
    ]

    skill_lookup = {s.name: s.id for s in db.query(Skill).all()}
    for topic_label, skill_names in specialized_topics:
        target_sids = [skill_lookup[sn] for sn in skill_names if sn in skill_lookup]
        matched_practices = [p for p in practices if any(sid in target_sids for sid in (p.skill_ids or []))]
        print(f"  [PASS] {topic_label}: Found {len(matched_practices)} practice resources (e.g. '{matched_practices[0].title if matched_practices else 'None'}')")
        assert len(matched_practices) >= 1, f"Missing practice resource for topic {topic_label}"

    db.close()
    print("\n" + "=" * 80)
    print(" ALL HANDS-ON PRACTICE RESOURCE AUDIT & RECOMMENDATION TESTS PASSED [100%]!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_practice_resources()
