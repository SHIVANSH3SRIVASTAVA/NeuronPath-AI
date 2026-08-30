import { apiClient } from './client';
import { Recommendation, Resource } from '../types';

export const getRecommendations = async (learnerId: number, goalId?: number) => {
  const config = goalId ? { params: { goal_id: goalId } } : undefined;
  const { data } = await apiClient.get<Recommendation[]>(`/learners/${learnerId}/recommendations`, config);
  return data;
};

export const getResources = async (params?: { type?: string; difficulty?: string }) => {
  const { data } = await apiClient.get<Resource[]>('/resources', { params });
  return data;
};
