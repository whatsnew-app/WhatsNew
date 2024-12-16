'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { NewsList } from '@/components/news/news-list';
import { useAuth } from '@/providers/auth-provider';
import type { NewsFilters } from '@/types/news';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [filters, setFilters] = useState<NewsFilters>({});
  
  const handleDateChange = (date?: Date) => {
    setFilters(prev => ({
      ...prev,
      date: date
    }));
  };

  const handlePromptChange = (promptId?: string) => {
    setFilters(prev => ({
      ...prev,
      promptId: promptId
    }));
  };

  return (
    <MainLayout
      onDateChange={handleDateChange}
      onPromptChange={handlePromptChange}
    >
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Latest News</h1>
          <p className="mt-2 text-gray-600">
            AI-curated news updates from trusted sources
          </p>
        </header>

        <NewsList filters={filters} />
      </div>
    </MainLayout>
  );
}