import { apiClient } from './client';
import { Learner, NextAction, OnboardingResult } from '../types';

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
  const { data } = await apiClient.delete<{ status: string; message: string }>(`/learners/${id}`);
  return data;
};

