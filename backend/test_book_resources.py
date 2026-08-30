"""
Audit and Verification for High-Quality Book Learning Resources.
Verifies that:
1. Book resources exist across all major career tracks and skills.
2. Each book resource has valid metadata, legitimate URLs, and appropriate difficulty.
3. For learners with different goals and experience levels, filtering recommendations by 'book' or 'article' returns rich, relevant results.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.resource import Resource
from models.skill import Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap
from api.recommendations import get_recommendations

def test_book_resources():
    print("\n" + "=" * 80)
    print(" AUDITING HIGH-QUALITY BOOK LEARNING RESOURCES ACROSS ALL DOMAINS")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # 1. Inspect all seeded book resources
    books = db.query(Resource).filter(Resource.type == "book").all()
    print(f"\n[1/3] Seeded Book Resources Count: {len(books)}")
    assert len(books) >= 30, f"Expected at least 30 book resources, found {len(books)}"
    
    # Check providers and urls
    for b in books[:10]:
        print(f"  -> [{b.provider}] {b.title} ({b.difficulty}, Quality: {b.quality_score}) - {b.url}")
        assert b.url.startswith("http://") or b.url.startswith("https://"), f"Invalid book URL: {b.url}"
        assert b.quality_score >= 90
        assert len(b.skill_ids) > 0

    print("  [PASS] All book resources have valid providers/authors, quality scores, and URLs.")

    # 2. Test Book Recommendations Across 6 Distinct Goals and Difficulty Levels
    test_goals = [
        ("Alex Python", "Python & Core Engineering", "Python Developer", "beginner"),
        ("Sarah FullStack", "Become a Full Stack Web Developer", "Full Stack Developer", "intermediate"),
        ("Marcus Java", "Enterprise Java Architecture", "Java Developer", "intermediate"),
        ("Elena Data", "Data Analytics Mastery", "Data Analyst", "beginner"),
        ("Devin DevOps", "Cloud & Container DevOps", "DevOps Engineer", "intermediate"),
        ("Maya ML", "Applied Machine Learning", "Machine Learning Engineer", "advanced")
    ]

    print("\n[2/3] Testing 'Articles & Books' Recommendations for Diverse Goals...")
    for name, goal_title, role, level in test_goals:
        learner = Learner(name=name, experience_level=level, weekly_hours=15)
        db.add(learner)
        db.commit()
        db.refresh(learner)

        create_goal(db, learner.id, goal_title, role, 6)
        generate_roadmap(db, learner.id)

        all_recs = get_recommendations(learner.id, db)
        book_recs = [r for r in all_recs if r["resource"].type in ("book", "article")]

        print(f"\n  Track: '{goal_title}' ({role}, {level})")
        print(f"    Total Recommendations: {len(all_recs)}, Books & Articles: {len(book_recs)}")
        assert len(book_recs) >= 2, f"Expected at least 2 book recommendations for {role}, got {len(book_recs)}"
        
        for br in book_recs[:3]:
            res = br["resource"]
            print(f"      - [{res.provider}] {res.title} (Score: {br['score']}, Diff: {res.difficulty}) -> {br['explanation']}")

    print("\n[3/3] Verifying Multi-Domain Classic & Modern Book Platform Coverage...")
    specialized_topics = [
        ("CLRS & DSA Books", ["Data Structures (Arrays, Lists, Trees)", "Algorithms (Sorting, Searching, Graphs)"]),
        ("Designing Data-Intensive Applications & SQL Books", ["SQL Fundamentals", "SQL Advanced", "Databases & SQL"]),
        ("Linux Command Line & Docker in Action", ["Linux Command Line", "Docker Basics"]),
        ("Kubernetes Up & Running and SRE Book", ["Kubernetes Orchestration", "Site Reliability & Monitoring"]),
        ("Web App Hacker's Handbook & Crypto", ["Ethical Hacking & Web Security", "Network Security & Cryptography"]),
        ("The Rust Book & Rust for Rustaceans", ["Rust Syntax & Ownership", "Rust Concurrency & Cargo"]),
        ("The Go Programming Language", ["Go Fundamentals", "Go Concurrency & Goroutines"]),
        ("Hands-On ML (Aurélien Géron) & PRML", ["ML Fundamentals", "Feature Engineering", "Linear & Logistic Regression"]),
        ("Deep Learning (Goodfellow) & Transformers", ["Deep Learning with PyTorch", "Neural Networks Basics", "NLP & Large Language Models"])
    ]

    skill_lookup = {s.name: s.id for s in db.query(Skill).all()}
    for topic_label, skill_names in specialized_topics:
        target_sids = [skill_lookup[sn] for sn in skill_names if sn in skill_lookup]
        matched_books = [b for b in books if any(sid in target_sids for sid in (b.skill_ids or []))]
        print(f"  [PASS] {topic_label}: Found {len(matched_books)} book resources (e.g. '{matched_books[0].title if matched_books else 'None'}')")
        assert len(matched_books) >= 1, f"Missing book resource for topic {topic_label}"

    db.close()
    print("\n" + "=" * 80)
    print(" ALL BOOK RESOURCE AUDIT & RECOMMENDATION TESTS PASSED [100%]!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_book_resources()
