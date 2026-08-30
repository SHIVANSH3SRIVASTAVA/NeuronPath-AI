import urllib.request
import json

def test_catalog():
    print("=================================================================")
    print(" TESTING 12 DIVERSE GOALS ACROSS EXPANDED NEURONPATH CATALOG")
    print("=================================================================")

    BASE = 'http://127.0.0.1:8000'

    def req(path, method='GET', data=None):
        url = f"{BASE}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    test_goals = [
        {"goal": "Enterprise Java & Spring Boot", "category": "Programming (Java)", "expected_skill": "Java Fundamentals"},
        {"goal": "Rust & Systems Programming", "category": "Programming (Rust)", "expected_skill": "Rust Syntax & Ownership"},
        {"goal": "Deep Learning with PyTorch", "category": "Data & AI", "expected_skill": "Deep Learning with PyTorch"},
        {"goal": "AI Engineering & LLM Applications", "category": "Data & AI", "expected_skill": "Transformers & LLM Engineering"},
        {"goal": "Kubernetes Cluster Administrator", "category": "Cloud & DevOps", "expected_skill": "Kubernetes Orchestration"},
        {"goal": "AWS Cloud Solutions Architect", "category": "Cloud & DevOps", "expected_skill": "AWS Cloud Foundations"},
        {"goal": "Modern Frontend Development with React", "category": "Software & Web", "expected_skill": "React & State Management"},
        {"goal": "iOS App Development with SwiftUI", "category": "Mobile Development", "expected_skill": "iOS Development with SwiftUI"},
        {"goal": "Data Structures & Algorithms Interview Prep", "category": "Computer Science", "expected_skill": "Data Structures (Arrays, Lists, Trees)"},
        {"goal": "Cybersecurity & Ethical Hacking", "category": "Cybersecurity", "expected_skill": "Network Security & Cryptography"},
        {"goal": "Blockchain & Smart Contracts Development", "category": "Blockchain", "expected_skill": "Solidity & Smart Contracts"},
        {"goal": "UI/UX Design with Figma", "category": "Design & Product", "expected_skill": "UI/UX Design & Wireframing"},
    ]

    all_milestone_1_titles = []

    for i, tg in enumerate(test_goals):
        print(f"\n[{i+1}/12] Testing Goal: '{tg['goal']}' ({tg['category']})")
        
        # 1. Create learner
        l = req('/api/learners', 'POST', {'name': f"Learner {i+1}"})
        lid = l['id']
        
        # 2. Onboard goal
        onb = req(f'/api/learners/{lid}/onboard', 'POST', {'goal_text': tg['goal']})
        print(f" -> Target Role: \"{onb['target_role']}\" | Goal: \"{onb['goal']}\"")
        
        # 3. Generate roadmap
        roadmap = req(f'/api/learners/{lid}/roadmap', 'POST')
        milestones = roadmap['milestones']
        assert len(milestones) >= 2, f"Roadmap for {tg['goal']} should have at least 2 milestones"
        
        m1 = milestones[0]
        print(f" -> Step 1 Milestone: \"{m1['title']}\" ({m1['estimated_hours']}h)")
        print(f"    Objective: \"{m1['objective']}\"")
        all_milestone_1_titles.append(m1['title'])
        
        # 4. Check Skill Gaps
        gaps = req(f'/api/learners/{lid}/skills/gaps')
        gap_names = [g['skill_name'] for g in gaps]
        print(f" -> Top Skills/Gaps: {gap_names[:3]}")
        
        # 5. Check Next Action
        next_act = req(f'/api/learners/{lid}/roadmap/next-action')
        print(f" -> Next Action: {next_act['action']} - {next_act['message']}")
        
        # Verification
        assert any(tg['expected_skill'].lower() in gn.lower() for gn in gap_names), \
            f"Expected skill '{tg['expected_skill']}' missing in gaps for goal '{tg['goal']}'"

    print("\n=================================================================")
    print(" VERIFYING DIVERSITY ACROSS ALL 12 TESTED GOALS")
    print("=================================================================")
    for i, t in enumerate(all_milestone_1_titles):
        print(f"Goal {i+1:02d} ({test_goals[i]['category']}) -> Step 1: {t}")
        
    unique_count = len(set(all_milestone_1_titles))
    print(f"\nUnique Step 1 Milestone Titles: {unique_count} / 12")
    assert unique_count >= 10, "At least 10 unique Step 1 titles expected across 12 diverse goals!"

    print("\n=================================================================")
    print(" ALL 12 DIVERSE GOALS VERIFIED WITH 100% SUCCESS!")
    print("=================================================================")

if __name__ == '__main__':
    test_catalog()
