import React from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { ProgressData } from '../../types';
import { Activity } from 'lucide-react';

export function RecentActivity({ data }: { data: ProgressData }) {
  if (!data || !data.recent_activity || data.recent_activity.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Recent Activity
          </h2>
        </CardHeader>
        <CardContent className="p-6 text-center text-xs text-slate-500 dark:text-slate-400">
          No recent learning activity recorded yet.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Recent Activity
        </h2>
      </CardHeader>
      <CardContent className="space-y-3.5 p-6">
        {data.recent_activity.slice(0, 5).map((item, i) => (
          <div key={i} className="flex flex-col border-l-2 border-primary-500 dark:border-primary-600 pl-3.5 py-0.5">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 mb-0.5">
              {item.date ? new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Recent'}
            </span>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-snug">{item.description}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
