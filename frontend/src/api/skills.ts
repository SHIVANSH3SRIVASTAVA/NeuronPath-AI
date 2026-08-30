import { apiClient } from './client';
import { SkillGap, LearnerSkill } from '../types';

export const getSkillGaps = async (learnerId: number) => {
  const { data } = await apiClient.get<SkillGap[]>(`/learners/${learnerId}/skills/gaps`);
  return data;
};

export const getLearnerSkills = async (learnerId: number) => {
  const { data } = await apiClient.get<LearnerSkill[]>(`/learners/${learnerId}/skills`);
  return data;
};
