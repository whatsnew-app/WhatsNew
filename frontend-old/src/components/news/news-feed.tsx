import { useEffect, useState } from 'react';
import { NewsCard } from './news-card';
import { newsApi } from '@/lib/api/news';
import type { NewsArticle, NewsFilters } from '@/types/news';

interface NewsFeedProps {
  filters: NewsFilters;
  className?: string;
}

export function NewsFeed({ filters, className }: NewsFeedProps) {
  const [news, setNews] = useState<{
    items: NewsArticle[];
    isLoading: boolean;
    error: string | null;
  }>({
    items: [],
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setNews(prev => ({ ...prev, isLoading: true, error: null }));
        const response = await newsApi.getPublicNews({
          date_filter: filters.date?.toISOString().split('T')[0],
          limit: 20,
          skip: 0,
        });
        setNews({
          items: response.items,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        setNews({
          items: [],
          isLoading: false,
          error: error.message || 'Failed to load news',
        });
      }
    };

    fetchNews();
  }, [filters]);

  if (news.error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">{news.error}</p>
        <button 
          onClick={() => setNews(prev => ({ ...prev, isLoading: true }))}
          className="text-blue-600 hover:text-blue-800 mt-4"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className={className}>
      {news.items.length === 0 && !news.isLoading ? (
        <div className="text-center p-8">
          <p className="text-gray-600">No news articles found</p>
        </div>
      ) : (
        <div className="space-y-6">
          {news.items.map(article => (
            <NewsCard 
              key={article.id} 
              article={article} 
              displayStyle={article.prompt_type === 'public' ? 'card' : 'rectangle'} 
            />
          ))}
        </div>
      )}

      {news.isLoading && (
        <div className="flex justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      )}
    </div>
  );
}