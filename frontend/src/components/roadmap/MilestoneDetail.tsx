import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RoadmapMilestone, MilestoneItem } from '../../types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { PlayCircle, CheckCircle2, Lock, Clock, Target, BookOpen, ExternalLink, Award, Code } from 'lucide-react';

interface MilestoneDetailProps {
  milestone: RoadmapMilestone;
  onStart: () => void;
  onCompleteItem: (id: number) => void;
  starting?: boolean;
}

export function MilestoneDetail({ 
  milestone, 
  onStart, 
  onCompleteItem,
  starting = false 
}: MilestoneDetailProps) {
  const navigate = useNavigate();
  const isAvailable = milestone.status === 'available';
  const isInProgress = milestone.status === 'in_progress';
  const isCompleted = milestone.status === 'completed';
  const isLocked = milestone.status === 'locked';

  const handleTaskClick = (item: MilestoneItem, resourceTitle: string) => {
    if (isLocked) return;

    if (item.item_type === 'assessment') {
      navigate('/assessment');
      return;
    }

    const resourceId = item.resource_id || item.resource?.id;
    if (resourceId && resourceTitle) {
      navigate(`/resources?id=${resourceId}&search=${encodeURIComponent(resourceTitle)}`);
    } else if (resourceId) {
      navigate(`/resources?id=${resourceId}`);
    } else if (resourceTitle) {
      navigate(`/resources?search=${encodeURIComponent(resourceTitle)}`);
    } else {
      navigate('/resources');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between gap-3 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Step {milestone.order_index + 1}
          </span>
          <Badge 
            variant={
              isCompleted 
                ? 'success' 
                : isInProgress 
                ? 'primary' 
                : isAvailable 
                ? 'default' 
                : 'secondary'
            }
          >
            {isCompleted ? 'Completed' : isInProgress ? 'In Progress' : isAvailable ? 'Available' : 'Locked'}
          </Badge>
        </div>

        <h3 className="text-xl font-bold text-slate-900 dark:text-white">{milestone.title}</h3>
        <p className="text-slate-700 dark:text-slate-300 text-sm mt-1.5 leading-relaxed">{milestone.objective}</p>
        
        <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400 mt-3 pt-3 border-t border-slate-200 dark:border-slate-800">
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            {milestone.estimated_hours || 10} hours estimated
          </span>
          <span className="flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            {milestone.completion_criteria || 'Complete all tasks & assessment'}
          </span>
        </div>
      </div>
      
      {isAvailable && (
        <div className="bg-primary-50 dark:bg-primary-950/60 p-4 rounded-xl border border-primary-200 dark:border-primary-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-primary-900 dark:text-primary-200">
            <p className="font-bold">Ready to begin this milestone?</p>
            <p className="text-primary-700 dark:text-primary-400 mt-0.5">Starting will activate your learning module.</p>
          </div>
          <Button 
            onClick={onStart} 
            disabled={starting}
            className="w-full sm:w-auto font-bold shrink-0 cursor-pointer"
          >
            <PlayCircle className="w-4 h-4 mr-1.5" />
            {starting ? 'Starting Milestone...' : 'Start Milestone'}
          </Button>
        </div>
      )}

      {isInProgress && (
        <div className="bg-emerald-50 dark:bg-emerald-950/50 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-800 flex items-center gap-2.5 text-xs text-emerald-900 dark:text-emerald-300 font-semibold">
          <PlayCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>This milestone is currently active! Complete all learning tasks below to achieve full milestone completion.</span>
        </div>
      )}

      {isCompleted && (
        <div className="bg-emerald-50 dark:bg-emerald-950/50 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-800 flex items-center gap-2.5 text-xs text-emerald-900 dark:text-emerald-300 font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>Milestone completed! All tasks have been mastered and dependent milestones unlocked.</span>
        </div>
      )}

      {isLocked && (
        <div className="bg-slate-50 dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center gap-2.5 text-xs text-slate-700 dark:text-slate-300">
          <Lock className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" />
          <span>This milestone is locked. Complete all tasks in the prerequisite milestone to unlock this section.</span>
        </div>
      )}

      <div>
        <h4 className="font-bold text-sm text-slate-900 dark:text-white mb-3 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Milestone Learning Tasks
        </h4>
        <div className="space-y-2.5">
          {milestone.items?.map((item, idx) => {
            const isItemDone = item.status === 'completed';
            const resourceTitle = item.resource?.title || item.project?.title || (item.item_type === 'assessment' ? 'Milestone Assessment' : `Learning Module ${idx + 1}`);
            const isAssessment = item.item_type === 'assessment';
            const isProject = item.item_type === 'project';
            
            return (
              <div 
                key={item.id} 
                className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                  isLocked
                    ? 'bg-slate-100/60 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 opacity-60'
                    : isItemDone 
                    ? 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 opacity-80' 
                    : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 shadow-2xs'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0 flex-1 mr-3">
                  <div className={`p-1.5 rounded-lg shrink-0 ${
                    isLocked
                      ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-500'
                      : isItemDone 
                      ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300' 
                      : isAssessment
                      ? 'bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400'
                      : isProject
                      ? 'bg-cyan-50 dark:bg-cyan-950 text-cyan-600 dark:text-cyan-400'
                      : 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400'
                  }`}>
                    {isLocked ? (
                      <Lock className="w-4 h-4" />
                    ) : isItemDone ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : isAssessment ? (
                      <Award className="w-4 h-4" />
                    ) : isProject ? (
                      <Code className="w-4 h-4" />
                    ) : (
                      <BookOpen className="w-4 h-4" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
                      {item.item_type}
                    </span>
                    {isLocked ? (
                      <p className="text-sm font-bold truncate text-slate-500 dark:text-slate-400">
                        {resourceTitle}
                      </p>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleTaskClick(item, resourceTitle)}
                        className="group/title text-sm font-bold truncate text-left text-slate-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 focus:text-primary-600 dark:focus:text-primary-400 hover:underline focus:underline focus:outline-none transition-colors inline-flex items-center gap-1.5 max-w-full cursor-pointer"
                        title={isAssessment ? 'Take Milestone Assessment' : `View "${resourceTitle}" in Resources`}
                      >
                        <span className="truncate">{resourceTitle}</span>
                        <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover/title:opacity-100 group-focus/title:opacity-100 transition-opacity text-primary-500 shrink-0" />
                      </button>
                    )}
                  </div>
                </div>

                <Button 
                  variant={isItemDone ? 'ghost' : isLocked ? 'secondary' : 'outline'} 
                  size="sm"
                  onClick={() => onCompleteItem(item.id)}
                  disabled={isItemDone || isLocked}
                  className="shrink-0"
                >
                  {isItemDone ? 'Completed' : isLocked ? 'Locked' : 'Mark Complete'}
                </Button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
