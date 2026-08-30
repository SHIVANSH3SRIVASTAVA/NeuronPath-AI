from recommendation.skill_gap import calculate_system_confidence

def test_system_confidence():
    assert calculate_system_confidence(100, None) == 70.0
    assert calculate_system_confidence(100, 50) == 70.0
    assert calculate_system_confidence(50, 100) == 80.0
