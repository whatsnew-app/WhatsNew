import apiClient from './client';
import type { LoginCredentials, AuthTokens, User } from '@/types/auth';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    // Create FormData object
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(data: { email: string; password: string; full_name?: string }): Promise<User> {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};