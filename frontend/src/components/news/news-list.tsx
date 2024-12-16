import { useEffect, useRef } from 'react';
import { NewsCard } from './news-card';
import { useNews } from '@/hooks/use-news';
import type { NewsFilters } from '@/types/news';

interface NewsListProps {
  filters?: NewsFilters;
}

export function NewsList({ filters }: NewsListProps) {
  const { articles, isLoading, error, hasMore, loadMore } = useNews(filters);
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
  }, [isLoading, hasMore]);

  if (error) {
    return <div className="text-red-600">Error: {error}</div>;
  }

  return (
    <div className="space-y-6">
      {articles.map((article, index) => (
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
    </div>
  );
}