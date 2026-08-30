from recommendation.prerequisite import build_prerequisite_graph

class DummyPrereq:
    def __init__(self, s, p):
        self.skill_id = s
        self.prerequisite_id = p

def test_build_graph():
    prereqs = [DummyPrereq(2, 1), DummyPrereq(3, 2)]
    graph = build_prerequisite_graph(prereqs)
    assert graph[2] == [1]
    assert graph[3] == [2]
