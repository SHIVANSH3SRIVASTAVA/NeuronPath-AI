from typing import List, Dict, Any, Tuple
from .skill_gap import SkillGap
from .prerequisite import check_prerequisites_met

def calculate_recommendation_score(
    resource: Any, 
    learner: Any, 
    skill_gaps: List[SkillGap], 
    prerequisite_graph: Dict[int, List[int]], 
    learner_skills: List[Any]
) -> Tuple[float, Dict[str, float]]:
    
    # Initialize score components
    scores = {
        'goal_relevance': 0.0,
        'skill_gap_coverage': 0.0,
        'prerequisite_readiness': 0.0,
        'difficulty_fit': 0.0,
        'duration_fit': 0.0,
        'format_preference': 0.0,
        'quality': 0.0
    }
    
    # 1. Goal relevance (0.25) & 2. Skill gap coverage (0.20)
    gap_dict = {gap.skill_id: gap for gap in skill_gaps}
    resource_skills = resource.skill_ids if hasattr(resource, 'skill_ids') and resource.skill_ids else []
    
    gap_coverage_sum = 0.0
    relevance_count = 0
    
    for skill_id in resource_skills:
        if skill_id in gap_dict:
            relevance_count += 1
            # Normalize gap to 0-1
            norm_gap = min(1.0, gap_dict[skill_id].gap / 100.0)
            gap_coverage_sum += norm_gap * gap_dict[skill_id].weight
            
    if resource_skills:
        scores['goal_relevance'] = min(1.0, relevance_count / len(resource_skills))
        scores['skill_gap_coverage'] = min(1.0, gap_coverage_sum / max(1, len(resource_skills)))
        
    # 3. Prerequisite readiness (0.15)
    resource_prereqs = resource.prerequisite_skill_ids if hasattr(resource, 'prerequisite_skill_ids') and resource.prerequisite_skill_ids else []
    ready = True
    current_levels = {ls.skill_id: (ls.system_confidence or 0.0) for ls in learner_skills} if learner_skills else {}
    
    for prereq_id in resource_prereqs:
        if current_levels.get(prereq_id, 0.0) < 40.0:
            ready = False
            break
            
    scores['prerequisite_readiness'] = 1.0 if ready else 0.0
    
    # 4. Difficulty fit (0.15)
    level_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    learner_exp = (getattr(learner, 'experience_level', 'beginner') or 'beginner').lower()
    learner_level = level_map.get(learner_exp, 1)
    
    res_diff = (getattr(resource, 'difficulty', 'intermediate') or 'intermediate').lower()
    resource_diff = level_map.get(res_diff, 1)
    
    diff_distance = abs(learner_level - resource_diff)
    if diff_distance == 0:
        scores['difficulty_fit'] = 1.0
    elif diff_distance == 1:
        scores['difficulty_fit'] = 0.5
    else:
        scores['difficulty_fit'] = 0.1
        
    # 5. Duration fit (0.10)
    res_duration = float(getattr(resource, 'duration_hours', 5.0) or 5.0)
    weekly_hours = float(getattr(learner, 'weekly_hours', 10.0) or 10.0)
    
    if res_duration <= weekly_hours:
        scores['duration_fit'] = 1.0
    elif res_duration <= weekly_hours * 2:
        scores['duration_fit'] = 0.7
    else:
        scores['duration_fit'] = 0.3
        
    # 6. Format preference (0.05)
    preferred_formats = getattr(learner, 'preferred_formats', None)
    res_type = getattr(resource, 'type', 'course') or 'course'
    if preferred_formats and isinstance(preferred_formats, list) and len(preferred_formats) > 0:
        if res_type in preferred_formats:
            scores['format_preference'] = 1.0
        else:
            scores['format_preference'] = 0.2
    else:
        scores['format_preference'] = 1.0 # No preference -> matches everything
        
    # 7. Quality (0.10)
    scores['quality'] = float(getattr(resource, 'quality_score', 50.0) or 50.0) / 100.0
    
    # Calculate final weighted score
    weights = {
        'goal_relevance': 0.25,
        'skill_gap_coverage': 0.20,
        'prerequisite_readiness': 0.15,
        'difficulty_fit': 0.15,
        'duration_fit': 0.10,
        'format_preference': 0.05,
        'quality': 0.10
    }
    
    final_score = sum(scores[k] * weights[k] for k in scores) * 100.0
    
    # Apply penalty if prerequisites not met
    if not ready:
        final_score *= 0.3
        
    return final_score, scores

def rank_resources(resources: List[Any], learner: Any, skill_gaps: List[SkillGap], prerequisite_graph: Dict[int, List[int]], learner_skills: List[Any]) -> List[Tuple[Any, float, Dict]]:
    results = []
    for resource in resources:
        score, breakdown = calculate_recommendation_score(resource, learner, skill_gaps, prerequisite_graph, learner_skills)
        results.append((resource, score, breakdown))
        
    results.sort(key=lambda x: x[1], reverse=True)
    return results
