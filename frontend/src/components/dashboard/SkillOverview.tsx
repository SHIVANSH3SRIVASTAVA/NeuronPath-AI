import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '../ui/Card';
import { ProgressData, CategorizedSkillItem } from '../../types';
import { 
  X, 
  CheckCircle2, 
  TrendingUp, 
  AlertTriangle, 
  HelpCircle, 
  Layers, 
  ChevronRight,
  Sparkles
} from 'lucide-react';

type SkillCategory = 'mastered' | 'developing' | 'weak' | 'missing';

interface CategoryConfig {
  key: SkillCategory;
  label: string;
  count: number;
  color: string;
  textColor: string;
  badgeBg: string;
  bg: string;
  hoverBorder: string;
  progressBarColor: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

export function SkillOverview({ data }: { data: ProgressData }) {
  const [selectedCategory, setSelectedCategory] = useState<SkillCategory | null>(null);

  // Close modal on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedCategory(null);
      }
    };
    if (selectedCategory) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [selectedCategory]);

  const categories: Record<SkillCategory, CategoryConfig> = {
    mastered: {
      key: 'mastered',
      label: 'Mastered',
      count: data.skills_mastered,
      color: 'text-emerald-700 dark:text-emerald-300',
      textColor: 'text-emerald-900 dark:text-emerald-100',
      badgeBg: 'bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 border-emerald-300 dark:border-emerald-700',
      bg: 'bg-emerald-50/90 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900/80',
      hoverBorder: 'hover:border-emerald-400 dark:hover:border-emerald-600',
      progressBarColor: 'bg-emerald-500',
      icon: CheckCircle2,
      description: 'Skills with ≥ 80% confidence and verified mastery'
    },
    developing: {
      key: 'developing',
      label: 'Developing',
      count: data.skills_developing,
      color: 'text-primary-700 dark:text-primary-300',
      textColor: 'text-primary-900 dark:text-primary-100',
      badgeBg: 'bg-primary-100 dark:bg-primary-900/60 text-primary-800 dark:text-primary-200 border-primary-300 dark:border-primary-700',
      bg: 'bg-primary-50/90 dark:bg-primary-950/40 border-primary-200 dark:border-primary-900/80',
      hoverBorder: 'hover:border-primary-400 dark:hover:border-primary-600',
      progressBarColor: 'bg-primary-500',
      icon: TrendingUp,
      description: 'Skills in active learning progression (40% - 79% confidence)'
    },
    weak: {
      key: 'weak',
      label: 'Weak',
      count: data.skills_weak,
      color: 'text-amber-800 dark:text-amber-300',
      textColor: 'text-amber-900 dark:text-amber-100',
      badgeBg: 'bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 border-amber-300 dark:border-amber-700',
      bg: 'bg-amber-50/90 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900/80',
      hoverBorder: 'hover:border-amber-400 dark:hover:border-amber-600',
      progressBarColor: 'bg-amber-500',
      icon: AlertTriangle,
      description: 'Skills with foundational gaps requiring targeted practice (10% - 39%)'
    },
    missing: {
      key: 'missing',
      label: 'Missing',
      count: data.skills_missing,
      color: 'text-rose-700 dark:text-rose-300',
      textColor: 'text-rose-900 dark:text-rose-100',
      badgeBg: 'bg-rose-100 dark:bg-rose-900/60 text-rose-800 dark:text-rose-200 border-rose-300 dark:border-rose-700',
      bg: 'bg-rose-50/90 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900/80',
      hoverBorder: 'hover:border-rose-400 dark:hover:border-rose-600',
      progressBarColor: 'bg-rose-500',
      icon: HelpCircle,
      description: 'Prerequisites & core goal skills not yet started (< 10% confidence)'
    }
  };

  // Get active skills list dynamically for selected category
  const getSkillsForCategory = (cat: SkillCategory): CategorizedSkillItem[] => {
    if (data.categorized_skills && data.categorized_skills[cat]) {
      return data.categorized_skills[cat];
    }
    return [];
  };

  const activeConfig = selectedCategory ? categories[selectedCategory] : null;
  const activeSkills = selectedCategory ? getSkillsForCategory(selectedCategory) : [];

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Skill Proficiency Overview</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Click any category to inspect skill breakdown</p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700 flex items-center gap-1">
            <Layers className="w-3 h-3" />
            {data.skills_mastered + data.skills_developing + data.skills_weak + data.skills_missing} Total
          </span>
        </CardHeader>
        <CardContent className="p-6 pt-3">
          <div className="grid grid-cols-2 gap-3.5">
            {(Object.keys(categories) as SkillCategory[]).map(key => {
              const s = categories[key];
              const Icon = s.icon;
              return (
                <button
                  key={s.label}
                  type="button"
                  onClick={() => setSelectedCategory(key)}
                  aria-label={`View ${s.label} skills (${s.count})`}
                  className={`p-4 rounded-xl ${s.bg} border ${s.hoverBorder} transition-all duration-150 text-left group cursor-pointer hover:shadow-md hover:scale-[1.02] active:scale-[0.99] focus:outline-none focus:ring-2 focus:ring-primary-500/50 relative overflow-hidden`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Icon className="w-3.5 h-3.5 opacity-80" />
                      {s.label}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-400 dark:text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-0.5" />
                  </div>
                  <div className="flex items-baseline justify-between mt-1.5">
                    <p className={`text-2xl font-black ${s.color}`}>{s.count}</p>
                    <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 opacity-80 group-hover:opacity-100">
                      View list →
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Glassmorphism Category Skills Modal */}
      {selectedCategory && activeConfig && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-150"
          onClick={() => setSelectedCategory(null)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="category-modal-title"
        >
          <div 
            className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-200/90 dark:border-slate-800/90 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-150"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/50">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-xl border ${activeConfig.badgeBg}`}>
                  <activeConfig.icon className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 id="category-modal-title" className="text-lg font-bold text-slate-900 dark:text-slate-100">
                      {activeConfig.label} Skills
                    </h3>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${activeConfig.badgeBg}`}>
                      {activeSkills.length}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {activeConfig.description}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCategory(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body - Skill List */}
            <div className="p-5 overflow-y-auto space-y-3 max-h-[55vh]">
              {activeSkills.length > 0 ? (
                activeSkills.map(skill => (
                  <div 
                    key={skill.skill_id}
                    className="p-3.5 rounded-xl border border-slate-200/90 dark:border-slate-800/90 bg-slate-50/50 dark:bg-slate-850/50 hover:bg-slate-100/60 dark:hover:bg-slate-800/60 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="pr-2">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                          {skill.name}
                        </h4>
                        <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                          {skill.category}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className={`text-sm font-black ${activeConfig.color}`}>
                          {skill.proficiency}%
                        </span>
                        <p className="text-[10px] text-slate-400 dark:text-slate-500">
                          {skill.demonstrated !== null ? 'Demonstrated' : skill.self_reported !== null ? 'Self-reported' : 'Confidence'}
                        </p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${activeConfig.progressBarColor} rounded-full transition-all duration-300`}
                        style={{ width: `${Math.min(100, Math.max(4, skill.proficiency))}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-10 text-center px-4">
                  <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 flex items-center justify-center mx-auto mb-3">
                    <activeConfig.icon className="w-6 h-6 opacity-60" />
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    No skills in this category
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs mx-auto">
                    {selectedCategory === 'mastered'
                      ? 'Complete milestones and pass assessments with ≥ 80% to master skills.'
                      : selectedCategory === 'developing'
                      ? 'Start learning resources in active milestones to begin developing skills.'
                      : selectedCategory === 'weak'
                      ? 'No critical weak skill gaps identified in your active learning roadmap.'
                      : 'All required skills for your current goal have been initiated or mastered! 🎉'}
                  </p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-primary-500" />
                Adaptive Skill Matrix
              </span>
              <button
                type="button"
                onClick={() => setSelectedCategory(null)}
                className="px-4 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 rounded-lg font-bold hover:bg-slate-800 dark:hover:bg-white transition-colors text-xs focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
