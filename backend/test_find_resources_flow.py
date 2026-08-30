import urllib.request
import json

def test_find_resources():
    print("=========================================================")
    print(" TESTING FIND RESOURCES FLOW (SKILLS -> RESOURCES)")
    print("=========================================================")

    BASE = 'http://127.0.0.1:8000'

    def req(path, method='GET', data=None):
        url = f"{BASE}{path}"
        r = urllib.request.Request(url, method=method)
        r.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8') if data is not None else None
        with urllib.request.urlopen(r, data=body) as resp:
            return json.loads(resp.read().decode('utf-8'))

    # Step 1: Create learner & roadmap
    l = req('/api/learners', 'POST', {'name': 'Taylor Skills'})
    lid = l['id']
    req(f'/api/learners/{lid}/onboard', 'POST', {'goal_text': 'Full Stack and Data Engineer'})
    req(f'/api/learners/{lid}/roadmap', 'POST')
    
    # Step 2: Fetch Skill Gaps
    print("\n1. Fetching Skill Gaps from /api/learners/{id}/skills/gaps...")
    gaps = req(f'/api/learners/{lid}/skills/gaps')
    print(f" -> Found {len(gaps)} skill gaps.")
    assert len(gaps) >= 2, "Need at least 2 skill gaps for testing."

    # Test with at least 2 distinct skills
    test_skills = gaps[:3]
    recs = req(f'/api/learners/{lid}/recommendations')
    print(f" -> Total recommended resources in catalog: {len(recs)}")

    for i, g in enumerate(test_skills):
        skill_id = g['skill_id']
        skill_name = g['skill_name']
        print(f"\n2.{i+1} Testing 'Find Resources' for Skill #{i+1}: '{skill_name}' (ID: {skill_id})")

        # Simulate client filtering logic implemented in Resources.tsx
        matching_resources = []
        for r_item in recs:
            res = r_item.get('resource', r_item)
            res_skill_ids = res.get('skill_ids') or []
            
            has_skill_id = skill_id in res_skill_ids
            has_name_in_title = skill_name.lower() in res.get('title', '').lower()
            has_name_in_desc = skill_name.lower() in (res.get('description') or '').lower()
            
            # Keyword matching
            keywords = [k for k in skill_name.lower().split() if len(k) > 2]
            has_keyword = any(k in res.get('title', '').lower() or k in (res.get('description') or '').lower() for k in keywords)

            if has_skill_id or has_name_in_title or has_name_in_desc or has_keyword:
                matching_resources.append(res)

        print(f" -> Found {len(matching_resources)} filtered resources for '{skill_name}':")
        for r in matching_resources[:2]:
            print(f"     • [{r.get('type')}] \"{r.get('title')}\" ({r.get('provider')}) -> {r.get('url')}")
            assert (r.get('url') or '').startswith('http'), f"Invalid resource URL: {r.get('url')}"

    print("\n=========================================================")
    print(" ALL FIND RESOURCES FLOW TESTS PASSED WITH 100% SUCCESS!")
    print("=========================================================")

if __name__ == '__main__':
    test_find_resources()
