import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { OnboardingResult } from '../../types';
import { Edit3, Check, X, Plus, Sparkles } from 'lucide-react';

const AVAILABLE_SKILLS = [
  "Python Basics", "Python Intermediate", "Python Advanced", "SQL Fundamentals", "SQL Advanced",
  "Git & Version Control", "Linux Command Line", "Linear Algebra", "Calculus", "Probability",
  "Descriptive Statistics", "Inferential Statistics", "NumPy", "Pandas", "Data Visualization",
  "Data Cleaning", "Exploratory Data Analysis", "ML Fundamentals", "Linear Regression",
  "Logistic Regression", "Decision Trees & Random Forests", "Model Evaluation", "Feature Engineering",
  "Clustering", "Dimensionality Reduction", "Gradient Boosting", "Neural Networks Basics",
  "Deep Learning with PyTorch", "CNNs", "NLP Fundamentals", "Model Deployment", "Docker Basics",
  "Experiment Tracking", "Technical Communication", "Problem Formulation", "JavaScript Essentials",
  "TypeScript Fundamentals", "React & State Management", "Java Fundamentals", "Spring Boot & Enterprise Java",
  "Go Fundamentals", "Rust Syntax & Ownership", "Kubernetes Orchestration", "AWS Cloud Foundations"
];

interface ProfileConfirmationProps {
  profile: OnboardingResult & { name?: string };
  onConfirm: (finalProfile?: OnboardingResult & { name?: string }) => void;
  onUpdate?: (updated: OnboardingResult & { name?: string }) => void;
}

export function ProfileConfirmation({ profile, onConfirm, onUpdate }: ProfileConfirmationProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(profile.name || 'Learner');
  const [goal, setGoal] = useState(profile.goal || '');
  const [targetRole, setTargetRole] = useState(profile.target_role || '');
  const [experienceLevel, setExperienceLevel] = useState(profile.experience_level || 'beginner');
  const [weeklyHours, setWeeklyHours] = useState(profile.weekly_hours || 10);
  const [timelineMonths, setTimelineMonths] = useState(profile.timeline_months || 6);
  const [knownSkills, setKnownSkills] = useState<string[]>(profile.known_skills || []);
  const [newSkillInput, setNewSkillInput] = useState('');

  const handleAddSkill = (skillToAdd?: string) => {
    const skill = (skillToAdd || newSkillInput).trim();
    if (skill && !knownSkills.includes(skill)) {
      setKnownSkills([...knownSkills, skill]);
      setNewSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setKnownSkills(knownSkills.filter(s => s !== skillToRemove));
  };

  const handleSaveEdit = () => {
    const updated: OnboardingResult & { name?: string } = {
      ...profile,
      name,
      goal,
      target_role: targetRole,
      experience_level: experienceLevel as any,
      weekly_hours: Number(weeklyHours),
      timeline_months: Number(timelineMonths),
      known_skills: knownSkills
    };
    if (onUpdate) onUpdate(updated);
    setIsEditing(false);
  };

  const handleProceed = () => {
    const currentData: OnboardingResult & { name?: string } = {
      ...profile,
      name,
      goal,
      target_role: targetRole,
      experience_level: experienceLevel as any,
      weekly_hours: Number(weeklyHours),
      timeline_months: Number(timelineMonths),
      known_skills: knownSkills
    };
    onConfirm(currentData);
  };

  return (
    <Card className="max-w-2xl mx-auto border-slate-200 dark:border-slate-800 shadow-md bg-white dark:bg-slate-900">
      <CardHeader className="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-slate-900 dark:to-slate-800 border-b border-primary-100 dark:border-slate-800 flex flex-row items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            {isEditing ? "Edit Your Learning Profile" : "Here's what I understood"}
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5">
            {isEditing ? "Customize your target role, timeline, and known skills." : "Review or adjust these details to generate your tailored roadmap."}
          </p>
        </div>
        {!isEditing && (
          <Button variant="outline" size="sm" onClick={() => setIsEditing(true)} className="flex items-center gap-1">
            <Edit3 className="w-4 h-4" /> Edit Manually
          </Button>
        )}
      </CardHeader>

      <CardContent className="space-y-4 pt-6 p-6">
        {isEditing ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Your Name</label>
                <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Jane Doe" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Goal Title</label>
                <Input value={goal} onChange={e => setGoal(e.target.value)} placeholder="e.g. Master SQL & Database Systems" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Target Professional Role</label>
                <Input value={targetRole} onChange={e => setTargetRole(e.target.value)} placeholder="e.g. SQL Developer, Data Analyst" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Experience Level</label>
                <select
                  value={experienceLevel}
                  onChange={e => setExperienceLevel(e.target.value)}
                  className="w-full p-2 text-sm border border-slate-300 dark:border-slate-700 rounded-md focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                >
                  <option value="beginner">Beginner (Starting from scratch)</option>
                  <option value="intermediate">Intermediate (Some prior coding/math)</option>
                  <option value="advanced">Advanced (Experienced practitioner)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Weekly Commitment (Hours)</label>
                <Input type="number" min="1" max="80" value={weeklyHours} onChange={e => setWeeklyHours(Number(e.target.value))} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Target Timeline (Months)</label>
                <Input type="number" min="1" max="24" value={timelineMonths} onChange={e => setTimelineMonths(Number(e.target.value))} />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1">Known Skills</label>
              <div className="flex flex-wrap gap-2 mb-2 p-2 border border-slate-200 dark:border-slate-700 rounded-md min-h-[44px] bg-slate-50 dark:bg-slate-800/80">
                {knownSkills.length === 0 && <span className="text-xs text-slate-500 dark:text-slate-400 self-center">No existing skills added yet.</span>}
                {knownSkills.map(s => (
                  <span key={s} className="inline-flex items-center gap-1 px-2.5 py-1 bg-primary-100 dark:bg-primary-950 text-primary-800 dark:text-primary-200 text-xs font-medium rounded-full border border-primary-200 dark:border-primary-800">
                    {s}
                    <button type="button" onClick={() => handleRemoveSkill(s)} className="text-primary-600 dark:text-primary-400 hover:text-red-600 dark:hover:text-red-400">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>

              <div className="flex gap-2">
                <select
                  onChange={e => {
                    if (e.target.value) {
                      handleAddSkill(e.target.value);
                      e.target.value = '';
                    }
                  }}
                  className="flex-1 p-2 text-xs border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  defaultValue=""
                >
                  <option value="" disabled>+ Select a skill from library...</option>
                  {AVAILABLE_SKILLS.filter(s => !knownSkills.includes(s)).map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                <Input
                  value={newSkillInput}
                  onChange={e => setNewSkillInput(e.target.value)}
                  placeholder="Or type custom skill"
                  className="text-xs max-w-[200px]"
                  onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkill(); } }}
                />
                <Button type="button" size="sm" variant="secondary" onClick={() => handleAddSkill()}>
                  <Plus className="w-4 h-4" /> Add
                </Button>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setIsEditing(false)}>Cancel</Button>
              <Button onClick={handleSaveEdit} className="flex items-center gap-1">
                <Check className="w-4 h-4" /> Save Profile Details
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Learner Name</span>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{name}</p>
              </div>
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Goal</span>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{goal}</p>
              </div>
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Target Role</span>
                <p className="font-bold text-primary-700 dark:text-primary-300 mt-0.5">{targetRole}</p>
              </div>
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Experience Level</span>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5 capitalize">{experienceLevel}</p>
              </div>
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Weekly Commitment</span>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{weeklyHours} hrs/week</p>
              </div>
              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Timeline</span>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{timelineMonths} months</p>
              </div>
              <div className="md:col-span-2 p-3.5 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1">Known Skills</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {knownSkills.length > 0 ? (
                    knownSkills.map(s => (
                      <span key={s} className="px-2.5 py-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-800 dark:text-slate-100 rounded-md shadow-2xs">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500 dark:text-slate-400 italic">None specified (we will start from foundations)</span>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setIsEditing(true)} className="flex items-center gap-1">
                <Edit3 className="w-4 h-4" /> Edit Manually
              </Button>
              <Button onClick={handleProceed} className="bg-primary-600 hover:bg-primary-700 text-white font-semibold">
                Looks Good, Build Roadmap
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
