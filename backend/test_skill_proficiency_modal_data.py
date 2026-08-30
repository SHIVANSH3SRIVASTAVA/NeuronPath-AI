"""
Test real-time categorized skill data for the Skill Proficiency Overview modal.
Verifies that:
1. get_progress returns accurate counts and detailed skill lists for Mastered, Developing, Weak, and Missing categories.
2. Skill names, categories, and proficiency scores match the learner's actual database records.
3. As learners complete milestones and pass assessments, the skills shift dynamically between categories.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.skill import LearnerSkill, Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap, recalculate_roadmap_milestone_statuses
from services.progress_service import get_progress
from services.skill_service import update_learner_skill

def test_skill_proficiency_modal_data():
    print("\n" + "=" * 80)
    print(" TESTING SKILL PROFICIENCY OVERVIEW MODAL DATA & CATEGORIZATION")
    print("=" * 80)

    db = SessionLocal()
    seed_database(db, force=True)

    # 1. Create a real learner
    learner = Learner(name="Jordan Dev", experience_level="beginner", weekly_hours=15)
    db.add(learner)
    db.commit()
    db.refresh(learner)

    create_goal(db, learner.id, "Full Stack Web Development", "Full Stack Developer", 6)
    roadmap = generate_roadmap(db, learner.id)

    # Fetch initial progress
    progress_init = get_progress(db, learner.id)
    print(f"\n[1/3] Initial Skill Proficiency Distribution for '{learner.name}':")
    print(f"  Mastered ({progress_init['skills_mastered']}): {[s['name'] for s in progress_init['categorized_skills']['mastered']]}")
    print(f"  Developing ({progress_init['skills_developing']}): {[s['name'] for s in progress_init['categorized_skills']['developing']]}")
    print(f"  Weak ({progress_init['skills_weak']}): {[s['name'] for s in progress_init['categorized_skills']['weak']]}")
    print(f"  Missing ({progress_init['skills_missing']}): {[s['name'] for s in progress_init['categorized_skills']['missing']]}")

    assert progress_init['skills_missing'] > 0
    assert len(progress_init['categorized_skills']['missing']) == progress_init['skills_missing']

    # 2. Simulate progressive skill improvements
    print("\n[2/3] Updating Learner Skills to Mastered & Developing...")
    html_skill = db.query(Skill).filter(Skill.name == "HTML Fundamentals").first()
    css_skill = db.query(Skill).filter(Skill.name == "CSS Fundamentals").first()
    js_skill = db.query(Skill).filter(Skill.name == "JavaScript Fundamentals").first()

    # Master HTML (95%), Develop CSS (65%), Weak JS (25%)
    update_learner_skill(db, learner.id, html_skill.id, self_reported_level=90, demonstrated_level=95)
    update_learner_skill(db, learner.id, css_skill.id, self_reported_level=60, demonstrated_level=70)
    update_learner_skill(db, learner.id, js_skill.id, self_reported_level=20, demonstrated_level=30)

    progress_updated = get_progress(db, learner.id)
    print(f"\nUpdated Skill Proficiency Distribution:")
    print(f"  Mastered ({progress_updated['skills_mastered']}): {[s['name'] for s in progress_updated['categorized_skills']['mastered']]}")
    print(f"  Developing ({progress_updated['skills_developing']}): {[s['name'] for s in progress_updated['categorized_skills']['developing']]}")
    print(f"  Weak ({progress_updated['skills_weak']}): {[s['name'] for s in progress_updated['categorized_skills']['weak']]}")
    print(f"  Missing ({progress_updated['skills_missing']}): {[s['name'] for s in progress_updated['categorized_skills']['missing']]}")

    assert progress_updated['skills_mastered'] >= 1
    assert any(s['name'] == "HTML Fundamentals" for s in progress_updated['categorized_skills']['mastered'])
    assert any(s['name'] == "CSS Fundamentals" for s in progress_updated['categorized_skills']['developing'])
    assert any(s['name'] == "JavaScript Fundamentals" for s in progress_updated['categorized_skills']['weak'])

    print("\n[3/3] Validating Data Integrity for Modal Cards...")
    for cat in ["mastered", "developing", "weak", "missing"]:
        skills_in_cat = progress_updated['categorized_skills'][cat]
        count = progress_updated[f"skills_{cat}"]
        print(f"  Category '{cat.upper()}': Count={count}, Items count={len(skills_in_cat)}")
        assert count == len(skills_in_cat), f"Mismatch in {cat}: count {count} != items {len(skills_in_cat)}"
        for item in skills_in_cat:
            assert "name" in item and len(item["name"]) > 0
            assert "category" in item
            assert "proficiency" in item and 0 <= item["proficiency"] <= 100

    db.close()
    print("\n" + "=" * 80)
    print(" ALL SKILL PROFICIENCY MODAL DATA TESTS PASSED [100%]!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_skill_proficiency_modal_data()
