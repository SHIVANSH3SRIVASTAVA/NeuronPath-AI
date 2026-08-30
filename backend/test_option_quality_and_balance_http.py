import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_option_quality_and_balance():
    print("\n================================================================================")
    print(" TESTING ASSESSMENT ANSWER-OPTION QUALITY, LENGTH PARITY & POSITION BALANCE")
    print("================================================================================")
    
    test_goals = [
        ("Full Stack Web Development", "Full Stack Developer"),
        ("Data Analytics Mastery", "Data Analyst"),
        ("Docker & DevOps Containerization", "DevOps Engineer"),
        ("Enterprise Java Backend", "Java Developer"),
        ("Machine Learning Foundations", "Machine Learning Engineer"),
    ]
    
    total_questions = 0
    position_counts = {0: 0, 1: 0, 2: 0, 3: 0} # A, B, C, D
    longest_count = 0
    shortest_count = 0
    middle_count = 0
    length_ratios = []
    
    all_sample_questions = []

    for title, role in test_goals:
        # 1. Create learner
        res_l = requests.post(f"{BASE_URL}/api/learners", json={"name": f"Tester {role}", "experience_level": "intermediate", "weekly_hours": 15})
        assert res_l.status_code == 200, res_l.text
        learner_id = res_l.json()["id"]
        
        # 2. Set goal
        res_g = requests.post(f"{BASE_URL}/api/learners/{learner_id}/goal", json={"title": title, "target_role": role, "timeline_months": 6})
        assert res_g.status_code == 200, res_g.text
        
        # 3. Generate roadmap
        res_r = requests.post(f"{BASE_URL}/api/learners/{learner_id}/roadmap")
        assert res_r.status_code == 200, res_r.text
        roadmap_data = res_r.json()
        milestones = roadmap_data.get("milestones", [])
        
        # 4. Test first 2 milestones
        for m in milestones[:2]:
            res_a = requests.post(f"{BASE_URL}/api/assessments/generate?learner_id={learner_id}", json={"milestone_id": m["id"]})
            assert res_a.status_code == 200, res_a.text
            assessment_data = res_a.json()
            assessment_id = assessment_data["id"]
            questions = assessment_data.get("questions", [])
            
            # Submit empty answers to get official explanations and correct answers
            res_sub = requests.post(f"{BASE_URL}/api/assessments/{assessment_id}/submit?learner_id={learner_id}", json={"answers": {}})
            assert res_sub.status_code == 200, res_sub.text
            sub_data = res_sub.json()
            explanations = sub_data.get("explanations", [])
            exp_map = {e["question_id"]: e["correct_answer"] for e in explanations}
            
            for q in questions:
                total_questions += 1
                opts = q["options"]
                correct_text = exp_map.get(q["id"])
                assert correct_text in opts, f"Correct answer '{correct_text}' not found in options: {opts}"
                
                corr_idx = opts.index(correct_text)
                corr_len = len(correct_text)
                
                # Verify exactly 4 distinct options
                assert len(opts) == 4, f"Question {q['id']} has {len(opts)} options, expected 4"
                assert len(set(opts)) == 4, f"Question {q['id']} has duplicate options: {opts}"
                assert 0 <= corr_idx < 4, f"Invalid correct index {corr_idx}"
                
                # Position tracking
                position_counts[corr_idx] += 1
                
                # Length analysis
                distractor_lens = [len(opts[i]) for i in range(4) if i != corr_idx]
                avg_dist_len = sum(distractor_lens) / len(distractor_lens)
                ratio = corr_len / avg_dist_len
                length_ratios.append(ratio)
                
                max_len = max(len(o) for o in opts)
                min_len = min(len(o) for o in opts)
                
                if corr_len == max_len and corr_len > min_len:
                    longest_count += 1
                elif corr_len == min_len and corr_len < max_len:
                    shortest_count += 1
                else:
                    middle_count += 1
                    
                if len(all_sample_questions) < 8:
                    all_sample_questions.append({
                        "question": q["question_text"],
                        "options": opts,
                        "correct_index": corr_idx,
                        "correct_letter": ["A", "B", "C", "D"][corr_idx],
                        "lengths": [len(o) for o in opts],
                        "ratio": round(ratio, 2)
                    })

    print(f"\nTotal Evaluated Questions across 5 goals and 10 milestones: {total_questions}")
    print("\n--- 1. Positional Distribution (A, B, C, D) ---")
    letters = ["A", "B", "C", "D"]
    for i in range(4):
        pct = (position_counts[i] / total_questions) * 100
        print(f"  Position {letters[i]} ({i}): {position_counts[i]} questions ({pct:.1f}%)")
        assert position_counts[i] > 0, f"Position {letters[i]} was never selected as correct answer!"
        
    print("\n--- 2. Answer Length Parity Analysis ---")
    print(f"  Correct Answer is Longest: {longest_count} ({longest_count/total_questions*100:.1f}%)")
    print(f"  Correct Answer is Middle Length / Tied: {middle_count} ({middle_count/total_questions*100:.1f}%)")
    print(f"  Correct Answer is Shortest: {shortest_count} ({shortest_count/total_questions*100:.1f}%)")
    
    avg_ratio = sum(length_ratios) / len(length_ratios)
    max_ratio = max(length_ratios)
    min_ratio = min(length_ratios)
    print(f"  Average Length Ratio (Correct / Avg Distractors): {avg_ratio:.2f}")
    print(f"  Min Length Ratio: {min_ratio:.2f}, Max Length Ratio: {max_ratio:.2f}")
    
    # Assertions for option quality and balance
    # Requirement: The correct answer MUST NOT systematically be the longest (< 50% of time)
    assert longest_count / total_questions < 0.50, f"Correct answer was longest {longest_count/total_questions*100:.1f}% of the time (too high)"
    # Requirement: Max length ratio must be well-bounded (no extreme outliers)
    assert max_ratio <= 1.45, f"Maximum length ratio {max_ratio:.2f} exceeded threshold 1.45"
    assert min_ratio >= 0.55, f"Minimum length ratio {min_ratio:.2f} fell below threshold 0.55"
    # Requirement: All 4 positions (A, B, C, D) are represented reasonably (>= 10% each)
    for i in range(4):
        assert position_counts[i] >= total_questions * 0.10, f"Position {letters[i]} is under-represented"

    print("\n--- 3. Detailed Inspection of Sample Generated Questions ---")
    for idx, sq in enumerate(all_sample_questions, 1):
        print(f"\n[Sample Question {idx}]")
        print(f"Q: {sq['question']}")
        for opt_idx, (opt, l) in enumerate(zip(sq['options'], sq['lengths'])):
            mark = " [CORRECT]" if opt_idx == sq['correct_index'] else ""
            print(f"  ({letters[opt_idx]}) [{l} chars]{mark} {opt}")
        print(f"  -> Correct: {sq['correct_letter']}, Length Ratio: {sq['ratio']}")

    print("\n================================================================================")
    print(" ALL OPTION QUALITY, BALANCING, AND DISTRIBUTION TESTS PASSED! [100%]")
    print("================================================================================\n")

if __name__ == "__main__":
    test_option_quality_and_balance()
