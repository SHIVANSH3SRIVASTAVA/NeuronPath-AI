import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SkillGap } from '../../types';
import { Button } from '../ui/Button';
import { BookOpen, Target, ArrowRight } from 'lucide-react';

interface SkillDetailProps {
  gap: SkillGap;
  onFindResources?: (skillName: string, skillId: number) => void;
}

export function SkillDetail({ gap, onFindResources }: SkillDetailProps) {
  const navigate = useNavigate();

  const handleFindResources = () => {
    if (onFindResources) {
      onFindResources(gap.skill.name, gap.skill.id);
    } else {
      navigate(`/resources?skill=${encodeURIComponent(gap.skill.name)}&skillId=${gap.skill.id}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <span className="text-[11px] font-bold uppercase tracking-wider text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-primary-950/70 px-2.5 py-0.5 rounded-md border border-primary-100 dark:border-primary-800">
            {gap.skill.category || 'Core Skill'}
          </span>
          <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full capitalize ${
            gap.priority_label === 'critical'
              ? 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800'
              : gap.priority_label === 'high'
              ? 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
              : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
          }`}>
            {gap.priority_label} Priority
          </span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{gap.skill.name}</h2>
        <p className="text-slate-700 dark:text-slate-300 text-sm mt-1.5 leading-relaxed">
          {gap.skill.description || `Mastery of ${gap.skill.name} is essential for achieving proficiency in your target role.`}
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1">Current Proficiency</p>
          <p className="text-2xl font-black text-slate-900 dark:text-white">{Math.round(gap.current_level)}%</p>
          <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full mt-2.5 overflow-hidden">
            <div className="bg-slate-700 dark:bg-slate-300 h-full rounded-full" style={{ width: `${Math.min(100, Math.max(5, gap.current_level))}%` }} />
          </div>
        </div>

        <div className="bg-primary-50 dark:bg-primary-950/60 p-4 rounded-xl border border-primary-200 dark:border-primary-800">
          <p className="text-xs font-bold text-primary-800 dark:text-primary-300 uppercase tracking-wider mb-1">Target Proficiency</p>
          <p className="text-2xl font-black text-primary-900 dark:text-primary-200">{Math.round(gap.required_level)}%</p>
          <div className="w-full bg-primary-200 dark:bg-primary-800 h-2 rounded-full mt-2.5 overflow-hidden">
            <div className="bg-primary-600 dark:bg-primary-400 h-full rounded-full" style={{ width: `${Math.min(100, gap.required_level)}%` }} />
          </div>
        </div>
      </div>

      <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
        <h4 className="font-bold text-xs uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
          <Target className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Gap Analysis & Readiness
        </h4>
        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-normal">
          Skill proficiency gap: <strong className="text-slate-900 dark:text-white">{Math.round(gap.gap)}%</strong>. {gap.prerequisites_met 
            ? 'All prerequisite foundations are met. You are fully ready to engage with learning resources for this skill.' 
            : 'Consider reviewing foundational prerequisites first.'}
        </p>
      </div>

      <div>
        <Button 
          onClick={handleFindResources} 
          className="w-full font-bold shadow-xs flex items-center justify-center gap-2 cursor-pointer"
          size="lg"
        >
          <BookOpen className="w-4 h-4" />
          <span>Find Resources for {gap.skill.name}</span>
          <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}
