import { apiClient } from './client';
import { Learner, LearnerGoal, GoalDeleteResult, NextAction, OnboardingResult } from '../types';

export const createLearner = async (data: { name: string; experience_level?: string; weekly_hours?: number }) => {
  const { data: learner } = await apiClient.post<Learner>('/learners', data);
  return learner;
};

export const getLearner = async (id: number) => {
  const { data } = await apiClient.get<Learner>(`/learners/${id}`);
  return data;
};

export const updateLearner = async (id: number, update: Partial<Learner>) => {
  const { data } = await apiClient.put<Learner>(`/learners/${id}`, update);
  return data;
};

export const onboardLearner = async (id: number, goalText: string) => {
  const { data } = await apiClient.post<OnboardingResult>(`/learners/${id}/onboard`, { goal_text: goalText });
  return data;
};

export const updateLearnerGoal = async (id: number, data: {
  title: string;
  target_role: string;
  timeline_months: number;
  known_skills?: string[];
  experience_level?: string;
  weekly_hours?: number;
}) => {
  const { data: res } = await apiClient.post(`/learners/${id}/goal`, data);
  return res;
};

export const getNextAction = async (id: number) => {
  try {
    const { data } = await apiClient.get<NextAction>(`/learners/${id}/roadmap/next-action`);
    return data;
  } catch {
    const { data } = await apiClient.get<NextAction>(`/learners/${id}/next-action`);
    return data;
  }
};

export const deleteLearner = async (id: number): Promise<{ status: string; message: string }> => {
  try {
    const { data } = await apiClient.delete<{ status: string; message: string }>(`/learners/${id}`);
    return data;
  } catch (err: any) {
    if (err.response?.status === 405 || err.response?.status === 404) {
      const { data } = await apiClient.delete<{ status: string; message: string }>('/auth/me');
      return data;
    }
    throw err;
  }
};

export const getLearnerGoals = async (learnerId: number): Promise<LearnerGoal[]> => {
  try {
    const { data } = await apiClient.get<LearnerGoal[]>('/goals');
    if (Array.isArray(data) && data.length > 0) return data;
  } catch {}

  try {
    const { data } = await apiClient.get<LearnerGoal[]>(`/learners/${learnerId}/goals`);
    if (Array.isArray(data) && data.length > 0) return data;
  } catch {}

  return [];
};

export const createLearnerGoal = async (
  learnerId: number,
  payload: { title: string; target_role: string; timeline_months: number; set_active?: boolean }
): Promise<LearnerGoal> => {
  // 1. Try clean /goals endpoint
  try {
    const { data } = await apiClient.post<LearnerGoal>('/goals', payload);
    if (data && data.id) return data;
  } catch (err1: any) {
    if (err1.response?.status !== 404 && err1.response?.status !== 405) {
      // If validation error from backend, let it fall through or try alternative
    }
  }

  // 2. Try /learners/{id}/goals endpoint
  try {
    const { data } = await apiClient.post<LearnerGoal>(`/learners/${learnerId}/goals`, payload);
    if (data && data.id) return data;
  } catch (err2: any) {
    if (err2.response?.status !== 404 && err2.response?.status !== 405) {
    }
  }

  // 3. Try /learners/{id}/goal endpoint (supported by all deployment revisions)
  const { data: res } = await apiClient.post<any>(`/learners/${learnerId}/goal`, {
    title: payload.title,
    target_role: payload.target_role,
    timeline_months: payload.timeline_months,
    known_skills: []
  });

  return {
    id: res.id || res.goal_id,
    learner_id: learnerId,
    title: res.title || payload.title,
    target_role: res.target_role || payload.target_role,
    timeline_months: res.timeline_months || payload.timeline_months,
    status: 'active'
  };
};

export const activateLearnerGoal = async (learnerId: number, goalId: number): Promise<LearnerGoal> => {
  try {
    const { data } = await apiClient.put<LearnerGoal>(`/goals/${goalId}/activate`);
    return data;
  } catch {}

  try {
    const { data } = await apiClient.put<LearnerGoal>(`/learners/${learnerId}/goals/${goalId}/activate`);
    return data;
  } catch {}

  const { data } = await apiClient.post<LearnerGoal>(`/learners/${learnerId}/goals/${goalId}/activate`);
  return data;
};

export const deleteLearnerGoal = async (learnerId: number, goalId: number): Promise<GoalDeleteResult> => {
  try {
    const { data } = await apiClient.delete<GoalDeleteResult>(`/goals/${goalId}`);
    return data;
  } catch {}

  const { data } = await apiClient.delete<GoalDeleteResult>(`/learners/${learnerId}/goals/${goalId}`);
  return data;
};



