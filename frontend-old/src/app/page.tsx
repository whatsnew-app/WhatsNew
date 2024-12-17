'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { NewsCard } from '@/components/news/news-card';
import { usePublicNews } from '@/hooks/use-news';
import type { NewsFilters } from '@/types/news';

export default function HomePage() {
  const [filters, setFilters] = useState<NewsFilters>({});
  const { articles, isLoading, error } = usePublicNews(filters);
  
  const handleDateChange = (date?: Date) => {
    setFilters(prev => ({
      ...prev,
      date: date
    }));
  };

  return (
    <MainLayout onDateChange={handleDateChange}>
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Latest News</h1>
          <p className="mt-2 text-gray-600">
            AI-curated news updates from trusted sources
          </p>
        </header>

        <div className="space-y-6">
          {isLoading && (
            <div className="flex justify-center p-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          )}

          {error && (
            <div className="text-red-600 text-center p-4">
              {error}
            </div>
          )}

          {!isLoading && !error && articles?.length === 0 && (
            <div className="text-center text-gray-500 p-4">
              No news articles available
            </div>
          )}

          {articles?.map((article) => (
            <NewsCard 
              key={article.id} 
              article={article}
            />
          ))}
        </div>
      </div>
    </MainLayout>
  );
}