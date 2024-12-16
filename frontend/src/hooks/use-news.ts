import { useState, useEffect } from 'react';
import { newsApi } from '@/lib/api/news';
import type { NewsArticle, NewsFilters } from '@/types/news';

const ITEMS_PER_PAGE = 20;

export function useNews(filters: NewsFilters = {}) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);

  const loadNews = async (reset = false) => {
    try {
      setIsLoading(true);
      setError(null);

      const params = {
        skip: reset ? 0 : page * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
        date_filter: filters.date?.toISOString().split('T')[0],
        prompt_id: filters.promptId,
      };

      const response = await newsApi.getMyNews(params);
      
      setArticles(prev => reset ? response.items : [...prev, ...response.items]);
      setHasMore(response.items.length === ITEMS_PER_PAGE);
      if (!reset) setPage(prev => prev + 1);
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to load news');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setPage(0);
    loadNews(true);
  }, [filters.date, filters.promptId, filters.category]);

  const loadMore = () => {
    if (!isLoading && hasMore) {
      loadNews();
    }
  };

  return {
    articles,
    isLoading,
    error,
    hasMore,
    loadMore,
  };
}