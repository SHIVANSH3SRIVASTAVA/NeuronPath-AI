import React from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Roadmap } from '../../types';
import { CheckCircle, Circle, Lock, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export function RoadmapPreview({ roadmap }: { roadmap: Roadmap }) {
  if (!roadmap || !roadmap.milestones) return null;
  const topMilestones = roadmap.milestones.slice(0, 3);
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Milestone Roadmap Track</h2>
        <Link to="/roadmap" className="text-xs font-bold text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-1">
          View All <ArrowRight className="w-3 h-3" />
        </Link>
      </CardHeader>
      <CardContent className="space-y-3.5 p-6">
        {topMilestones.map((m, idx) => (
          <div key={m.id || idx} className="flex items-center gap-3.5 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors">
            {m.status === 'completed' ? (
              <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            ) : m.status === 'locked' ? (
              <Lock className="w-5 h-5 text-slate-400 dark:text-slate-500 shrink-0" />
            ) : (
              <Circle className="w-5 h-5 text-primary-600 dark:text-primary-400 shrink-0 animate-pulse" />
            )}
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-bold truncate ${m.status === 'locked' ? 'text-slate-500 dark:text-slate-400' : 'text-slate-900 dark:text-white'}`}>
                {m.title}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 font-medium">
                {m.estimated_hours} hrs • <span className="capitalize">{m.status.replace('_', ' ')}</span>
              </p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
