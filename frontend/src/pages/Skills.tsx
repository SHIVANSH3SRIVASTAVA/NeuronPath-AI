import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { getSkillGaps } from '../api/skills';
import { SkillCard } from '../components/skills/SkillCard';
import { SkillDetail } from '../components/skills/SkillDetail';
import { Modal } from '../components/ui/Modal';
import { SkillGap } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import { Brain, Sparkles } from 'lucide-react';

export default function Skills() {
  const { currentLearner, activeGoalVersion, activeGoal } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [selectedGap, setSelectedGap] = useState<SkillGap | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    getSkillGaps(currentLearner.id, activeGoal?.id)
      .then(res => {
        const mappedGaps: SkillGap[] = res.map((r: any) => ({
          skill: {
            id: r.skill_id,
            name: r.skill_name,
            category: r.category || 'Technical',
            description: r.description || ''
          },
          current_level: r.current_proficiency || r.current || 0,
          required_level: r.required_proficiency || r.required || 80,
          gap: r.gap || 0,
          priority: r.priority || 0,
          priority_label: (r.priority >= 50 || r.gap >= 60) ? 'critical' : (r.priority >= 25 || r.gap >= 35) ? 'high' : 'medium',
          prerequisites_met: true
        }));
        setGaps(mappedGaps);
      })
      .catch(err => {
        console.error('Skill gaps fetch error:', err);
        setError('Failed to load skill gaps.');
      })
      .finally(() => setLoading(false));
  }, [currentLearner, activeGoalVersion, activeGoal?.id]);

  if (!currentLearner) {
    return <div className="p-8 text-center text-slate-600 dark:text-slate-400">Please complete onboarding to view your skills map.</div>;
  }

  if (loading) {
    return (
      <div className="space-y-6 pb-12 max-w-6xl mx-auto">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-6 w-1/2" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
          <Skeleton className="h-44 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <Brain className="w-7 h-7 text-primary-600 dark:text-primary-400" /> Your Skills & Gap Analysis
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Detailed breakdown of required proficiencies versus your current demonstrated levels.
        </p>
      </div>
      
      {error && <div className="text-red-600 dark:text-red-300 bg-red-50 dark:bg-red-950/50 p-4 rounded-xl border border-red-200 dark:border-red-900 text-sm">{error}</div>}

      {gaps.length === 0 && !error ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
          <Sparkles className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
          <h3 className="font-bold text-slate-900 dark:text-slate-100 mb-1">No Skill Gaps Detected!</h3>
          <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
            You've achieved the target proficiencies for all required skills in your current goal track.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gaps.map((gap, idx) => (
            <SkillCard key={gap.skill.id || idx} gap={gap} onClick={() => setSelectedGap(gap)} />
          ))}
        </div>
      )}

      <Modal isOpen={!!selectedGap} onClose={() => setSelectedGap(null)} title="Skill Details & Learning Objectives">
        {selectedGap && <SkillDetail gap={selectedGap} />}
      </Modal>
    </div>
  );
}
