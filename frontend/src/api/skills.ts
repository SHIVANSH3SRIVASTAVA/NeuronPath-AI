import { apiClient } from './client';
import { SkillGap, LearnerSkill } from '../types';

export const getSkillGaps = async (learnerId: number, goalId?: number) => {
  const config = goalId ? { params: { goal_id: goalId } } : undefined;
  const { data } = await apiClient.get<SkillGap[]>(`/learners/${learnerId}/skills/gaps`, config);
  return data;
};

export const getLearnerSkills = async (learnerId: number, goalId?: number) => {
  const config = goalId ? { params: { goal_id: goalId } } : undefined;
  const { data } = await apiClient.get<LearnerSkill[]>(`/learners/${learnerId}/skills`, config);
  return data;
};
