import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { SkillGap } from '../../types';

export function SkillCard({ gap, onClick }: { gap: SkillGap; onClick: () => void }) {
  const priorityColors = {
    critical: 'error',
    high: 'warning',
    medium: 'primary',
    low: 'default'
  } as const;

  return (
    <Card className="cursor-pointer hover:border-primary-400 dark:hover:border-primary-600 hover:shadow-md transition-all" onClick={onClick}>
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">{gap.skill.name}</h3>
            <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{gap.skill.category}</span>
          </div>
          <Badge variant={priorityColors[gap.priority_label]}>{gap.priority_label}</Badge>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-500 dark:text-slate-400">Current Level</span>
              <span className="font-bold text-slate-700 dark:text-slate-300">{Math.round(gap.current_level)}%</span>
            </div>
            <Progress value={gap.current_level} max={100} colorClass="bg-secondary-500 dark:bg-secondary-400" />
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-500 dark:text-slate-400">Required Level</span>
              <span className="font-bold text-slate-700 dark:text-slate-300">{Math.round(gap.required_level)}%</span>
            </div>
            <Progress value={gap.required_level} max={100} colorClass="bg-primary-600 dark:bg-primary-500" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
