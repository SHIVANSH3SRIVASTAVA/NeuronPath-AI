export interface Learner {
  id: number;
  name: string;
  email?: string;
  experience_level: 'beginner' | 'intermediate' | 'advanced';
  weekly_hours: number;
  learning_style?: string;
  preferred_formats: string[];
  created_at: string;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  description: string;
}

export interface LearnerSkill {
  id: number;
  learner_id: number;
  skill_id: number;
  skill: Skill;
  self_reported_level: number;
  demonstrated_level: number | null;
  system_confidence: number;
}

export interface SkillGap {
  skill: Skill;
  current_level: number;
  required_level: number;
  gap: number;
  priority: number;
  priority_label: 'critical' | 'high' | 'medium' | 'low';
  prerequisites_met: boolean;
}

export interface Resource {
  id: number;
  title: string;
  type: string;
  provider: string;
  url?: string;
  difficulty: string;
  duration_hours: number;
  quality_score: number;
  description: string;
  skill_ids: number[];
}

export interface LearnerGoal {
  id: number;
  learner_id: number;
  title: string;
  target_role: string;
  timeline_months: number;
  status: string;
}

export interface RoadmapMilestone {
  id: number;
  roadmap_id: number;
  order_index: number;
  title: string;
  objective: string;
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  estimated_hours: number;
  skill_ids: number[];
  skills?: Skill[];
  completion_criteria: string;
  items: MilestoneItem[];
}

export interface MilestoneItem {
  id: number;
  milestone_id: number;
  resource_id?: number;
  project_id?: number;
  item_type: 'resource' | 'project' | 'assessment';
  status: 'not_started' | 'in_progress' | 'completed';
  resource?: Resource;
  project?: Project;
}

export interface Roadmap {
  id: number;
  learner_id: number;
  goal_id: number;
  status: string;
  milestones: RoadmapMilestone[];
  goal?: LearnerGoal;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  skill_ids: number[];
  estimated_hours: number;
}

export interface Assessment {
  id: number;
  learner_id: number;
  title: string;
  skill_ids: number[];
  status: string;
  questions: AssessmentQuestion[];
}

export interface AssessmentQuestion {
  id: number;
  skill_id: number;
  question_text: string;
  options: string[];
  difficulty: string;
}

export interface AssessmentResult {
  score: number;
  total_questions: number;
  correct_answers: number;
  skill_scores: Record<string, number>;
  explanations: Array<{
    question_id: number;
    correct: boolean;
    correct_answer: string;
    explanation: string;
  }>;
  adaptation_actions: string[];
}

export interface Recommendation {
  id: number;
  resource: Resource;
  score: number;
  score_breakdown: Record<string, number>;
  explanation: string;
}

export interface NextAction {
  action: string;
  description: string;
  type: 'resource' | 'assessment' | 'project' | 'milestone';
  milestone_title?: string;
  resource_id?: number;
  assessment_id?: number;
}

export interface CategorizedSkillItem {
  skill_id: number;
  name: string;
  category: string;
  proficiency: number;
  demonstrated: number | null;
  self_reported: number | null;
}

export interface ProgressionPoint {
  id: string;
  label: string;
  title: string;
  order_index: number;
  status: 'completed' | 'in_progress' | 'available' | 'locked';
  progress: number;
  target_progress: number;
  mastery: number;
  assessment_score: number | null;
  completed_items: number;
  total_items: number;
  estimated_hours?: number;
  date?: string;
  is_current?: boolean;
}

export interface AssessmentHistoryItem {
  id: number;
  score: number;
  date: string;
  skill_scores?: Record<string, number>;
}

export interface ProgressData {
  overall_progress: number;
  milestones_completed: number;
  milestones_total: number;
  skills_mastered: number;
  skills_developing: number;
  skills_weak: number;
  skills_missing: number;
  categorized_skills?: {
    mastered: CategorizedSkillItem[];
    developing: CategorizedSkillItem[];
    weak: CategorizedSkillItem[];
    missing: CategorizedSkillItem[];
  };
  total_learning_hours: number;
  assessments_taken: number;
  average_score: number;
  current_mastery?: number;
  baseline_mastery?: number;
  mastery_growth?: number;
  velocity_status?: string;
  velocity_badge?: string;
  current_milestone_title?: string;
  progression_timeline?: ProgressionPoint[];
  assessment_history?: AssessmentHistoryItem[];
  skill_growth: Array<{ skill: string; before: number; after: number }>;
  recent_activity: Array<{ type: string; description: string; date: string }>;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  created_at?: string;
}

export interface OnboardingResult {
  goal: string;
  target_role: string;
  experience_level: string;
  known_skills: string[];
  weekly_hours: number;
  timeline_months: number;
  learning_style?: string;
  preferred_formats?: string[];
}

export interface AuthResponse {
  status: string;
  access_token: string;
  token_type: string;
  learner: Learner;
}

export interface LoginCredentials {
  email: string;
  password?: string;
}

export interface RegisterCredentials {
  name: string;
  email: string;
  password?: string;
}

