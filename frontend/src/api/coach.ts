import { apiClient } from './client';
import { ChatMessage } from '../types';

interface CoachResponse {
  content: string;
  intent: string;
  action_taken: string | null;
}

export const getCoachHistory = async (learnerId: number) => {
  const { data } = await apiClient.get<ChatMessage[]>(`/learners/${learnerId}/coach/history`);
  return data;
};

export const sendCoachMessage = async (learnerId: number, message: string) => {
  const { data } = await apiClient.post<CoachResponse>(`/learners/${learnerId}/coach/chat`, { content: message });
  return data;
};
