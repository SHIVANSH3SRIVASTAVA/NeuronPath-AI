import urllib.request
import json
import sys

def test_flow(base_url, desc):
    print(f"\n=======================================================")
    print(f" TESTING BUILD ROADMAP FLOW VIA: {desc} ({base_url})")
    print(f"=======================================================")
    
    def req(path, method='GET', data=None):
        url = f"{base_url}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    # Step 1: User enters Name in chat -> POST /api/learners
    print("Step 1: Create Learner (Name: 'Jordan Cyber')")
    l = req('/learners' if '/api' in base_url else '/api/learners', 'POST', {'name': 'Jordan Cyber'})
    lid = l['id']
    print(f" -> Created learner ID {lid}: {l}")

    # Step 2: User enters Goal in chat -> POST /api/learners/{id}/onboard
    print("Step 2: Onboard Goal ('I want to become a Cybersecurity Engineer')")
    api_prefix = '' if '/api' in base_url else '/api'
    onb = req(f"{api_prefix}/learners/{lid}/onboard", 'POST', {'goal_text': 'I want to become a Cybersecurity Engineer'})
    print(f" -> Extracted Profile: Goal={onb['goal']}, Role={onb['target_role']}, Hours={onb['weekly_hours']}")

    # Step 3: Fetch updated profile -> GET /api/learners/{id}
    print("Step 3: Fetch Learner Profile")
    learner_prof = req(f"{api_prefix}/learners/{lid}")
    print(f" -> Learner Profile: {learner_prof}")

    # Step 4: User clicks 'Looks Good, Build Roadmap' -> PUT /api/learners/{id} (CRITICAL PREVIOUS FAILURE POINT)
    print("Step 4: Update Learner Profile -> PUT /api/learners/{id}")
    put_res = req(f"{api_prefix}/learners/{lid}", 'PUT', {
        'name': 'Jordan Cyber',
        'experience_level': onb['experience_level'],
        'weekly_hours': onb['weekly_hours']
    })
    print(f" -> PUT Result SUCCESS: {put_res}")

    # Step 5: Save Goal -> POST /api/learners/{id}/goal
    print("Step 5: Save Goal -> POST /api/learners/{id}/goal")
    goal_res = req(f"{api_prefix}/learners/{lid}/goal", 'POST', {
        'title': onb['goal'],
        'target_role': onb['target_role'],
        'timeline_months': onb['timeline_months'],
        'known_skills': onb['known_skills'],
        'experience_level': onb['experience_level'],
        'weekly_hours': onb['weekly_hours']
    })
    print(f" -> Goal Save Result: {goal_res}")

    # Step 6: Generate Roadmap -> POST /api/learners/{id}/roadmap
    print("Step 6: Generate Roadmap -> POST /api/learners/{id}/roadmap")
    roadmap_res = req(f"{api_prefix}/learners/{lid}/roadmap", 'POST')
    print(f" -> Roadmap Generated: ID={roadmap_res['id']}, Status={roadmap_res['status']}, Milestones={len(roadmap_res.get('milestones', []))}")
    assert len(roadmap_res.get('milestones', [])) > 0, "Error: No milestones generated!"
    for m in roadmap_res['milestones']:
        print(f"     Milestone {m['order_index'] + 1}: '{m['title']}' ({m['status']}) - {m['estimated_hours']}h")

    # Step 7: Dashboard load -> GET /progress, /roadmap, /next-action
    print("Step 7: Verify Dashboard Data Retrieval")
    prog = req(f"{api_prefix}/learners/{lid}/progress")
    next_act = req(f"{api_prefix}/learners/{lid}/next-action")
    print(f" -> Progress: {prog['overall_progress']}%")
    print(f" -> Next Action: {next_act['action']} - {next_act['message']}")
    print(f" -> ALL 7 ONBOARDING -> BUILD ROADMAP STEPS PASSED PERFECTLY!\n")

if __name__ == '__main__':
    # Test 1: Direct Backend
    test_flow('http://127.0.0.1:8000/api', 'DIRECT FASTAPI BACKEND')
    # Test 2: Via Vite Dev Server Proxy (Exact Browser Path)
    test_flow('http://127.0.0.1:5173/api', 'VITE DEV PROXY')
    print("\n=======================================================")
    print(" ALL TESTS PASSED! ZERO NETWORK OR SERIALIZATION ERRORS")
    print("=======================================================")
