import apiClient from './client';
import type { Prompt, PromptCreate, PromptUpdate } from '@/types/prompt';
import type { PaginationParams } from '@/types/api';

export const promptApi = {
  async getPrompts(params?: PaginationParams & { prompt_type?: string }): Promise<Prompt[]> {
    const response = await apiClient.get('/prompts/', { params });
    return response.data;
  },

  async createPrompt(data: PromptCreate): Promise<Prompt> {
    const response = await apiClient.post('/prompts/', data);
    return response.data;
  },

  async updatePrompt(promptId: string, data: PromptUpdate): Promise<Prompt> {
    const response = await apiClient.put(`/prompts/${promptId}`, data);
    return response.data;
  },

  async deletePrompt(promptId: string): Promise<void> {
    await apiClient.delete(`/prompts/${promptId}`);
  }
};