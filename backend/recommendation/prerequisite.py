from typing import List, Dict, Set, Any
from collections import defaultdict, deque

def build_prerequisite_graph(skill_prerequisites: List[Any]) -> Dict[int, List[int]]:
    """Build adjacency list where key is skill_id, value is list of prerequisite_ids."""
    graph = defaultdict(list)
    for sp in skill_prerequisites:
        graph[sp.skill_id].append(sp.prerequisite_id)
    return graph

def get_prerequisite_chain(skill_id: int, graph: Dict[int, List[int]]) -> List[int]:
    """Topological sort of prerequisites for a specific skill using DFS."""
    visited = set()
    chain = []
    
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for prereq in graph.get(node, []):
            dfs(prereq)
        if node != skill_id:
            chain.append(node)
            
    dfs(skill_id)
    return chain

def check_prerequisites_met(skill_id: int, learner_skills: List[Any], graph: Dict[int, List[int]], threshold: float = 40.0) -> bool:
    """Check if all prerequisites for a given skill have been met by learner."""
    prereqs = graph.get(skill_id, [])
    if not prereqs:
        return True
        
    current_levels = {ls.skill_id: (ls.system_confidence or 0.0) for ls in learner_skills} if learner_skills else {}
    
    for prereq_id in prereqs:
        level = current_levels.get(prereq_id, 0.0)
        if level < threshold:
            return False
            
    return True

def get_learning_order(
    required_skills: List[int], 
    learner_skills: List[Any], 
    graph: Dict[int, List[int]], 
    skill_weights: Dict[int, float] = None
) -> List[int]:
    """
    Topological sort of required skills ensuring prerequisites come first,
    while prioritizing high-weight, goal-critical skills when multiple skills are ready.
    """
    current_levels = {ls.skill_id: (ls.system_confidence or 0.0) for ls in learner_skills} if learner_skills else {}
    # Filter out already mastered skills (> 95% proficiency)
    skills_to_learn = [s for s in required_skills if current_levels.get(s, 0.0) < 95.0]
    
    if not skills_to_learn:
        skills_to_learn = list(required_skills)
        
    if not skill_weights:
        skill_weights = {}

    in_degree = {s: 0 for s in skills_to_learn}
    adj_list = defaultdict(list)
    skills_set = set(skills_to_learn)
    
    for s in skills_to_learn:
        prereqs = graph.get(s, [])
        for p in prereqs:
            if p in skills_set:
                adj_list[p].append(s)
                in_degree[s] += 1
                
    # Initial queue of unblocked skills, sorted by goal priority weight descending
    available = [s for s in skills_to_learn if in_degree[s] == 0]
    available.sort(key=lambda s: skill_weights.get(s, 1.0), reverse=True)
    
    order = []
    while available:
        current = available.pop(0)
        order.append(current)
        
        newly_available = []
        for neighbor in adj_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                newly_available.append(neighbor)
                
        if newly_available:
            available.extend(newly_available)
            available.sort(key=lambda s: skill_weights.get(s, 1.0), reverse=True)
        
    # Append any remaining skills if cycle detected
    if len(order) != len(skills_to_learn):
        remaining = [s for s in skills_to_learn if s not in order]
        remaining.sort(key=lambda s: skill_weights.get(s, 1.0), reverse=True)
        order.extend(remaining)
        
    return order
