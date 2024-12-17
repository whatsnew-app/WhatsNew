import { create } from 'zustand'
import api from '@/lib/api'

export interface Prompt {
  id: string
  name: string
  content: string
  type: 'public' | 'internal' | 'private'
  generate_image: boolean
  display_style: 'card' | 'rectangle' | 'highlight'
  news_sources: string[]
  template_id: string
  created_at: string
  updated_at: string
}

interface PromptState {
  prompts: Prompt[]
  isLoading: boolean
  error: string | null
  hasMore: boolean
  currentPage: number
  fetchPrompts: (reset?: boolean) => Promise<void>
  createPrompt: (promptData: Partial<Prompt>) => Promise<Prompt>
  updatePrompt: (id: string, promptData: Partial<Prompt>) => Promise<Prompt>
  deletePrompt: (id: string) => Promise<void>
}

export const usePromptStore = create<PromptState>((set, get) => ({
  prompts: [],
  isLoading: false,
  error: null,
  hasMore: true,
  currentPage: 0,

  fetchPrompts: async (reset = false) => {
    const { currentPage, prompts } = get()
    const limit = 20
    const newPage = reset ? 0 : currentPage

    try {
      set({ isLoading: true, error: null })
      
      const response = await api.get('/api/v1/prompts/', {
        params: {
          skip: newPage * limit,
          limit,
        },
      })

      const newPrompts = response.data
      
      set({
        prompts: reset ? newPrompts : [...prompts, ...newPrompts],
        currentPage: newPage + 1,
        hasMore: newPrompts.length === limit,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch prompts',
        isLoading: false,
      })
    }
  },

  createPrompt: async (promptData) => {
    try {
      set({ isLoading: true, error: null })
      
      const response = await api.post('/api/v1/prompts/', promptData)
      const newPrompt = response.data
      
      set((state) => ({
        prompts: [newPrompt, ...state.prompts],
        isLoading: false,
      }))

      return newPrompt
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create prompt',
        isLoading: false,
      })
      throw error
    }
  },

  updatePrompt: async (id, promptData) => {
    try {
      set({ isLoading: true, error: null })
      
      const response = await api.put(`/api/v1/prompts/${id}`, promptData)
      const updatedPrompt = response.data
      
      set((state) => ({
        prompts: state.prompts.map((prompt) =>
          prompt.id === id ? updatedPrompt : prompt
        ),
        isLoading: false,
      }))

      return updatedPrompt
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update prompt',
        isLoading: false,
      })
      throw error
    }
  },

  deletePrompt: async (id) => {
    try {
      set({ isLoading: true, error: null })
      
      await api.delete(`/api/v1/prompts/${id}`)
      
      set((state) => ({
        prompts: state.prompts.filter((prompt) => prompt.id !== id),
        isLoading: false,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete prompt',
        isLoading: false,
      })
      throw error
    }
  },
}))