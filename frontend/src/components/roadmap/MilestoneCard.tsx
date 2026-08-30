import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { RoadmapMilestone } from '../../types';
import { CheckCircle, Lock, PlayCircle, Clock } from 'lucide-react';
import { Badge } from '../ui/Badge';

export function MilestoneCard({ milestone, onClick }: { milestone: RoadmapMilestone; onClick: () => void }) {
  const statusColors = {
    completed: 'text-emerald-500 border-emerald-500 bg-white dark:bg-slate-900',
    in_progress: 'text-primary-500 border-primary-500 bg-white dark:bg-slate-900',
    available: 'text-slate-600 dark:text-slate-400 border-slate-400 dark:border-slate-600 bg-white dark:bg-slate-900',
    locked: 'text-slate-300 dark:text-slate-600 border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900'
  };

  return (
    <div className="relative pl-8 cursor-pointer group" onClick={onClick}>
      <div className={`absolute -left-[11px] top-4 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${statusColors[milestone.status]}`}>
        {milestone.status === 'completed' && <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />}
        {milestone.status === 'in_progress' && <PlayCircle className="w-3.5 h-3.5 text-primary-500 animate-pulse" />}
        {milestone.status === 'locked' && <Lock className="w-3 h-3 text-slate-400 dark:text-slate-600" />}
      </div>
      <Card className="hover:border-primary-400 dark:hover:border-primary-600 hover:shadow-md transition-all">
        <CardContent className="p-5 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Step {milestone.order_index + 1}</span>
              <Badge variant={milestone.status === 'completed' ? 'success' : milestone.status === 'in_progress' ? 'primary' : 'default'}>
                {milestone.status.replace('_', ' ')}
              </Badge>
            </div>
            <h3 className={`text-lg font-bold transition-colors ${milestone.status === 'locked' ? 'text-slate-400 dark:text-slate-500' : 'text-slate-900 dark:text-slate-100'}`}>
              {milestone.title}
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 mt-0.5 leading-relaxed">
              {milestone.objective}
            </p>
          </div>
          <div className="text-right shrink-0">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 inline-flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" /> {milestone.estimated_hours}h
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
