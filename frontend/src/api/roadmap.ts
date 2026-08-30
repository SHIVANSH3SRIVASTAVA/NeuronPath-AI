import { apiClient } from './client';
import { Roadmap } from '../types';

export const getRoadmap = async (learnerId: number, goalId?: number) => {
  const config = goalId ? { params: { goal_id: goalId } } : undefined;
  const { data } = await apiClient.get<Roadmap>(`/learners/${learnerId}/roadmap`, config);
  return data;
};

export const generateRoadmap = async (learnerId: number, goalId?: number) => {
  const { data } = await apiClient.post<Roadmap>(`/learners/${learnerId}/roadmap`, goalId ? { goal_id: goalId } : {});
  return data;
};

export const startMilestone = async (learnerId: number, milestoneId: number) => {
  const { data } = await apiClient.post(`/learners/${learnerId}/roadmap/milestones/${milestoneId}/start`, {});
  return data;
};

export const markItemComplete = async (learnerId: number, itemId: number) => {
  const { data } = await apiClient.post(`/learners/${learnerId}/roadmap/items/${itemId}/complete`, {});
  return data;
};
