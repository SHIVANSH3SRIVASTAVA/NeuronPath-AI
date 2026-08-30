import React from 'react';
import { cn } from '../../utils';

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  colorClass?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Progress({ value, max = 100, colorClass = 'bg-primary-600 dark:bg-primary-500', size = 'md', className, ...props }: ProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const sizes = { sm: 'h-1.5', md: 'h-2.5', lg: 'h-4' };
  
  return (
    <div className={cn('w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden border border-slate-200/50 dark:border-slate-700/50', sizes[size], className)} {...props}>
      <div 
        className={cn('h-full rounded-full transition-all duration-500 ease-in-out shadow-xs', colorClass)} 
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
