import apiClient from './client';
import type { NewsResponse, NewsArticle, DateFilterParams } from '@/types/api';

export const newsApi = {
  async getPublicNews(params: DateFilterParams): Promise<NewsResponse> {
    const response = await apiClient.get('/public/news', { params });
    return response.data;
  },

  async getMyNews(params: DateFilterParams & { prompt_id?: string }): Promise<NewsResponse> {
    const response = await apiClient.get('/news/my', { params });
    return response.data;
  },

  async getNewsBySlug(promptName: string, date: string, slug: string): Promise<NewsArticle> {
    const response = await apiClient.get(`/news/private/${promptName}/${date}/${slug}`);
    return response.data;
  },

  async getFullNews(date: string): Promise<NewsResponse> {
    const response = await apiClient.get(`/news/${date}/full`);
    return response.data;
  }
};