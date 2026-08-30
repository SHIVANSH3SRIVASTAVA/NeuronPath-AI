import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { getProgress } from '../api/progress';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Progress } from '../components/ui/Progress';
import { Skeleton } from '../components/ui/Skeleton';
import { ActivityTimeline } from '../components/progress/ActivityTimeline';
import { MasteryGrowthChart } from '../components/progress/MasteryGrowthChart';
import { TrendingUp, PieChart } from 'lucide-react';

export default function ProgressPage() {
  const { currentLearner, activeGoalVersion, activeGoal } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [progressData, setProgressData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    getProgress(currentLearner.id)
      .then(setProgressData)
      .catch(err => {
        console.error(err);
        setError('Failed to load progress data.');
      })
      .finally(() => setLoading(false));
  }, [currentLearner, activeGoalVersion, activeGoal?.id]);

  if (!currentLearner) {
    return <div className="p-8 text-center text-slate-600 dark:text-slate-400">Please complete onboarding to view progress analytics.</div>;
  }

  if (loading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto pb-12">
        <Skeleton className="h-10 w-1/4" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 dark:text-red-300 bg-red-50 dark:bg-red-950/50 p-4 rounded-xl border border-red-200 dark:border-red-900">{error}</div>;
  }

  if (!progressData) {
    return <div className="p-8 text-center text-slate-600 dark:text-slate-400">No progress data available.</div>;
  }

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <TrendingUp className="w-7 h-7 text-primary-600 dark:text-primary-400" /> Your Learning Progress
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Real-time metrics on completed milestones, skill acquisition, and assessment scores.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MasteryGrowthChart progressData={progressData} />
        
        <Card>
          <CardHeader>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Stats Overview
            </h2>
          </CardHeader>
          <CardContent className="space-y-6 p-6">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">
                <span>Overall Goal Track</span>
                <span className="text-primary-600 dark:text-primary-400 font-bold">{Math.round(progressData.overall_progress)}%</span>
              </div>
              <Progress value={progressData.overall_progress} size="lg" />
            </div>
            
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
              <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-4">Skill Proficiency Distribution</h3>
              <div className="space-y-3.5">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-600 dark:text-slate-400 font-medium">Mastered Skills</span>
                    <span className="font-bold text-emerald-600 dark:text-emerald-400">{progressData.skills_mastered}</span>
                  </div>
                  <Progress value={Math.min(100, (progressData.skills_mastered / 10) * 100)} colorClass="bg-emerald-500" />
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-600 dark:text-slate-400 font-medium">Developing Skills</span>
                    <span className="font-bold text-primary-600 dark:text-primary-400">{progressData.skills_developing}</span>
                  </div>
                  <Progress value={Math.min(100, (progressData.skills_developing / 10) * 100)} colorClass="bg-primary-500" />
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-600 dark:text-slate-400 font-medium">Weak / Missing</span>
                    <span className="font-bold text-amber-600 dark:text-amber-400">{progressData.skills_weak + progressData.skills_missing}</span>
                  </div>
                  <Progress value={Math.min(100, ((progressData.skills_weak + progressData.skills_missing) / 10) * 100)} colorClass="bg-amber-500" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {progressData.recent_activity && progressData.recent_activity.length > 0 && (
        <Card>
          <CardHeader>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Detailed Learning Activity</h2>
          </CardHeader>
          <CardContent className="p-6">
            <ActivityTimeline activities={progressData.recent_activity} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
