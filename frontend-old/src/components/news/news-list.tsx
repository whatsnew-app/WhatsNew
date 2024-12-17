import { useEffect, useRef } from 'react';
import { NewsCard } from './news-card';
import { useNews, usePublicNews, type NewsHookResult } from '@/hooks/use-news';
import { useAuth } from '@/providers/auth-provider';
import type { NewsFilters } from '@/types/news';

interface NewsListProps {
  filters?: NewsFilters;
  type?: 'public' | 'all';
}

export function NewsList({ filters = {}, type = 'all' }: NewsListProps) {
  const { isAuthenticated } = useAuth();
  // Always call both hooks to maintain consistent hook ordering
  const publicNewsResult = usePublicNews(filters);
  const privateNewsResult = useNews(filters);

  // Select which result to use based on type and auth status
  const newsResult: NewsHookResult = 
    (!isAuthenticated || type === 'public') ? publicNewsResult : privateNewsResult;

  const { articles, isLoading, error, hasMore, loadMore } = newsResult;
  const observer = useRef<IntersectionObserver>();
  const lastArticleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isLoading) return;

    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMore();
      }
    });

    if (lastArticleRef.current) {
      observer.current.observe(lastArticleRef.current);
    }

    return () => {
      if (observer.current) {
        observer.current.disconnect();
      }
    };
  }, [isLoading, hasMore, loadMore]);

  if (error) {
    return (
      <div className="text-center p-4">
        <div className="text-red-600">Error: {error}</div>
        <button 
          onClick={() => loadMore()} 
          className="mt-2 text-blue-600 hover:text-blue-800"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {articles?.map((article, index) => (
        <div
          key={article.id}
          ref={index === articles.length - 1 ? lastArticleRef : null}
        >
          <NewsCard article={article} />
        </div>
      ))}
      
      {isLoading && (
        <div className="flex justify-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      )}
      
      {!isLoading && !error && (!articles || articles.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          No news articles found
        </div>
      )}
      
      {error && (
        <div className="text-center p-4">
          <div className="text-red-600">{error}</div>
        </div>
      )}
    </div>
  );
}