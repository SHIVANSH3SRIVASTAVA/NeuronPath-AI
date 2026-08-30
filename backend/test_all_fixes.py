import urllib.request
import json
import sys

BASE = 'http://127.0.0.1:8000'

def req(url, method='GET', data=None):
    r = urllib.request.Request(f'{BASE}{url}', method=method)
    r.add_header('Content-Type', 'application/json')
    body = json.dumps(data).encode('utf-8') if data is not None else None
    with urllib.request.urlopen(r, data=body) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print('=== 1. TESTING GOAL PRESERVATION FOR 3 DIFFERENT GOALS ===')

    # Test Goal 1: SQL
    l1 = req('/api/learners', 'POST', {'name': 'Devin SQL'})
    onb1 = req(f'/api/learners/{l1["id"]}/onboard', 'POST', {'goal_text': 'SQL'})
    print(f'Input: "SQL" -> Target Role: {onb1["target_role"]}, Goal: {onb1["goal"]}')
    assert 'Machine Learning' not in onb1['target_role'], 'Error: Hardcoded ML role detected!'
    assert 'SQL' in onb1['target_role'], 'Error: SQL not in target role!'

    # Test Goal 2: Data Analyst
    l2 = req('/api/learners', 'POST', {'name': 'Dana Analyst'})
    onb2 = req(f'/api/learners/{l2["id"]}/onboard', 'POST', {'goal_text': 'I want to become a Data Analyst in 4 months with 15 hours per week'})
    print(f'Input: "Data Analyst in 4 months" -> Target Role: {onb2["target_role"]}, Goal: {onb2["goal"]}, Timeline: {onb2["timeline_months"]}, Hours: {onb2["weekly_hours"]}')
    assert onb2['target_role'] == 'Data Analyst', f'Error: Target role mismatch ({onb2["target_role"]})!'
    assert onb2['timeline_months'] == 4, 'Error: Timeline not extracted!'
    assert onb2['weekly_hours'] == 15.0, 'Error: Hours not extracted!'

    # Test Goal 3: Cybersecurity Engineer
    l3 = req('/api/learners', 'POST', {'name': 'Sam Security'})
    onb3 = req(f'/api/learners/{l3["id"]}/onboard', 'POST', {'goal_text': 'Cybersecurity Engineer'})
    print(f'Input: "Cybersecurity Engineer" -> Target Role: {onb3["target_role"]}, Goal: {onb3["goal"]}')
    assert onb3['target_role'] == 'Cybersecurity Engineer', 'Error: Cybersecurity role mismatch!'

    print('\n=== 2. TESTING EDIT MANUALLY PERSISTENCE ===')
    # Edit manual update
    edit_payload = {
        'title': 'Senior Cloud & Database Architect',
        'target_role': 'SQL Developer',
        'timeline_months': 5,
        'weekly_hours': 18.0,
        'experience_level': 'intermediate',
        'known_skills': ['SQL Fundamentals', 'Linux Command Line']
    }
    edit_res = req(f'/api/learners/{l1["id"]}/goal', 'POST', edit_payload)
    print(f'Updated Goal Result: {edit_res}')
    # Generate roadmap from edited goal
    rm1 = req(f'/api/learners/{l1["id"]}/roadmap', 'POST')
    print(f'Generated Roadmap Milestones: {len(rm1["milestones"])}')
    assert len(rm1['milestones']) > 0, 'Error: Roadmap should have milestones!'

    print('\n=== 3. TESTING DASHBOARD ENDPOINTS ===')
    prog1 = req(f'/api/learners/{l1["id"]}/progress')
    print(f'Progress overall: {prog1["overall_progress"]}%')
    next1_a = req(f'/api/learners/{l1["id"]}/next-action')
    next1_b = req(f'/api/learners/{l1["id"]}/roadmap/next-action')
    print(f'Next Action (/next-action): {next1_a["action"]} - {next1_a["message"]}')
    print(f'Next Action (/roadmap/next-action): {next1_b["action"]} - {next1_b["message"]}')
    assert next1_a['action'] == next1_b['action'], 'Error: Next action endpoints should match!'

    print('\n=== 4. TESTING ASSESSMENTS (NO PLACEHOLDERS) ===')
    ass1 = req(f'/api/assessments/generate?learner_id={l1["id"]}', 'POST', {'milestone_id': 0, 'skill_ids': []})
    print(f'Generated Assessment ID: {ass1["id"]}, Questions: {len(ass1["questions"])}')
    for i, q in enumerate(ass1['questions']):
        print(f'  Q{i+1}: {q["question_text"]}')
        print(f'      Options: {q["options"]}')
        assert 'Sample question' not in q['question_text'], f'Error: Placeholder question found: {q["question_text"]}'
        assert len(q['options']) == 4, 'Error: Must have 4 valid options'
        assert q['options'] != ['A', 'B', 'C', 'D'], f'Error: Placeholder A/B/C/D found in options: {q["options"]}'

    # Submit answers
    sub1 = req(f'/api/assessments/{ass1["id"]}/submit?learner_id={l1["id"]}', 'POST', {'answers': {str(ass1["questions"][0]["id"]): 0}})
    print(f'Submission Result Score: {sub1["score"]}%, Adaptations: {sub1["adaptations"]}')
    assert len(sub1['explanations']) > 0, 'Error: Explanations missing in submission response'
    for exp in sub1['explanations']:
        assert exp['explanation'] and exp['explanation'] != 'Explanation here.', 'Error: Placeholder explanation detected!'

    print('\n=== 5. TESTING RESOURCES (NO PLACEHOLDER URLS) ===')
    recs1 = req(f'/api/learners/{l1["id"]}/recommendations')
    print(f'Recommended Resources count: {len(recs1)}')
    for r_item in recs1[:5]:
        r = r_item.get('resource', r_item)
        print(f'  Resource: "{r["title"]}" -> URL: {r.get("url")}')
        assert not (r.get('url') or '').startswith('#demo'), f'Error: Placeholder demo URL found: {r.get("url")}'
        assert (r.get('url') or '').startswith('http'), f'Error: Invalid URL scheme: {r.get("url")}'

    print('\n=== 6. TESTING DATA CONSISTENCY ===')
    gaps1 = req(f'/api/learners/{l1["id"]}/skills/gaps')
    print(f'Learner 1 ({onb1["target_role"]}) skill gaps count: {len(gaps1)}')
    gap_names = [g['skill_name'] for g in gaps1]
    print(f'Top skill gaps for SQL Developer: {gap_names[:5]}')
    assert 'SQL Fundamentals' in gap_names or 'SQL Advanced' in gap_names, 'Error: SQL skills missing in SQL track!'

    # Test AI Coach context for this learner
    coach_res = req(f'/api/learners/{l1["id"]}/coach/chat', 'POST', {'content': 'What is my goal?'})
    print(f'Coach response for SQL Learner: {coach_res["content"][:150]}...')
    assert 'SQL' in coach_res['content'] or 'Database' in coach_res['content'] or 'Senior Cloud' in coach_res['content'], 'Error: Coach unaware of learner SQL goal!'

    print('\n=============================================')
    print(' ALL 6 VERIFICATION TEST SUITES PASSED! [100%]')
    print('=============================================')

if __name__ == '__main__':
    run_tests()
