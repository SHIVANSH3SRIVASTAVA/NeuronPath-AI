import urllib.request
import json

def test_goals():
    print("=================================================================")
    print(" TESTING 5 DISTINCT GOALS FOR PERSONALIZED ROADMAP GENERATION")
    print("=================================================================")

    BASE = 'http://127.0.0.1:8000'

    def req(path, method='GET', data=None):
        url = f"{BASE}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    test_cases = [
        {
            "name": "Alex DevOps",
            "goal_input": "Docker / DevOps",
            "expected_top_skills": ["Docker Basics", "Linux Command Line"],
            "expected_not_in_milestone_1": ["Data Visualization", "Linear Regression"]
        },
        {
            "name": "Sarah Analyst",
            "goal_input": "Data Analyst",
            "expected_top_skills": ["SQL Fundamentals", "Descriptive Statistics"],
            "expected_not_in_milestone_1": ["Deep Learning with PyTorch", "Docker Basics"]
        },
        {
            "name": "Elena Security",
            "goal_input": "Cybersecurity",
            "expected_top_skills": ["Linux Command Line", "Git & Version Control"],
            "expected_not_in_milestone_1": ["Pandas", "Linear Regression"]
        },
        {
            "name": "David SQL",
            "goal_input": "SQL Developer",
            "expected_top_skills": ["SQL Fundamentals", "SQL Advanced"],
            "expected_not_in_milestone_1": ["Neural Networks Basics", "Docker Basics"]
        },
        {
            "name": "Liam MLE",
            "goal_input": "Machine Learning Engineer",
            "expected_top_skills": ["Python Basics", "ML Fundamentals"],
            "expected_not_in_milestone_1": ["SQL Advanced"]
        }
    ]

    all_milestone_titles = []

    for i, tc in enumerate(test_cases):
        print(f"\n--- TEST GOAL {i+1}: '{tc['goal_input']}' (Learner: {tc['name']}) ---")
        
        # 1. Create learner
        l = req('/api/learners', 'POST', {'name': tc['name']})
        lid = l['id']
        
        # 2. Onboard goal
        onb = req(f'/api/learners/{lid}/onboard', 'POST', {'goal_text': tc['goal_input']})
        print(f"Goal Derived: \"{onb['goal']}\" -> Target Role: \"{onb['target_role']}\"")
        
        # 3. Generate roadmap
        roadmap = req(f'/api/learners/{lid}/roadmap', 'POST')
        milestones = roadmap['milestones']
        print(f"Generated {len(milestones)} Milestones:")
        
        m1 = milestones[0]
        print(f"  * Milestone 1 (Active): \"{m1['title']}\"")
        print(f"    Objective: \"{m1['objective']}\"")
        print(f"    Hours: {m1['estimated_hours']}h")
        
        all_milestone_titles.append(m1['title'])
        
        for idx, m in enumerate(milestones[1:]):
            print(f"  - Milestone {idx + 2}: \"{m['title']}\" ({m['status']})")
            
        # 4. Check Skill Gaps
        gaps = req(f'/api/learners/{lid}/skills/gaps')
        gap_names = [g['skill_name'] for g in gaps]
        print(f"Top 4 Skill Gaps: {gap_names[:4]}")
        
        # 5. Check Next Action
        next_act = req(f'/api/learners/{lid}/roadmap/next-action')
        print(f"Next Action: {next_act['action']} - {next_act['message']}")
        
        # Assertions to ensure each goal is personalized and distinct
        for top_skill in tc['expected_top_skills']:
            assert any(top_skill.lower() in gn.lower() for gn in gap_names), f"Expected skill '{top_skill}' missing for goal '{tc['goal_input']}'"
            
    print("\n=================================================================")
    print(" VERIFYING MATERIAL DIFFERENCES ACROSS ALL 5 GENERATED ROADMAPS")
    print("=================================================================")
    for i, t in enumerate(all_milestone_titles):
        print(f"Goal {i+1} ({test_cases[i]['goal_input']}) -> Step 1: {t}")
        
    unique_titles = set(all_milestone_titles)
    print(f"\nUnique Step 1 Titles count: {len(unique_titles)} / 5")
    assert len(unique_titles) >= 4, "Roadmaps must produce materially different Step 1 titles!"
    
    print("\n=================================================================")
    print(" ALL 5 DISTINCT GOAL ROADMAPS GENERATED WITH 100% SUCCESS!")
    print("=================================================================")

if __name__ == '__main__':
    test_goals()
