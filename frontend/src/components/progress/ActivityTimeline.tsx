import React from 'react';
import { Activity } from 'lucide-react';

interface ActivityTimelineProps {
  activities?: Array<{ date: string; description: string }>;
}

export function ActivityTimeline({ activities = [] }: ActivityTimelineProps) {
  if (!activities || activities.length === 0) {
    return (
      <div className="space-y-4 text-center py-6">
        <p className="text-sm text-slate-500 dark:text-slate-400">No recent learning activity recorded.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((item, idx) => (
        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 transition-colors">
          <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-950 text-primary-700 dark:text-primary-300 mt-0.5 shrink-0">
            <Activity className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 mb-0.5">
              {item.date ? new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recent'}
            </p>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              {item.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
