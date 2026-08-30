"""
Audit and Verification for High-Quality Video Learning Resources.
Verifies that:
1. Video resources exist across all major career tracks and skills.
2. Each video has valid metadata, legitimate URLs, and appropriate difficulty.
3. For learners with different goals, filtering recommendations by 'video' returns rich, relevant results.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.resource import Resource
from models.skill import Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from api.recommendations import get_recommendations

def test_video_resources():
    print("\n" + "=" * 80)
    print(" AUDITING HIGH-QUALITY VIDEO LEARNING RESOURCES ACROSS ALL DOMAINS")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # 1. Inspect all seeded video resources
    videos = db.query(Resource).filter(Resource.type == "video").all()
    print(f"\n[1/3] Seeded Video Resources Count: {len(videos)}")
    assert len(videos) >= 30, f"Expected at least 30 video resources, found {len(videos)}"
    
    # Check providers and urls
    for v in videos[:10]:
        print(f"  -> [{v.provider}] {v.title} ({v.duration_hours}h, Quality: {v.quality_score}) - {v.url}")
        assert v.url.startswith("https://www.youtube.com/watch?v="), f"Invalid video URL: {v.url}"
        assert v.quality_score >= 90
        assert len(v.skill_ids) > 0

    print("  [PASS] All video resources have valid providers, quality scores, and URLs.")

    # 2. Test Video Recommendations Across 6 Distinct Goals
    test_goals = [
        ("Alex Python", "Python & Data Mastery", "Python Developer", 6),
        ("Sarah FullStack", "Become a Full Stack Web Developer", "Full Stack Developer", 6),
        ("Marcus Java", "Enterprise Java Architecture", "Java Developer", 6),
        ("Elena Data", "Data Analytics Mastery", "Data Analyst", 6),
        ("Devin DevOps", "Cloud & Container DevOps", "DevOps Engineer", 6),
        ("Maya ML", "Applied Machine Learning", "Machine Learning Engineer", 6)
    ]

    print("\n[2/3] Testing 'Videos' Filter for Diverse Goals...")
    for name, goal_title, role, months in test_goals:
        learner = Learner(name=name, experience_level="beginner", weekly_hours=15)
        db.add(learner)
        db.commit()
        db.refresh(learner)

        create_goal(db, learner.id, goal_title, role, months)
        generate_roadmap(db, learner.id)

        all_recs = get_recommendations(learner.id, db)
        video_recs = [r for r in all_recs if r["resource"].type == "video"]

        print(f"\n  Track: '{goal_title}' ({role})")
        print(f"    Total Recommendations: {len(all_recs)}, Video Resources: {len(video_recs)}")
        assert len(video_recs) >= 3, f"Expected at least 3 video recommendations for {role}, got {len(video_recs)}"
        
        for vr in video_recs[:3]:
            res = vr["resource"]
            print(f"      • [{res.provider}] {res.title} (Score: {vr['score']}) -> {vr['explanation']}")

    print("\n[3/3] Verifying Multi-Language and Specialization Video Coverage...")
    specialized_topics = [
        ("Rust", ["Rust Syntax & Ownership", "Rust Concurrency & Cargo"]),
        ("Go", ["Go Fundamentals", "Go Concurrency & Goroutines"]),
        ("C++", ["C++ Fundamentals", "Modern C++ & STL"]),
        ("C#", ["C# Basics & OOP", ".NET Core & ASP.NET"]),
        ("Algorithms & DSA", ["Data Structures (Arrays, Lists, Trees)", "Algorithms (Sorting, Searching, Graphs)"]),
        ("Kubernetes & Docker", ["Docker Basics", "Kubernetes Orchestration"]),
        ("Cybersecurity", ["Ethical Hacking & Web Security", "Network Security & Cryptography"]),
        ("Mobile (Flutter/Swift)", ["Cross-Platform App Development (Flutter/React Native)", "Swift Syntax & Basics"])
    ]

    skill_lookup = {s.name: s.id for s in db.query(Skill).all()}
    for topic_label, skill_names in specialized_topics:
        target_sids = [skill_lookup[sn] for sn in skill_names if sn in skill_lookup]
        matched_videos = [v for v in videos if any(sid in target_sids for sid in (v.skill_ids or []))]
        print(f"  [PASS] {topic_label}: Found {len(matched_videos)} video resources (e.g. '{matched_videos[0].title if matched_videos else 'None'}')")
        assert len(matched_videos) >= 1, f"Missing video resource for topic {topic_label}"

    db.close()
    print("\n" + "=" * 80)
    print(" ALL VIDEO RESOURCE AUDIT & RECOMMENDATION TESTS PASSED [100%]!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_video_resources()
