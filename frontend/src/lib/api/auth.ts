import apiClient from './client';
import type { LoginCredentials, RegisterCredentials, AuthTokens, User } from '@/types/auth';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  async register(data: RegisterCredentials): Promise<User> {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.put('/auth/update', data);
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }
};