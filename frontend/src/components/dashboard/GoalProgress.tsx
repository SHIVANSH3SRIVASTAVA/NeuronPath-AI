import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { Progress } from '../ui/Progress';

export function GoalProgress({ progress, goalTitle }: { progress: number, goalTitle?: string }) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Overall Track Progress</h3>
        <p className="text-lg font-bold text-slate-900 dark:text-white mb-4">{goalTitle || 'Your Learning Goal'}</p>
        <div className="flex items-center justify-between mb-2">
          <span className="text-3xl font-black text-primary-600 dark:text-primary-400">{Math.round(progress)}%</span>
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">Target: 100% Mastery</span>
        </div>
        <Progress value={progress} size="lg" />
      </CardContent>
    </Card>
  );
}
