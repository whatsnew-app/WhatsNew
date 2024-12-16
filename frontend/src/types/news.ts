export type PromptType = 'public' | 'internal' | 'private';
export type DisplayStyle = 'card' | 'rectangle' | 'highlight';

export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  source_urls: string[];
  image_url?: string;
  ai_metadata?: Record<string, any>;
  prompt_id: string;
  prompt_type: PromptType;
  prompt_name: string;
  published_date: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface NewsResponse {
  items: NewsArticle[];
  total: number;
  skip: number;
  limit: number;
}

export interface NewsFilters {
  date?: Date;
  promptId?: string;
  category?: string;
}

export interface NewsState {
  articles: NewsArticle[];
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
  currentPage: number;
}