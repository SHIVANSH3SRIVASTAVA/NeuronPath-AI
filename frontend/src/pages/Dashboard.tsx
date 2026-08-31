import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { NextBestAction } from '../components/dashboard/NextBestAction';
import { GoalProgress } from '../components/dashboard/GoalProgress';
import { SkillOverview } from '../components/dashboard/SkillOverview';
import { RoadmapPreview } from '../components/dashboard/RoadmapPreview';
import { RecentActivity } from '../components/dashboard/RecentActivity';
import { Skeleton } from '../components/ui/Skeleton';
import { Button } from '../components/ui/Button';
import { getProgress } from '../api/progress';
import { getNextAction as fetchNextAction } from '../api/learner';
import { getRoadmap } from '../api/roadmap';
import { ProgressData, NextAction, Roadmap } from '../types';
import { Sparkles, Map, Target } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { currentLearner, goalsVersion, activeGoal } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [nextAction, setNextAction] = useState<NextAction | null>(null);
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);

  useEffect(() => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    
    Promise.allSettled([
      getProgress(currentLearner.id),
      fetchNextAction(currentLearner.id),
      getRoadmap(currentLearner.id),
    ]).then(([progResult, actionResult, roadmapResult]) => {
      if (progResult.status === 'fulfilled') {
        setProgressData(progResult.value);
      }
      
      if (actionResult.status === 'fulfilled' && actionResult.value) {
        const act = actionResult.value as any;
        setNextAction({
          action: act.action || 'start_resource',
          description: act.description || act.message || 'Continue your learning roadmap.',
          type: (act.action || '').includes('resource') ? 'resource' : (act.action || '').includes('assessment') ? 'assessment' : 'milestone',
          resource_id: act.resource_id,
          assessment_id: act.assessment_id,
          milestone_title: act.title || act.milestone_title
        });
      }
      
      if (roadmapResult.status === 'fulfilled' && roadmapResult.value) {
        setRoadmap(roadmapResult.value);
      } else {
        setRoadmap(null);
      }
    }).catch(err => {
      console.error('Dashboard load error:', err);
      setError('Could not load all dashboard components.');
    }).finally(() => {
      setLoading(false);
    });
  }, [currentLearner, goalsVersion, activeGoal?.id]);

  if (!currentLearner) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-16 h-16 bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center mb-2">
          <Target className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">No Learner Profile Active</h2>
        <p className="text-slate-600 dark:text-slate-400 max-w-md text-center">Get started by completing onboarding to set up your personalized learning goal.</p>
        <div className="flex gap-4 pt-2">
          <Button onClick={() => navigate('/onboarding')}>Start Onboarding</Button>
          <Button variant="secondary" onClick={() => navigate('/')}>Back to Home</Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto pb-10">
        <Skeleton className="h-12 w-1/3" />
        <Skeleton className="h-28 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-44 w-full" />
          <Skeleton className="h-44 w-full" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-64 lg:col-span-2 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  const goalTitle = roadmap?.goal?.target_role || roadmap?.goal?.title || 'Personalized Learning Goal';

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            Welcome back, {currentLearner.name || 'Learner'}! 👋
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Track: <span className="font-semibold text-primary-700 dark:text-primary-400">{goalTitle}</span> • {currentLearner.weekly_hours} hrs/week
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/roadmap')} className="flex items-center gap-1.5">
            <Map className="w-4 h-4" /> Full Roadmap
          </Button>
          <Button size="sm" onClick={() => navigate('/assessment')} className="flex items-center gap-1.5">
            <Sparkles className="w-4 h-4" /> Take Quiz
          </Button>
        </div>
      </div>

      {error && <div className="text-amber-700 bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900 p-3 rounded-lg text-sm">{error}</div>}

      {nextAction && <NextBestAction action={nextAction} />}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GoalProgress progress={progressData?.overall_progress || 0} goalTitle={goalTitle} />
        {progressData && <SkillOverview data={progressData} />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {roadmap && roadmap.milestones && roadmap.milestones.length > 0 ? (
            <RoadmapPreview roadmap={roadmap} />
          ) : (
            <div className="p-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
              <Map className="w-10 h-10 text-primary-500 mx-auto mb-3" />
              <h3 className="font-bold text-slate-900 dark:text-slate-100 mb-1">No Active Roadmap Found</h3>
              <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto mb-4">Generate your personalized step-by-step learning milestones tailored to your target skills.</p>
              <Button onClick={() => navigate('/roadmap')}>Generate My Roadmap</Button>
            </div>
          )}
        </div>
        <div>
          {progressData && <RecentActivity data={progressData} />}
        </div>
      </div>
    </div>
  );
}
