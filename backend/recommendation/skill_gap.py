from typing import List, Dict, Any

class SkillGap:
    def __init__(self, skill_id: int, skill_name: str, current: float, required: float, weight: float, prerequisite_urgency: float = 0.0):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.current = current
        self.required = required
        self.weight = weight
        self.gap = max(0, required - current)
        self.priority = self.gap * weight * (1 + prerequisite_urgency)

def calculate_skill_gaps(learner_skills: List[Any], goal_requirements: List[Any], prerequisite_graph: Dict = None) -> List[SkillGap]:
    # Map learner skills by skill_id
    current_levels = {ls.skill_id: (ls.system_confidence or 0.0) for ls in learner_skills}
    
    gaps = []
    for req in goal_requirements:
        current = current_levels.get(req.skill_id, 0.0)
        
        # Calculate prerequisite urgency
        prereq_urgency = 0.0
        if prerequisite_graph:
            dependents = _count_dependents(req.skill_id, goal_requirements, prerequisite_graph)
            prereq_urgency = min(dependents * 0.1, 0.5)
            
        gap = SkillGap(
            skill_id=req.skill_id,
            skill_name=req.skill.name if hasattr(req, 'skill') else f"Skill {req.skill_id}",
            current=current,
            required=req.required_proficiency,
            weight=req.weight,
            prerequisite_urgency=prereq_urgency
        )
        if gap.gap > 0:
            gaps.append(gap)
            
    # Sort by priority descending
    gaps.sort(key=lambda x: x.priority, reverse=True)
    return gaps

def _count_dependents(skill_id: int, goal_requirements: List[Any], prerequisite_graph: Dict) -> int:
    count = 0
    req_skill_ids = {req.skill_id for req in goal_requirements}
    for req_id in req_skill_ids:
        if req_id in prerequisite_graph and skill_id in prerequisite_graph[req_id]:
            count += 1
    return count

def calculate_system_confidence(self_reported: float = None, demonstrated: float = None) -> float:
    """Calculate combined system confidence level from self-reported and demonstrated proficiencies."""
    if self_reported is None and demonstrated is None:
        return 0.0
    if demonstrated is None:
        return float(self_reported or 0.0) * 0.7
    if self_reported is None:
        return float(demonstrated)
    return 0.4 * float(self_reported) + 0.6 * float(demonstrated)
