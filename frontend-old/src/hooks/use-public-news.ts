import { useState, useEffect, useCallback } from 'react';
import { newsApi } from '@/lib/api/news';
import type { NewsArticle, NewsFilters } from '@/types/news';

const ITEMS_PER_PAGE = 20;

export function usePublicNews(filters: NewsFilters = {}) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await newsApi.getPublicNews({
        skip: 0,
        limit: ITEMS_PER_PAGE,
        date_filter: filters.date?.toISOString().split('T')[0]
      });
      setArticles(response.items || []);
    } catch (error: any) {
      setError(error.message || 'Failed to load news');
    } finally {
      setIsLoading(false);
    }
  }, [filters.date]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  return { articles, isLoading, error };
}