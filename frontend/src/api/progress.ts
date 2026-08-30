import { apiClient } from './client';
import { ProgressData } from '../types';

export const getProgress = async (learnerId: number) => {
  const { data } = await apiClient.get<ProgressData>(`/learners/${learnerId}/progress`);
  return data;
};
