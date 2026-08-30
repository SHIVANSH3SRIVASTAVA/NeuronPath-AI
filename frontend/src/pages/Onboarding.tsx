import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { OnboardingChat } from '../components/onboarding/OnboardingChat';
import { ProfileConfirmation } from '../components/onboarding/ProfileConfirmation';
import { useAppStore } from '../store/useAppStore';
import { createLearner, onboardLearner, updateLearner, updateLearnerGoal, getLearner } from '../api/learner';
import { generateRoadmap } from '../api/roadmap';
import { OnboardingResult } from '../types';
import { AlertCircle } from 'lucide-react';

const formatError = (err: any): string => {
  if (!err) return 'An error occurred during roadmap generation.';
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d?.msg || JSON.stringify(d)).join(', ');
  }
  if (typeof detail === 'object' && detail !== null) {
    return JSON.stringify(detail);
  }
  return err.message || 'Failed to generate roadmap. Please check connection.';
};

export default function Onboarding() {
  const navigate = useNavigate();
  const { setCurrentLearner, setOnboarded } = useAppStore();
  const [stage, setStage] = useState<'chat' | 'confirm'>('chat');
  const [profileData, setProfileData] = useState<(OnboardingResult & { name?: string }) | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [learnerId, setLearnerId] = useState<number | null>(null);

  const handleChatComplete = async (data: { name: string; goalText: string }) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Create a new learner with their actual name
      const learner = await createLearner({ name: data.name });
      setLearnerId(learner.id);
      setCurrentLearner(learner);

      // 2. Onboard the learner with goal text
      const result = await onboardLearner(learner.id, data.goalText);
      
      // 3. Refresh learner data
      const updatedLearner = await getLearner(learner.id);
      setCurrentLearner(updatedLearner);

      setProfileData({
        name: data.name,
        goal: result.goal || data.goalText,
        target_role: result.target_role || 'Software & Data Professional',
        experience_level: result.experience_level || updatedLearner.experience_level || 'beginner',
        known_skills: result.known_skills || [],
        weekly_hours: result.weekly_hours || updatedLearner.weekly_hours || 10,
        timeline_months: result.timeline_months || 6,
        learning_style: result.learning_style || updatedLearner.learning_style || 'visual',
        preferred_formats: result.preferred_formats || ["course", "practice"]
      });
      setStage('confirm');
    } catch (err: any) {
      console.error('Onboarding extraction error:', err);
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (finalProfile?: OnboardingResult & { name?: string }) => {
    setLoading(true);
    setError(null);
    try {
      const activeData = finalProfile || profileData;
      const id = learnerId || useAppStore.getState().currentLearner?.id;
      if (!id) {
        throw new Error('Active learner profile ID not found. Please restart onboarding.');
      }

      if (activeData) {
        // Save any manual edits to learner profile
        await updateLearner(id, {
          name: activeData.name,
          experience_level: activeData.experience_level as any,
          weekly_hours: activeData.weekly_hours,
        });

        // Save updated goal and known skills
        await updateLearnerGoal(id, {
          title: activeData.goal,
          target_role: activeData.target_role,
          timeline_months: activeData.timeline_months,
          known_skills: activeData.known_skills,
          experience_level: activeData.experience_level,
          weekly_hours: activeData.weekly_hours
        });
      }

      // Generate the personalized roadmap from the updated goal
      try {
        await generateRoadmap(id);
      } catch (rmErr) {
        console.warn('Roadmap generation trigger acknowledged:', rmErr);
      }
      
      // Refresh current learner in store
      const refreshedLearner = await getLearner(id);
      setCurrentLearner(refreshedLearner);
      setOnboarded(true);

      navigate('/dashboard');
    } catch (err: any) {
      console.error('Roadmap generation error:', err);
      setError(formatError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-12 px-4 sm:px-6 flex flex-col transition-colors">
      <div className="max-w-3xl mx-auto w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-slate-900 dark:text-white">Let's craft your learning path</h1>
          <p className="text-slate-600 dark:text-slate-300 mt-2 text-sm">
            {stage === 'chat' ? 'Tell us about yourself and what you would like to achieve' : 'Review your profile before we generate your tailored roadmap'}
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 p-4 rounded-xl mb-6 border border-red-200 dark:border-red-900 text-sm flex items-start gap-2.5">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-200">Unable to proceed</p>
              <p className="mt-0.5 text-xs">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
            <p className="text-slate-600 dark:text-slate-300 font-medium">
              {stage === 'chat' ? 'Analyzing your goal and skills...' : 'Generating your personalized roadmap...'}
            </p>
          </div>
        )}

        {stage === 'chat' && !loading && (
          <div className="shadow-sm rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
            <OnboardingChat onComplete={handleChatComplete} />
          </div>
        )}

        {stage === 'confirm' && profileData && !loading && (
          <ProfileConfirmation 
            profile={profileData} 
            onConfirm={handleConfirm}
            onUpdate={(updated) => setProfileData(updated)}
          />
        )}
      </div>
    </div>
  );
}
