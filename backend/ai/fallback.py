def get_fallback_response(intent: str, context: dict = None) -> str:
    """Context-aware fallback responses when LLM is unavailable."""
    ctx = context or {}
    name = ctx.get('learner_name', 'there')
    milestone = ctx.get('current_milestone', 'your current milestone')
    progress = ctx.get('overall_progress', 0)
    target_role = ctx.get('target_role', 'your goal')
    gaps = ctx.get('top_skill_gaps', '')
    skills_text = ctx.get('current_skills', '')
    
    responses = {
        'ROADMAP_QUERY': f"Hey {name}! You're currently working on '{milestone}'. "
            f"Your overall progress is {progress:.0f}%. "
            f"Keep focusing on this milestone — once you complete its resources and assessment, the next one will unlock automatically. "
            f"Check the Roadmap page for the full path to becoming {target_role}.",
        
        'PROGRESS_QUERY': f"Here's where you stand, {name}: you're at {progress:.0f}% overall progress toward {target_role}. "
            f"{'Great momentum — keep going!' if progress > 30 else 'You are just getting started — every expert was once a beginner!'} "
            f"Head to the Progress page for detailed analytics.",
        
        'SKILL_QUERY': f"{name}, here's your skill snapshot: {skills_text or 'Check the Skills page for your detailed gap analysis.'}. "
            + (f"Your top gaps are: {gaps}." if gaps else "Visit the Skills page to see where you stand."),
        
        'RECOMMENDATION': f"Based on your skill gaps, I'd recommend focusing on the resources in your current milestone: '{milestone}'. "
            f"The Resources page has personalized recommendations ranked by relevance to your {target_role} goal.",
        
        'LEARNING_EXPLAIN': f"I'd love to explain that in detail, {name}, but my AI engine is currently in offline mode. "
            f"For now, check out the resources in your current milestone — they cover the key concepts you need. "
            f"You can also try asking me again later!",
        
        'ASSESSMENT_REQ': f"Ready to test your knowledge, {name}? "
            f"Head to the Assessment page to take a quiz on your current milestone skills. "
            f"Your roadmap will automatically adapt based on your score — "
            f"scoring 70%+ unlocks the next milestone!",
        
        'ROADMAP_CHANGE': f"To modify your roadmap, you have a few options:\n"
            f"• Update your profile (experience level, weekly hours) to recalibrate\n"
            f"• Take an assessment — high scores can accelerate your path\n"
            f"• Click 'Recalculate Path' on the Roadmap page\n"
            f"Your path will adapt automatically as you progress.",
        
        'TIME_CHANGE': f"I understand your schedule might be changing, {name}. "
            f"You can update your weekly commitment in your Profile page. "
            f"Your roadmap timeline will adjust accordingly.",
        
        'GOAL_CHANGE': f"Want to change direction, {name}? You can update your goal through the onboarding flow. "
            f"This will generate a completely new roadmap tailored to your new target.",
        
        'GENERAL': f"Hi {name}! I'm your NeuronPath AI coach. "
            f"I'm currently running in offline mode, but I can still help with:\n"
            f"• 📍 Roadmap guidance — ask about your learning path\n"
            f"• 📊 Progress updates — ask how you're doing\n"
            f"• 🎯 Skill analysis — ask about your gaps\n"
            f"• 📚 Recommendations — ask what to study next\n"
            f"• 📝 Assessments — ask to test your knowledge"
    }
    
    return responses.get(intent, responses['GENERAL'])
