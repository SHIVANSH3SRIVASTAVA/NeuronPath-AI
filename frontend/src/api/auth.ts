import { apiClient } from './client';
import { AuthResponse, Learner, LoginCredentials, RegisterCredentials } from '../types';

export const registerLearner = async (data: RegisterCredentials): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/register', data);
  return response.data;
};

export const loginLearner = async (data: LoginCredentials): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/login', data);
  return response.data;
};

export const getMe = async (): Promise<Learner> => {
  const response = await apiClient.get<Learner>('/auth/me');
  return response.data;
};

