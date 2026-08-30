import { apiClient } from './client';
import { Assessment, AssessmentResult } from '../types';

export const getAssessment = async (assessmentId: number) => {
  const { data } = await apiClient.get<Assessment>(`/assessments/${assessmentId}`);
  return data;
};

export const submitAssessment = async (learnerId: number, assessmentId: number, answers: Record<string | number, number>) => {
  const { data } = await apiClient.post<AssessmentResult>(`/assessments/${assessmentId}/submit`, { answers }, { params: { learner_id: learnerId } });
  return data;
};

export const generateAssessment = async (learnerId: number, milestoneId?: number, skillIds?: number[]) => {
  const payload: { milestone_id?: number; skill_ids?: number[] } = {};
  if (milestoneId) payload.milestone_id = milestoneId;
  if (skillIds && skillIds.length > 0) payload.skill_ids = skillIds;
  const { data } = await apiClient.post<Assessment>('/assessments/generate', payload, { params: { learner_id: learnerId } });
  return data;
};
