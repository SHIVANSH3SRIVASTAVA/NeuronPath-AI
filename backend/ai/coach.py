from models.learner import Learner
from models.roadmap import LearnerGoal, Roadmap, RoadmapMilestone
from models.skill import LearnerSkill
from models.activity import ChatMessage
from services.progress_service import get_progress
from recommendation.skill_gap import calculate_skill_gaps
from models.roadmap import GoalSkillRequirement

INTENTS = {
    'ROADMAP_QUERY': ['roadmap', 'path', 'plan', 'next', 'learn next', 'what should'],
    'PROGRESS_QUERY': ['progress', 'how far', 'completed', 'done', 'close to goal'],
    'SKILL_QUERY': ['skill', 'weak', 'strong', 'gap', 'proficiency'],
    'RECOMMENDATION': ['recommend', 'suggest', 'course', 'resource', 'what to study'],
    'LEARNING_EXPLAIN': ['explain', 'what is', 'how does', 'teach me', 'help me understand'],
    'ASSESSMENT_REQ': ['quiz', 'test', 'assess', 'evaluate'],
    'ROADMAP_CHANGE': ['skip', 'already know', 'change roadmap', 'modify plan'],
    'TIME_CHANGE': ['hours', 'time', 'availability', 'busy', 'free time'],
    'GOAL_CHANGE': ['change goal', 'new goal', 'different career', 'want to become'],
    'GENERAL': []
}

def detect_intent_basic(message: str) -> str:
    """Simple keyword matching for intent detection."""
    msg_lower = message.lower()
    
    best_intent = 'GENERAL'
    max_matches = 0
    
    for intent, keywords in INTENTS.items():
        matches = sum(1 for kw in keywords if kw in msg_lower)
        if matches > max_matches:
            max_matches = matches
            best_intent = intent
            
    return best_intent


def _build_context(db, learner_id: int, intent: str) -> dict:
    """Build rich context for the coach based on intent."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    goal = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id, LearnerGoal.status == "active"
    ).first()
    
    context = {
        "learner_name": learner.name if learner else "Learner",
        "experience_level": learner.experience_level if learner else "unknown",
        "weekly_hours": learner.weekly_hours if learner else 10,
        "goal_title": goal.title if goal else "No goal set",
        "target_role": goal.target_role if goal else "Unknown",
    }
    
    # Get progress data
    progress_data = get_progress(db, learner_id)
    context["overall_progress"] = progress_data.get("overall_progress", 0)
    context["milestones_completed"] = progress_data.get("milestones_completed", 0)
    context["milestones_total"] = progress_data.get("milestones_total", 0)
    context["assessments_taken"] = progress_data.get("assessments_taken", 0)
    context["average_score"] = progress_data.get("average_score", 0)
    
    # Get current milestone
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, Roadmap.status == "active"
    ).first()
    
    if roadmap:
        current_milestone = db.query(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id,
            RoadmapMilestone.status.in_(["available", "in_progress"])
        ).order_by(RoadmapMilestone.order_index).first()
        context["current_milestone"] = current_milestone.title if current_milestone else "None"
        context["current_milestone_objective"] = current_milestone.objective if current_milestone else ""
    else:
        context["current_milestone"] = "No roadmap generated"
        context["current_milestone_objective"] = ""
    
    # Get skill gaps for skill-related intents
    if intent in ['SKILL_QUERY', 'RECOMMENDATION', 'ROADMAP_QUERY']:
        learner_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
        if goal:
            requirements = db.query(GoalSkillRequirement).filter(
                GoalSkillRequirement.goal_id == goal.id
            ).all()
            gaps = calculate_skill_gaps(learner_skills, requirements, None)
            top_gaps = sorted(gaps, key=lambda g: g.gap, reverse=True)[:5]
            context["top_skill_gaps"] = ", ".join([
                f"{g.skill_name} (need {g.required:.0f}%, have {g.current:.0f}%)" 
                for g in top_gaps
            ])
        else:
            context["top_skill_gaps"] = "No goal set to compare against"
        
        # Current skill levels
        skill_summary = []
        for ls in learner_skills[:8]:
            skill_name = ls.skill.name if ls.skill else f"Skill {ls.skill_id}"
            skill_summary.append(f"{skill_name}: {ls.system_confidence:.0f}%")
        context["current_skills"] = ", ".join(skill_summary) if skill_summary else "No skills recorded"
    
    return context


def _build_system_prompt(intent: str, context: dict) -> str:
    """Build a context-rich system prompt for the LLM."""
    base_prompt = f"""You are the AI Learning Coach for NeuronPath — an intelligent learning companion.

LEARNER CONTEXT:
- Name: {context.get('learner_name', 'Learner')}
- Goal: {context.get('goal_title', 'Not set')} → {context.get('target_role', 'Unknown')}
- Level: {context.get('experience_level', 'unknown')}
- Weekly commitment: {context.get('weekly_hours', 10)} hours/week
- Current milestone: {context.get('current_milestone', 'None')}
- Milestone objective: {context.get('current_milestone_objective', '')}
- Overall progress: {context.get('overall_progress', 0):.1f}%
- Milestones: {context.get('milestones_completed', 0)}/{context.get('milestones_total', 0)} completed
- Assessments taken: {context.get('assessments_taken', 0)}, Average score: {context.get('average_score', 0):.0f}%"""

    # Add intent-specific context
    if intent == 'SKILL_QUERY':
        base_prompt += f"\n- Current skills: {context.get('current_skills', 'None')}"
        base_prompt += f"\n- Top skill gaps: {context.get('top_skill_gaps', 'None')}"
    elif intent == 'RECOMMENDATION':
        base_prompt += f"\n- Top skill gaps: {context.get('top_skill_gaps', 'None')}"
    elif intent == 'ROADMAP_QUERY':
        base_prompt += f"\n- Top skill gaps: {context.get('top_skill_gaps', 'None')}"
    
    base_prompt += f"""

DETECTED INTENT: {intent}

INSTRUCTIONS:
- Respond helpfully using the learner's ACTUAL data shown above
- Be specific — reference their real progress, skills, and roadmap
- Be encouraging but honest about areas needing improvement
- Keep responses concise (2-4 paragraphs)
- Use the learner's name naturally
- If they ask about skills, reference their ACTUAL skill levels and gaps
- If they ask what to learn next, reference their ACTUAL current milestone
- If they ask about progress, give them specific numbers
"""
    return base_prompt


async def process_coach_message(learner_id: int, message: str, db, llm) -> dict:
    """Process a coach message with full learner context."""
    # 1. Detect intent
    intent = detect_intent_basic(message)
    
    # 2. Build rich context
    context = _build_context(db, learner_id, intent)
    
    # 3. Save user message
    user_msg = ChatMessage(
        learner_id=learner_id,
        role="user",
        content=message,
        intent=intent
    )
    db.add(user_msg)
    db.commit()
    
    # 4. Get recent chat history for continuity
    recent_messages = db.query(ChatMessage).filter(
        ChatMessage.learner_id == learner_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    history_text = ""
    if len(recent_messages) > 1:
        history_lines = []
        for msg in reversed(recent_messages[1:]):  # Exclude current message, oldest first
            history_lines.append(f"{msg.role.upper()}: {msg.content[:200]}")
        history_text = "\n\nRECENT CONVERSATION:\n" + "\n".join(history_lines[-6:])
    
    # 5. Build system prompt with context
    system_prompt = _build_system_prompt(intent, context) + history_text
    
    # 6. Generate response
    if not llm.is_available():
        from .fallback import get_fallback_response
        content = get_fallback_response(intent, context)
    else:
        try:
            content = await llm.generate(message, system_prompt)
        except Exception:
            from .fallback import get_fallback_response
            content = get_fallback_response(intent, context)
    
    # 7. Save assistant response
    assistant_msg = ChatMessage(
        learner_id=learner_id,
        role="assistant",
        content=content,
        intent=intent
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "content": content,
        "intent": intent,
        "action_taken": None
    }


def get_chat_history(db, learner_id: int, limit: int = 50) -> list:
    """Get chat history for a learner."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.learner_id == learner_id
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "intent": msg.intent,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in messages
    ]
