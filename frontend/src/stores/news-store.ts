import { create } from 'zustand'
import api from '@/lib/api'

export interface NewsArticle {
  id: string
  title: string
  content: string
  summary: string | null
  source_urls: string[]
  image_url: string | null
  published_date: string
  prompt_id: string
  prompt_name: string
  prompt_type: 'public' | 'internal' | 'private'
  slug: string
}

interface NewsState {
  articles: NewsArticle[]
  isLoading: boolean
  error: string | null
  hasMore: boolean
  currentPage: number
  fetchNews: (reset?: boolean) => Promise<void>
}

export const useNewsStore = create<NewsState>((set, get) => ({
  articles: [],
  isLoading: false,
  error: null,
  hasMore: true,
  currentPage: 0,

  fetchNews: async (reset = false) => {
    const { currentPage, articles } = get()
    const limit = 10
    const newPage = reset ? 0 : currentPage

    try {
      set({ isLoading: true, error: null })
      
      const response = await api.get('/api/v1/public/news', {
        params: {
          skip: newPage * limit,
          limit,
        },
      })

      const newArticles = response.data
      
      set({
        articles: reset ? newArticles : [...articles, ...newArticles],
        currentPage: newPage + 1,
        hasMore: newArticles.length === limit,
        isLoading: false,
      })
    } catch (error: any) {
      console.error('Error fetching news:', error)
      set({
        error: 'Failed to load news articles. Please try again later.',
        isLoading: false,
      })
    }
  }
}))