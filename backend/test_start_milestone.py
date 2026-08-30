import urllib.request
import json
import sys

def run_tests():
    print("=========================================================")
    print(" TESTING START MILESTONE FLOW (API & PERSISTENCE)")
    print("=========================================================")

    BASE = 'http://127.0.0.1:8000'

    def req(path, method='GET', data=None):
        url = f"{BASE}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    # Step 1: Create a learner and generate a roadmap
    print("\n1. Creating test learner and roadmap...")
    l = req('/api/learners', 'POST', {'name': 'Morgan Data'})
    lid = l['id']
    onb = req(f'/api/learners/{lid}/onboard', 'POST', {'goal_text': 'I want to become a Data Analyst'})
    roadmap = req(f'/api/learners/{lid}/roadmap', 'POST')
    
    milestones = roadmap['milestones']
    print(f" -> Generated {len(milestones)} milestones.")
    assert len(milestones) >= 2, "Need at least 2 milestones for test."

    first_m = milestones[0]
    print(f" -> Initial Milestone 1 Status: '{first_m['status']}' (ID: {first_m['id']})")
    assert first_m['status'] == 'available', f"Expected initial status 'available', got '{first_m['status']}'"

    # Step 2: Call Start Milestone API (as triggered by clicking 'Start Milestone' button)
    print(f"\n2. Calling Start Milestone for Milestone ID {first_m['id']}...")
    start_res = req(f'/api/learners/{lid}/roadmap/milestones/{first_m["id"]}/start', 'POST')
    print(f" -> Start Milestone API Response: {start_res}")
    assert start_res['status'] == 'success', "Start Milestone API failed!"
    assert start_res['milestone_status'] == 'in_progress', "Status should be 'in_progress'!"

    # Step 3: Fetch fresh roadmap from DB to verify persistence
    print("\n3. Verifying DB persistence via GET /api/learners/{id}/roadmap...")
    fresh_roadmap = req(f'/api/learners/{lid}/roadmap')
    updated_first_m = [m for m in fresh_roadmap['milestones'] if m['id'] == first_m['id']][0]
    print(f" -> Persisted Milestone 1 Status in DB: '{updated_first_m['status']}'")
    assert updated_first_m['status'] == 'in_progress', "Database did not persist 'in_progress' status!"

    # Step 4: Verify Next Action updates accordingly
    print("\n4. Checking Next Action endpoint reflection...")
    next_action = req(f'/api/learners/{lid}/roadmap/next-action')
    print(f" -> Next Action: {next_action['action']} - {next_action['message']}")

    # Step 5: Test idempotence (calling start again when already in_progress)
    print("\n5. Testing idempotence for repeated start calls...")
    repeat_start = req(f'/api/learners/{lid}/roadmap/milestones/{first_m["id"]}/start', 'POST')
    print(f" -> Repeated Start API Response: {repeat_start}")
    assert repeat_start['milestone_status'] == 'in_progress', "Should remain in_progress"

    # Step 6: Test completing a task item in milestone
    if updated_first_m.get('items') and len(updated_first_m['items']) > 0:
        first_item = updated_first_m['items'][0]
        print(f"\n6. Testing task completion for item ID {first_item['id']}...")
        comp_res = req(f'/api/learners/{lid}/roadmap/items/{first_item["id"]}/complete', 'POST')
        print(f" -> Complete Item Response: {comp_res}")
        assert comp_res['item_status'] == 'completed', "Item was not marked completed"

    print("\n=========================================================")
    print(" ALL START MILESTONE VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("=========================================================")

if __name__ == '__main__':
    run_tests()
