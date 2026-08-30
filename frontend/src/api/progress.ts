import { apiClient } from './client';
import { ProgressData } from '../types';

export const getProgress = async (learnerId: number, goalId?: number) => {
  const config = goalId ? { params: { goal_id: goalId } } : undefined;
  const { data } = await apiClient.get<ProgressData>(`/learners/${learnerId}/progress`, config);
  return data;
};

