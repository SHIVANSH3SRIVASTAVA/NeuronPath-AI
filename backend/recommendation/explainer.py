from typing import Dict, Any

def generate_explanation(resource: Any, score: float, breakdown: Dict[str, float]) -> str:
    """Generate a human-readable explanation for why a resource was recommended."""
    reasons = []
    
    if breakdown.get('goal_relevance', 0) > 0.8:
        reasons.append("It directly aligns with your current learning goals.")
        
    if breakdown.get('skill_gap_coverage', 0) > 0.7:
        reasons.append("It targets your biggest skill gaps.")
        
    if breakdown.get('difficulty_fit', 0) > 0.8:
        reasons.append(f"The {resource.difficulty} difficulty is a perfect match for your current level.")
        
    if breakdown.get('duration_fit', 0) > 0.8:
        reasons.append("It fits well within your weekly learning schedule.")
        
    if breakdown.get('format_preference', 0) > 0.8:
        reasons.append(f"It matches your preferred learning format ({resource.type}).")
        
    if not reasons:
        return f"This {resource.type} is recommended based on your overall profile."
        
    explanation = f"We highly recommend this {resource.type} because: "
    explanation += " ".join(reasons)
    
    return explanation
