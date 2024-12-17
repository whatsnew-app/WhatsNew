import { useState, useEffect, useCallback } from 'react';
import { newsApi } from '@/lib/api/news';
import type { NewsArticle, NewsFilters } from '@/types/news';

const ITEMS_PER_PAGE = 20;

// Hook factory to create news hooks with consistent behavior
const createNewsHook = (
  fetcher: (params: any) => Promise<any>,
  options: { includePromptId?: boolean } = {}
) => {
  return (filters: NewsFilters = {}) => {
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(0);

    const loadNews = useCallback(async (reset = false) => {
      try {
        setIsLoading(true);
        setError(null);

        const params = {
          skip: reset ? 0 : page * ITEMS_PER_PAGE,
          limit: ITEMS_PER_PAGE,
          date_filter: filters.date?.toISOString().split('T')[0],
          ...(options.includePromptId && { prompt_id: filters.promptId }),
        };

        const response = await fetcher(params);
        
        // Handle both array and paginated responses
        const newsItems = Array.isArray(response) ? response : response.items || [];
        
        setArticles(prev => reset ? newsItems : [...prev, ...newsItems]);
        setHasMore(newsItems.length === ITEMS_PER_PAGE);
        if (!reset) setPage(prev => prev + 1);
      } catch (error: any) {
        console.error('Error loading news:', error);
        setError(error.response?.data?.message || 'Failed to load news');
      } finally {
        setIsLoading(false);
      }
    }, [page, filters.date, filters.promptId]);

    useEffect(() => {
      setPage(0);
      loadNews(true);
    }, [filters.date, filters.promptId, loadNews]);

    const loadMore = useCallback(() => {
      if (!isLoading && hasMore) {
        loadNews();
      }
    }, [isLoading, hasMore, loadNews]);

    return {
      articles,
      isLoading,
      error,
      hasMore,
      loadMore,
      refresh: () => loadNews(true),
    };
  };
};

// Create hooks using the factory
export const usePublicNews = createNewsHook(newsApi.getPublicNews);
export const useNews = createNewsHook(newsApi.getMyNews, { includePromptId: true });

// Re-export for backwards compatibility
export default useNews;

// Types for hook returns
export type NewsHookResult = {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => void;
  refresh: () => Promise<void>;
};