import { apiClient } from './client';
import { Recommendation, Resource } from '../types';

export const getRecommendations = async (learnerId: number) => {
  const { data } = await apiClient.get<Recommendation[]>(`/learners/${learnerId}/recommendations`);
  return data;
};

export const getResources = async (params?: { type?: string; difficulty?: string }) => {
  const { data } = await apiClient.get<Resource[]>('/resources', { params });
  return data;
};
