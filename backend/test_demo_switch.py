import urllib.request
import json

def test_demo_switch():
    print("=========================================================")
    print(" TESTING QUICK SWITCH DEMO FLOW (ALEX <-> SAM)")
    print("=========================================================")

    BASE = 'http://127.0.0.1:8000'

    def req(path, method='GET', data=None):
        url = f"{BASE}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    # Step 1: List demo learners
    print("\n1. Listing Demo Learners via GET /api/demo/learners...")
    list_res = req('/api/demo/learners')
    print(f" -> Response: {list_res}")
    demo_learners = list_res['demo_learners']
    assert len(demo_learners) == 2, "Expected 2 demo learners."
    assert "Alex Chen" in demo_learners[0]['name'], "Alex Chen missing in demo learners"
    assert "Sam Rivera" in demo_learners[1]['name'], "Sam Rivera missing in demo learners"

    # Step 2: Switch to Alex Chen (Beginner)
    print("\n2. Switching to Alex Chen (POST /api/demo/switch/alex)...")
    alex_res = req('/api/demo/switch/alex', 'POST')
    print(f" -> Switched to: {alex_res['learner']['name']} (ID: {alex_res['learner']['id']}, Level: {alex_res['learner']['experience_level']})")
    alex_id = alex_res['learner']['id']
    assert "Alex" in alex_res['learner']['name']
    assert alex_res['learner']['experience_level'] == 'beginner'

    # Step 3: Fetch Alex's data (Roadmap, Progress, Gaps, Recommendations)
    alex_roadmap = req(f'/api/learners/{alex_id}/roadmap')
    alex_progress = req(f'/api/learners/{alex_id}/progress')
    alex_gaps = req(f'/api/learners/{alex_id}/skills/gaps')
    alex_recs = req(f'/api/learners/{alex_id}/recommendations')
    print(f" -> Alex Chen: {len(alex_roadmap['milestones'])} milestones, {len(alex_gaps)} skill gaps, {len(alex_recs)} recommended resources.")

    # Step 4: Switch to Sam Rivera (Intermediate)
    print("\n4. Switching to Sam Rivera (POST /api/demo/switch/sam)...")
    sam_res = req('/api/demo/switch/sam', 'POST')
    print(f" -> Switched to: {sam_res['learner']['name']} (ID: {sam_res['learner']['id']}, Level: {sam_res['learner']['experience_level']})")
    sam_id = sam_res['learner']['id']
    assert "Sam" in sam_res['learner']['name']
    assert sam_res['learner']['experience_level'] == 'intermediate'
    assert sam_id != alex_id, "Alex and Sam must have different learner IDs!"

    # Step 5: Fetch Sam's data
    sam_roadmap = req(f'/api/learners/{sam_id}/roadmap')
    sam_progress = req(f'/api/learners/{sam_id}/progress')
    sam_gaps = req(f'/api/learners/{sam_id}/skills/gaps')
    sam_recs = req(f'/api/learners/{sam_id}/recommendations')
    print(f" -> Sam Rivera: {len(sam_roadmap['milestones'])} milestones, {len(sam_gaps)} skill gaps, {len(sam_recs)} recommended resources.")

    # Step 6: Verify differences between Alex and Sam
    print("\n6. Verifying differences between Beginner (Alex) and Intermediate (Sam)...")
    print(f" -> Alex Weekly Hours: {alex_res['learner']['weekly_hours']}h vs Sam Weekly Hours: {sam_res['learner']['weekly_hours']}h")
    print(f" -> Alex Experience Level: {alex_res['learner']['experience_level']} vs Sam Experience Level: {sam_res['learner']['experience_level']}")

    # Step 7: Switch back to Alex Chen to verify repeated bidirectional switching
    print("\n7. Switching back to Alex Chen (Alex -> Sam -> Alex)...")
    alex_switch_back = req('/api/demo/switch/alex', 'POST')
    assert alex_switch_back['learner']['id'] == alex_id, "Alex ID should be preserved"
    print(f" -> Successfully switched back to {alex_switch_back['learner']['name']}!")

    print("\n=========================================================")
    print(" ALL QUICK SWITCH DEMO TESTS PASSED WITH 100% SUCCESS!")
    print("=========================================================")

if __name__ == '__main__':
    test_demo_switch()
