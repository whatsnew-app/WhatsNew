import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '@/lib/api'

interface User {
  id: string
  email: string
  full_name?: string
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        try {
          set({ isLoading: true, error: null })
          
          const formData = new URLSearchParams()
          formData.append('username', email)
          formData.append('password', password)
          
          const response = await api.post('/api/v1/auth/login', 
            formData.toString(),
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            }
          )

          const { access_token, refresh_token } = response.data
          
          // Store tokens
          set({
            token: access_token,
            refreshToken: refresh_token,
            isLoading: false,
          })

          // Fetch user details
          try {
            const userResponse = await api.get('/api/v1/auth/me', {
              headers: { Authorization: `Bearer ${access_token}` }
            })
            set({ user: userResponse.data })
          } catch (error) {
            console.error('Failed to fetch user details:', error)
          }
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Failed to login',
            isLoading: false,
          })
          throw error
        }
      },

      signup: async (email: string, password: string, fullName?: string) => {
        try {
          set({ isLoading: true, error: null })
          
          await api.post('/api/v1/auth/register', {
            email,
            password,
            full_name: fullName,
          })

          // Login after successful signup
          await get().login(email, password)
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Failed to sign up',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          error: null,
        })
      },

      updateUser: async (userData: Partial<User>) => {
        try {
          set({ isLoading: true, error: null })
          
          const response = await api.put('/api/v1/auth/update', userData)
          
          set({
            user: response.data,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Failed to update user',
            isLoading: false,
          })
          throw error
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
)