import React from 'react';

export function RoadmapTimeline({ children }: { children: React.ReactNode }) {
  return <div className="relative border-l-2 border-slate-200 dark:border-slate-800 ml-4 space-y-8 transition-colors">{children}</div>;
}
