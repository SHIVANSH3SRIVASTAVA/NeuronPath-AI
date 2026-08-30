import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { getRoadmap, generateRoadmap, startMilestone, markItemComplete } from '../api/roadmap';
import { RoadmapTimeline } from '../components/roadmap/RoadmapTimeline';
import { MilestoneCard } from '../components/roadmap/MilestoneCard';
import { MilestoneDetail } from '../components/roadmap/MilestoneDetail';
import { Modal } from '../components/ui/Modal';
import { Roadmap, RoadmapMilestone } from '../types';
import { Skeleton } from '../components/ui/Skeleton';
import { Button } from '../components/ui/Button';
import { Map, RefreshCw, AlertCircle } from 'lucide-react';

export default function RoadmapPage() {
  const { currentLearner, activeGoalVersion, activeGoal } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [selectedMilestone, setSelectedMilestone] = useState<RoadmapMilestone | null>(null);
  const [processing, setProcessing] = useState(false);

  const fetchRoadmap = async () => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    try {
      const rMap = await getRoadmap(currentLearner.id, activeGoal?.id);
      setRoadmap(rMap);
      return rMap;
    } catch (err: any) {
      setRoadmap(null);
      setError(err?.response?.data?.detail || err.message || 'Failed to load roadmap.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, [currentLearner, activeGoalVersion, activeGoal?.id]);

  const handleRecalculate = async () => {
    if (!currentLearner) return;
    setProcessing(true);
    setError(null);
    try {
      await generateRoadmap(currentLearner.id, activeGoal?.id);
      await fetchRoadmap();
      setSelectedMilestone(null);
    } catch (err: any) {
      console.error('Roadmap calculation error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to recalculate roadmap.');
    } finally {
      setProcessing(false);
    }
  };

  const handleStartMilestone = async () => {
    if (!currentLearner || !selectedMilestone) return;
    setProcessing(true);
    setError(null);
    try {
      await startMilestone(currentLearner.id, selectedMilestone.id);
      const updatedList = roadmap?.milestones.map(m => 
        m.id === selectedMilestone.id ? { ...m, status: 'in_progress' as const } : m
      ) || [];
      if (roadmap) {
        setRoadmap({ ...roadmap, milestones: updatedList });
      }
      setSelectedMilestone(prev => prev ? { ...prev, status: 'in_progress' as const } : null);

      const refreshed = await fetchRoadmap();
      if (refreshed && selectedMilestone) {
        const found = refreshed.milestones.find(m => m.id === selectedMilestone.id);
        if (found) setSelectedMilestone(found);
      }
    } catch (err: any) {
      console.error('Start milestone error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to start milestone.');
    } finally {
      setProcessing(false);
    }
  };

  const handleCompleteItem = async (itemId: number) => {
    if (!currentLearner) return;
    setProcessing(true);
    try {
      await markItemComplete(currentLearner.id, itemId);
      const refreshed = await fetchRoadmap();
      if (refreshed && selectedMilestone) {
        const updated = refreshed.milestones.find(m => m.id === selectedMilestone.id);
        if (updated) setSelectedMilestone(updated);
      }
    } catch (err: any) {
      console.error('Complete task error:', err);
    } finally {
      setProcessing(false);
    }
  };

  if (!currentLearner) {
    return <div className="p-8 text-center text-slate-600 dark:text-slate-400">Please complete onboarding to view your roadmap.</div>;
  }

  if (loading && !roadmap) {
    return (
      <div className="space-y-4 max-w-4xl mx-auto pt-6 pb-12">
        <Skeleton className="h-10 w-1/4" />
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {error && (
        <div className="text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-950/50 p-4 rounded-xl border border-red-200 dark:border-red-900 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
            <Map className="w-7 h-7 text-primary-600 dark:text-primary-400" /> Your Learning Path
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Personalized milestone progression tailored to your goals.
          </p>
        </div>
        <Button variant="outline" onClick={handleRecalculate} disabled={processing} className="font-semibold">
          <RefreshCw className={`w-4 h-4 mr-2 ${processing ? 'animate-spin' : ''}`} />
          {processing ? 'Recalculating...' : 'Recalculate Path'}
        </Button>
      </div>

      {!roadmap || roadmap.milestones.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 p-12 text-center rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs mt-8">
          <Map className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <h3 className="font-bold text-slate-800 dark:text-slate-200 mb-1">No Roadmap Generated Yet</h3>
          <p className="text-slate-500 dark:text-slate-400 text-sm mb-4">Click below to build your tailored learning roadmap.</p>
          <Button onClick={handleRecalculate} disabled={processing}>Generate Roadmap</Button>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs mt-6 transition-colors">
          <RoadmapTimeline>
            {roadmap.milestones.map(m => (
              <MilestoneCard 
                key={m.id} 
                milestone={m} 
                onClick={() => setSelectedMilestone(m)} 
              />
            ))}
          </RoadmapTimeline>
        </div>
      )}

      <Modal 
        isOpen={!!selectedMilestone} 
        onClose={() => setSelectedMilestone(null)} 
        title="Milestone Details & Learning Tasks"
      >
        {selectedMilestone && (
          <MilestoneDetail 
            milestone={selectedMilestone}
            onStart={handleStartMilestone}
            onCompleteItem={handleCompleteItem}
            starting={processing}
          />
        )}
      </Modal>
    </div>
  );
}
