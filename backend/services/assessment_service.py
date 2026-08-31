from sqlalchemy.orm import Session
from models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from models.roadmap import Roadmap, RoadmapMilestone, LearnerGoal, GoalSkillRequirement
from models.skill import Skill, LearnerSkill
from catalog_questions import CATALOG_QUESTIONS
import random
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Progressive diagnostic question templates categorized by cognitive level
# Templates are strictly balanced in length, granularity, and grammatical parallelism.
PROGRESSIVE_QUESTION_TEMPLATES = [
    # Level 1: Foundations & Definitions (Easy)
    {
        "tier": "easy",
        "style": "foundations",
        "question": "What is the primary role of {skill_name} in {category} workflows?",
        "correct_desc": "Provides architectural design patterns, abstractions, and core conventions for {skill_name}",
        "distractors": [
            "Manages low-level memory allocations, register sets, and kernel interrupt handlers for {skill_name}",
            "Renders graphical window viewports, handles canvas events, and compiles GPU shaders for {skill_name}",
            "Encrypts transport packets, manages network socket routing, and negotiates TLS handshakes for {skill_name}"
        ]
    },
    {
        "tier": "easy",
        "style": "core_mechanics",
        "question": "Which foundational concept is critical when getting started with {skill_name}?",
        "correct_desc": "Mastering syntax rules, standard data structures, and core conventions for {skill_name}",
        "distractors": [
            "Configuring real-time microcontroller clocks, timer interrupts, and serial bus protocols for {skill_name}",
            "Bypassing static type checks and automated linters to accelerate development builds in {skill_name}",
            "Disabling diagnostic error logging and stack trace generation to eliminate storage overhead in {skill_name}"
        ]
    },
    # Level 2: Understanding & Practical Rules (Intermediate)
    {
        "tier": "intermediate",
        "style": "core_principles",
        "question": "When developing with {skill_name}, which practice is considered an industry standard for reliability?",
        "correct_desc": "Applying modular boundaries, defensive validation, and structured error handling in {skill_name}",
        "distractors": [
            "Directly modifying production server environments without version control or testing in {skill_name}",
            "Hardcoding database connection secrets and private authentication tokens inside client bundles for {skill_name}",
            "Suppressing warning alerts and performance metric collection to minimize background CPU usage in {skill_name}"
        ]
    },
    {
        "tier": "intermediate",
        "style": "practical_methods",
        "question": "How do engineering teams practically implement {skill_name} in day-to-day development?",
        "correct_desc": "Employing established patterns and automated unit testing to manage {skill_name} reliably",
        "distractors": [
            "Executing shell commands with unrestricted superuser privileges across unencrypted public networks in {skill_name}",
            "Persisting transient session tokens in global memory buffers without persistent backing stores in {skill_name}",
            "Disabling firewall access control lists and input filters to permit open ingress traffic in {skill_name}"
        ]
    },
    # Level 3: Application & Best Practices (Intermediate/Advanced)
    {
        "tier": "intermediate",
        "style": "performance_optimization",
        "question": "How do developers optimize performance when implementing {skill_name}?",
        "correct_desc": "Leveraging caching, efficient data indexing, and minimizing redundant operations in {skill_name}",
        "distractors": [
            "Removing input sanitization routines to minimize CPU instruction cycles during execution in {skill_name}",
            "Spawning unbounded concurrent background worker threads without synchronization locks in {skill_name}",
            "Saving raw ephemeral cache data permanently inside relational database tables in {skill_name}"
        ]
    },
    {
        "tier": "intermediate",
        "style": "security_robustness",
        "question": "Which security measure is critical when building systems with {skill_name}?",
        "correct_desc": "Enforcing principle of least privilege, token expiration, and strict input sanitization in {skill_name}",
        "distractors": [
            "Exposing administrative debug interfaces and internal ports directly to external networks in {skill_name}",
            "Disabling cryptographic transport encryption to reduce packet transmission latency and headers in {skill_name}",
            "Using default static administrator credentials and unhashed passwords across all services in {skill_name}"
        ]
    },
    # Level 4: Problem Solving & Tradeoffs (Advanced)
    {
        "tier": "advanced",
        "style": "problem_solving",
        "question": "What is a common pitfall when scaling {skill_name}, and how is it resolved?",
        "correct_desc": "Profiling runtime performance bottlenecks, isolating edge cases, and adding regression tests in {skill_name}",
        "distractors": [
            "Removing automated test suites and validation routines to accelerate deployment pipelines in {skill_name}",
            "Storing unvalidated raw strings in memory instead of using structured and typed schemas in {skill_name}",
            "Relying entirely on developer intuition and memory instead of maintaining technical specs in {skill_name}"
        ]
    },
    {
        "tier": "advanced",
        "style": "architecture_tradeoffs",
        "question": "What primary engineering tradeoff must be evaluated when adopting {skill_name}?",
        "correct_desc": "Balancing architectural implementation complexity against scalability and maintainability in {skill_name}",
        "distractors": [
            "Eliminating static analysis and type validation checks from production build scripts in {skill_name}",
            "Sacrificing transactional data consistency guarantees in exchange for arbitrary latency gains in {skill_name}",
            "Executing manual batch updates via spreadsheets instead of automated migration scripts in {skill_name}"
        ]
    },
    {
        "tier": "advanced",
        "style": "debugging_troubleshooting",
        "question": "When diagnosing a regression involving {skill_name}, what is the recommended workflow?",
        "correct_desc": "Analyzing structured logs, reproducing failures with isolated test cases, and inspecting stack traces in {skill_name}",
        "distractors": [
            "Restarting production cluster nodes repeatedly until intermittent failures subside automatically in {skill_name}",
            "Suppressing application error handlers and try-catch blocks to prevent logs from accumulating in {skill_name}",
            "Reinstalling third-party package dependencies without analyzing the underlying failure root cause in {skill_name}"
        ]
    },
    {
        "tier": "advanced",
        "style": "scalability",
        "question": "How does {skill_name} support high-availability architectures under heavy demand?",
        "correct_desc": "Facilitating decoupled components, horizontal scaling, and stateless request processing in {skill_name}",
        "distractors": [
            "Routing all application traffic through a single monolithic server bottleneck process in {skill_name}",
            "Restricting concurrent user connections strictly to one active client session at a time in {skill_name}",
            "Disabling disk write buffering to force synchronous block writes on every incoming request in {skill_name}"
        ]
    }
]

def validate_and_balance_question(
    q_text: str,
    options: List[str],
    correct_idx: int,
    seen_texts: set
) -> Tuple[bool, Optional[List[str]], Optional[int]]:
    """
    Validates question quality and ensures no answer length/style bias:
    1. Exactly 4 options.
    2. Exactly 4 distinct options (no duplicates).
    3. Exactly 1 valid correct answer index (0..3).
    4. Length parity: The correct option's length must NOT be an obvious outlier (> 1.40x or < 0.60x avg distractor length).
    5. Question text must be unique within the assessment.
    """
    if not q_text or q_text in seen_texts:
        return False, None, None

    if len(options) != 4:
        return False, None, None

    cleaned_options = [opt.strip() for opt in options if opt and opt.strip()]
    if len(cleaned_options) != 4:
        return False, None, None

    if len(set(cleaned_options)) != 4:
        return False, None, None

    if not (0 <= correct_idx < 4):
        return False, None, None

    correct_len = len(cleaned_options[correct_idx])
    distractor_lens = [len(cleaned_options[i]) for i in range(4) if i != correct_idx]
    avg_dist_len = sum(distractor_lens) / max(1, len(distractor_lens))

    # Reject if correct option is disproportionately long or short compared to distractors
    if avg_dist_len > 0:
        ratio = correct_len / avg_dist_len
        if ratio > 1.40 or ratio < 0.60:
            return False, None, None

    return True, cleaned_options, correct_idx

def generate_assessment(db: Session, learner_id: int, milestone_id: Optional[int] = None, skill_ids: Optional[List[int]] = None):
    """
    Generate a milestone-aligned, progressive diagnostic assessment with balanced answer options:
    - 70–80% questions from CURRENT milestone's skills.
    - 20–30% questions from PAST completed prerequisites.
    - 0% questions from FUTURE locked milestones.
    - All 4 options balanced in length, detail, and grammatical structure.
    - Randomized correct answer positions (A, B, C, D) with no length bias.
    - Validation step ensures no option length guessing pattern.
    """
    # 1. Retrieve learner's active goal
    goal = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id,
        LearnerGoal.status == "active"
    ).first()
    
    target_role = goal.target_role if goal else "Software Professional"
    
    # 2. Retrieve roadmap and milestone partitioning for active goal
    roadmap = None
    if goal:
        roadmap = db.query(Roadmap).filter(
            Roadmap.learner_id == learner_id,
            Roadmap.goal_id == goal.id,
            Roadmap.status.in_(["active", "completed"])
        ).order_by(Roadmap.created_at.desc()).first()
    if not roadmap:
        roadmap = db.query(Roadmap).filter(
            Roadmap.learner_id == learner_id,
            Roadmap.status.in_(["active", "completed"])
        ).order_by(Roadmap.created_at.desc()).first()

    all_milestones: List[RoadmapMilestone] = []
    target_milestone: Optional[RoadmapMilestone] = None
    target_index = 0
    
    if roadmap:
        all_milestones = db.query(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id
        ).order_by(RoadmapMilestone.order_index).all()
        
        if milestone_id and milestone_id > 0:
            for idx, m in enumerate(all_milestones):
                if m.id == milestone_id:
                    target_milestone = m
                    target_index = idx
                    break
                    
        if not target_milestone and all_milestones:
            for idx, m in enumerate(all_milestones):
                if m.status in ["available", "in_progress"]:
                    target_milestone = m
                    target_index = idx
                    break
            if not target_milestone:
                target_milestone = all_milestones[0]
                target_index = 0

    # 3. Partition Skills: Current vs Past vs Future
    current_skill_ids: List[int] = []
    past_skill_ids: List[int] = []
    future_skill_ids: List[int] = []

    if target_milestone and target_milestone.skill_ids:
        current_skill_ids = list(target_milestone.skill_ids)
    elif skill_ids and len(skill_ids) > 0:
        current_skill_ids = list(skill_ids)

    if all_milestones:
        for idx, m in enumerate(all_milestones):
            if m.skill_ids:
                if idx < target_index:
                    for sid in m.skill_ids:
                        if sid not in past_skill_ids and sid not in current_skill_ids:
                            past_skill_ids.append(sid)
                elif idx > target_index:
                    for sid in m.skill_ids:
                        if sid not in future_skill_ids and sid not in current_skill_ids:
                            future_skill_ids.append(sid)

    all_skills_map = {s.id: s for s in db.query(Skill).all()}
    all_skills_by_name = {s.name.lower(): s for s in all_skills_map.values()}
    
    if not current_skill_ids:
        current_skill_ids = [list(all_skills_map.keys())[0]]

    # 4. Create Assessment Record
    milestone_title = target_milestone.title if target_milestone else "Skill Assessment"
    assessment_title = f"Assessment: {milestone_title}"
    assessment = Assessment(
        learner_id=learner_id,
        milestone_id=target_milestone.id if target_milestone else None,
        title=assessment_title,
        skill_ids=current_skill_ids + past_skill_ids
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # 5. Question Quotas: ~7-8 Current Milestone questions, ~2-3 Prerequisite questions, 0 Future questions
    target_current_count = 8 if past_skill_ids else 10
    target_past_count = 10 - target_current_count
    
    questions_to_add: List[AssessmentQuestion] = []
    seen_question_texts = set()

    # Helper to randomize options and balance position
    def prepare_and_validate_question(
        raw_text: str,
        raw_options: List[str],
        raw_correct_idx: int,
        skill_id: int,
        difficulty: str,
        explanation: str,
        seed_val: int,
        allow_relaxed: bool = False
    ) -> Optional[AssessmentQuestion]:
        if len(raw_options) != 4 or not (0 <= raw_correct_idx < 4):
            return None
            
        correct_text = raw_options[raw_correct_idx]
        shuffled = list(raw_options)
        
        # True dynamic position randomization
        rng = random.Random(seed_val)
        rng.shuffle(shuffled)
        new_correct_idx = shuffled.index(correct_text)
        
        if allow_relaxed:
            if raw_text in seen_question_texts or len(set(shuffled)) != 4:
                return None
            return AssessmentQuestion(
                assessment_id=assessment.id,
                skill_id=skill_id,
                question_text=raw_text,
                options=shuffled,
                correct_answer_index=new_correct_idx,
                difficulty=difficulty,
                explanation=explanation
            )
            
        is_valid, final_options, final_idx = validate_and_balance_question(
            raw_text, shuffled, new_correct_idx, seen_question_texts
        )
        if not is_valid or not final_options:
            return None
            
        return AssessmentQuestion(
            assessment_id=assessment.id,
            skill_id=skill_id,
            question_text=raw_text,
            options=final_options,
            correct_answer_index=final_idx,
            difficulty=difficulty,
            explanation=explanation
        )

    def add_from_curated_catalog(skill_id_list: List[int], max_count: int) -> int:
        added = 0
        for q_idx, q_data in enumerate(CATALOG_QUESTIONS):
            if added >= max_count:
                break
            q_skill_name = q_data.get("skill", "")
            matching_skill = all_skills_by_name.get(q_skill_name.lower())
            
            if matching_skill and matching_skill.id in skill_id_list:
                q_text = q_data["question"]
                if q_text not in seen_question_texts:
                    seed = hash(q_text) + q_idx + len(questions_to_add) * 17
                    q_obj = prepare_and_validate_question(
                        raw_text=q_text,
                        raw_options=q_data["options"],
                        raw_correct_idx=q_data["correct"],
                        skill_id=matching_skill.id,
                        difficulty=q_data.get("difficulty", "intermediate"),
                        explanation=q_data.get("explanation", ""),
                        seed_val=seed
                    )
                    if q_obj:
                        questions_to_add.append(q_obj)
                        seen_question_texts.add(q_text)
                        added += 1
        return added

    # Step A: Collect Curated Current Milestone Questions
    add_from_curated_catalog(current_skill_ids, target_current_count)

    # Step B: Collect Curated Past Prerequisite Questions
    if past_skill_ids and target_past_count > 0:
        add_from_curated_catalog(past_skill_ids, target_past_count)

    # Step C: Deterministically generate remaining Current Milestone Questions with balanced templates
    current_skills_objs = [all_skills_map[sid] for sid in current_skill_ids if sid in all_skills_map]
    if not current_skills_objs:
        current_skills_objs = list(all_skills_map.values())[:1]

    template_idx = 0
    loop_guard = 0
    while len(questions_to_add) < target_current_count and loop_guard < 50:
        loop_guard += 1
        skill_obj = current_skills_objs[template_idx % len(current_skills_objs)]
        tmpl = PROGRESSIVE_QUESTION_TEMPLATES[template_idx % len(PROGRESSIVE_QUESTION_TEMPLATES)]
        template_idx += 1
        
        sname = skill_obj.name
        scat = skill_obj.category or "Engineering"
        
        q_text = tmpl["question"].format(
            skill_name=sname,
            target_role=target_role,
            category=scat
        )
        
        if q_text in seen_question_texts:
            continue
            
        correct_opt = tmpl["correct_desc"].format(
            skill_name=sname,
            category=scat
        )
        distractors = [d.format(skill_name=sname, category=scat) for d in tmpl["distractors"]]
        raw_options = [correct_opt] + distractors
        
        seed = hash(q_text) + template_idx + len(questions_to_add) * 31
        q_obj = prepare_and_validate_question(
            raw_text=q_text,
            raw_options=raw_options,
            raw_correct_idx=0,
            skill_id=skill_obj.id,
            difficulty=tmpl["tier"],
            explanation=f"{sname} is essential within {scat} architectures.",
            seed_val=seed
        )
        if q_obj:
            questions_to_add.append(q_obj)
            seen_question_texts.add(q_text)

    # Step D: Deterministically generate remaining Past Prerequisite Questions
    if past_skill_ids and len(questions_to_add) < 10:
        past_skills_objs = [all_skills_map[sid] for sid in past_skill_ids if sid in all_skills_map]
        p_template_idx = 0
        p_loop_guard = 0
        while len(questions_to_add) < 10 and past_skills_objs and p_loop_guard < 30:
            p_loop_guard += 1
            skill_obj = past_skills_objs[p_template_idx % len(past_skills_objs)]
            tmpl = PROGRESSIVE_QUESTION_TEMPLATES[p_template_idx % len(PROGRESSIVE_QUESTION_TEMPLATES)]
            p_template_idx += 1
            
            sname = skill_obj.name
            scat = skill_obj.category or "Engineering"
            
            q_text = tmpl["question"].format(
                skill_name=sname,
                target_role=target_role,
                category=scat
            )
            
            if q_text in seen_question_texts:
                continue
                
            correct_opt = tmpl["correct_desc"].format(
                skill_name=sname,
                category=scat
            )
            distractors = [d.format(skill_name=sname, category=scat) for d in tmpl["distractors"]]
            raw_options = [correct_opt] + distractors
            
            seed = hash(q_text) + p_template_idx + len(questions_to_add) * 43
            q_obj = prepare_and_validate_question(
                raw_text=q_text,
                raw_options=raw_options,
                raw_correct_idx=0,
                skill_id=skill_obj.id,
                difficulty=tmpl["tier"],
                explanation=f"{sname} provides foundational prerequisite understanding for subsequent milestones.",
                seed_val=seed
            )
            if q_obj:
                questions_to_add.append(q_obj)
                seen_question_texts.add(q_text)

    # Step E: Fill up to 10 questions with balanced variations
    e_loop_guard = 0
    while len(questions_to_add) < 10 and e_loop_guard < 40:
        e_loop_guard += 1
        skill_obj = current_skills_objs[template_idx % len(current_skills_objs)]
        tmpl = PROGRESSIVE_QUESTION_TEMPLATES[template_idx % len(PROGRESSIVE_QUESTION_TEMPLATES)]
        template_idx += 1
        
        sname = skill_obj.name
        scat = skill_obj.category or "Engineering"
        
        q_text = f"Regarding {sname} ({tmpl['style']}): " + tmpl["question"].format(
            skill_name=sname,
            target_role=target_role,
            category=scat
        )
        
        if q_text in seen_question_texts:
            continue
            
        correct_opt = tmpl["correct_desc"].format(
            skill_name=sname,
            category=scat
        )
        distractors = [d.format(skill_name=sname, category=scat) for d in tmpl["distractors"]]
        raw_options = [correct_opt] + distractors
        
        seed = hash(q_text) + template_idx + len(questions_to_add) * 59
        q_obj = prepare_and_validate_question(
            raw_text=q_text,
            raw_options=raw_options,
            raw_correct_idx=0,
            skill_id=skill_obj.id,
            difficulty=tmpl["tier"],
            explanation=f"Validated technical concept for {sname}.",
            seed_val=seed,
            allow_relaxed=True
        )
        if q_obj:
            questions_to_add.append(q_obj)
            seen_question_texts.add(q_text)

    # Commit all validated questions
    for q in questions_to_add[:12]:
        db.add(q)
    db.commit()
    db.refresh(assessment)
    
    return assessment

def submit_assessment(db: Session, learner_id: int, assessment_id: int, answers: Dict[str, Any]):
    """Grade assessment submission, compute detailed skill proficiency impact, and trigger roadmap adaptation."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
    
    correct = 0
    skill_scores = {}
    skill_counts = {}
    question_explanations = []
    
    for q in questions:
        ans = answers.get(str(q.id))
        is_correct = False
        
        if ans is not None:
            # 1. Integer option index match
            try:
                if int(ans) == q.correct_answer_index:
                    is_correct = True
            except (ValueError, TypeError):
                pass
            
            # 2. String option text match
            if not is_correct and isinstance(ans, str) and q.options:
                if 0 <= q.correct_answer_index < len(q.options):
                    if ans.strip() == q.options[q.correct_answer_index].strip():
                        is_correct = True

        if is_correct:
            correct += 1
            
        sid = str(q.skill_id)
        if sid not in skill_scores:
            skill_scores[sid] = 0
            skill_counts[sid] = 0
            
        if is_correct:
            skill_scores[sid] += 1
        skill_counts[sid] += 1

        correct_opt_text = q.options[q.correct_answer_index] if (q.options and 0 <= q.correct_answer_index < len(q.options)) else "Correct Option"
        question_explanations.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "correct": is_correct,
            "correct_answer": correct_opt_text,
            "explanation": q.explanation or "Validated technical concept."
        })
        
    score = (correct / max(1, len(questions))) * 100
    
    for sid in skill_scores:
        skill_scores[sid] = (skill_scores[sid] / max(1, skill_counts[sid])) * 100
        
    attempt = AssessmentAttempt(
        assessment_id=assessment_id,
        learner_id=learner_id,
        answers=answers,
        score=score,
        skill_scores=skill_scores
    )
    
    db.add(attempt)
    assessment.status = "completed"
    db.commit()
    db.refresh(attempt)
    
    # Trigger adaptation
    from .adaptation_service import adapt_after_assessment
    adaptation_result = adapt_after_assessment(db, learner_id, attempt)
    
    # Build skill breakdown with real names
    skill_breakdown = {}
    for sid_str, sc in skill_scores.items():
        skill = db.query(Skill).filter(Skill.id == int(sid_str)).first()
        name = skill.name if skill else f"Skill {sid_str}"
        skill_breakdown[name] = round(sc, 1)
    
    return {
        "score": round(score, 1),
        "total_questions": len(questions),
        "correct_answers": correct,
        "skill_scores": skill_scores,
        "skill_breakdown": skill_breakdown,
        "explanations": question_explanations,
        "adaptations": adaptation_result.get("actions", [])
    }
