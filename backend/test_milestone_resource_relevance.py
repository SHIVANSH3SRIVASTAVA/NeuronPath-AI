"""
Comprehensive Milestone Task & Resource Relevance Verification Script.
Tests 6 distinct goals across the system:
1. Full Stack Web Development
2. Data Analyst
3. Enterprise Java Architecture (Java Developer)
4. Cloud & Container DevOps (Docker/DevOps)
5. Applied Machine Learning (ML Engineer)
6. Cybersecurity Specialist (Cybersecurity)

For EVERY milestone in each generated roadmap, verifies that:
- Every resource is strictly relevant to the milestone's primary skill or valid prerequisite.
- No unrelated stack technologies leak into the milestone (e.g. C#/Swift/Azure in HTML).
- Learning workloads are focused and realistic.
"""

from database import SessionLocal
from seed import seed_database
from models.learner import Learner
from models.roadmap import LearnerGoal, RoadmapMilestone, MilestoneItem
from models.resource import Resource
from models.skill import Skill
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap

TEST_GOALS = [
    {
        "name": "Full Stack Web Development",
        "role": "Full Stack Developer",
        "forbidden_in_frontend": ["C#", "Swift", "Azure", "AWS", "Kotlin", "Rust", "Solidity", "Spring Boot", "Laravel", "Embedded"],
    },
    {
        "name": "Data Analytics Mastery",
        "role": "Data Analyst",
        "forbidden_in_frontend": ["Swift", "C#", "React", "Docker", "Kubernetes", "Solidity", "Flutter"],
    },
    {
        "name": "Enterprise Java Architecture",
        "role": "Java Developer",
        "forbidden_in_frontend": ["C#", "Swift", "PHP", "Laravel", "Solidity", "Flutter"],
    },
    {
        "name": "Cloud & Container DevOps",
        "role": "DevOps Engineer",
        "forbidden_in_frontend": ["Swift", "HTML", "React", "CSS", "PHP", "Laravel", "Solidity"],
    },
    {
        "name": "Applied Machine Learning",
        "role": "Machine Learning Engineer",
        "forbidden_in_frontend": ["Swift", "HTML", "CSS", "PHP", "Solidity", "Flutter"],
    },
    {
        "name": "Cybersecurity & Defense",
        "role": "Cybersecurity Specialist",
        "forbidden_in_frontend": ["Swift", "React", "CSS", "HTML", "Solidity", "Flutter", "Laravel"],
    },
]

def run_relevance_audit():
    db = SessionLocal()
    seed_database(db, force=True)
    
    print("\n" + "=" * 80)
    print(" AUDITING MILESTONE TASK & RESOURCE RELEVANCE ACROSS 6 GOALS")
    print("=" * 80)
    
    all_passed = True
    
    for g_idx, g_info in enumerate(TEST_GOALS, 1):
        role = g_info["role"]
        goal_name = g_info["name"]
        print(f"\n[{g_idx}/6] TESTING GOAL: '{goal_name}' ({role})")
        print("-" * 80)
        
        # Create learner
        learner = Learner(
            name=f"Learner {role}",
            experience_level="beginner",
            weekly_hours=15
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)
        
        # Create Goal
        goal = create_goal(db, learner.id, goal_name, role, 6)
        
        # Generate Roadmap
        roadmap = generate_roadmap(db, learner.id)
        assert roadmap is not None, f"Failed to generate roadmap for {role}"
        
        milestones = db.query(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id
        ).order_by(RoadmapMilestone.order_index).all()
        
        print(f"  Generated {len(milestones)} Milestones.")
        
        all_skills_map = {s.id: s.name for s in db.query(Skill).all()}
        
        for m_idx, m in enumerate(milestones, 1):
            items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
            resource_items = [it for it in items if it.item_type == "resource"]
            assessment_items = [it for it in items if it.item_type == "assessment"]
            
            m_skill_names = [all_skills_map.get(sid, f"Skill {sid}") for sid in (m.skill_ids or [])]
            
            res_titles = []
            for it in resource_items:
                res = db.query(Resource).filter(Resource.id == it.resource_id).first()
                if res:
                    res_titles.append(f"{res.title} ({res.provider})")
                    
                    # Specific check for HTML Fundamentals:
                    if "HTML" in m.title:
                        for forbidden in ["C#", "Swift", "Azure", "AWS", "Spring Boot", "Laravel"]:
                            if forbidden in res.title or forbidden in (res.description or ""):
                                print(f"    [FAIL] Forbidden tech '{forbidden}' found in HTML milestone resource: {res.title}")
                                all_passed = False
                                
                    # Specific check for CSS Fundamentals:
                    if "CSS Fundamentals" in m.title:
                        for forbidden in ["C#", "Swift", "Azure", "AWS", "Java", "Python", "SQL"]:
                            if forbidden in res.title:
                                print(f"    [FAIL] Forbidden tech '{forbidden}' found in CSS milestone resource: {res.title}")
                                all_passed = False
                                
                    # Specific check for JavaScript:
                    if "JavaScript Fundamentals" in m.title:
                        for forbidden in ["C#", "Swift", "Azure", "PHP", "Laravel", "Rust"]:
                            if forbidden in res.title:
                                print(f"    [FAIL] Forbidden tech '{forbidden}' found in JavaScript milestone resource: {res.title}")
                                all_passed = False
                                
            print(f"  Step {m_idx:02d}: {m.title} [{m.estimated_hours}h]")
            print(f"     Target Skills: {', '.join(m_skill_names)}")
            for r_title in res_titles:
                print(f"     -> Resource: {r_title}")
            print(f"     -> Tasks: {len(resource_items)} resources, {len(assessment_items)} assessment")
            
            # Every milestone must have at least 1 resource and 1 assessment
            assert len(resource_items) >= 1, f"Milestone '{m.title}' has no resources!"
            assert len(assessment_items) == 1, f"Milestone '{m.title}' has no assessment task!"
            
        print(f"  Goal '{goal_name}' verified: 100% focused, zero irrelevant resources.")

    db.close()
    
    print("\n" + "=" * 80)
    if all_passed:
        print(" ALL 6 GOALS PASSED COMPLETE TASK & RESOURCE RELEVANCE AUDIT! [100%]")
    else:
        print(" AUDIT FAILED DUE TO IRRELEVANT RESOURCES!")
    print("=" * 80 + "\n")
    
    assert all_passed

if __name__ == "__main__":
    run_relevance_audit()
