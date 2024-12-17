'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import type { User, AuthState } from '@/types/auth';
import { deleteCookie, getCookie } from 'cookies-next';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Define public paths that don't require authentication
const PUBLIC_PATHS = ['/', '/login', '/register', '/public/news'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: false,  // Changed to false initially
    isAuthenticated: false,
    error: null
  });

  useEffect(() => {
    const checkAuth = async () => {
      console.log('Current pathname:', pathname);

      // Always allow public paths without checking auth
      if (PUBLIC_PATHS.includes(pathname || '')) {
        console.log('Public path detected, skipping auth check');
        setState(prev => ({ 
          ...prev, 
          isLoading: false,
          user: null,
          isAuthenticated: false 
        }));
        return;
      }

      // Check for existing token
      const token = getCookie('access_token');
      if (!token) {
        console.log('No token found');
        setState(prev => ({ ...prev, isLoading: false }));
        // Only redirect on protected routes
        if (!PUBLIC_PATHS.includes(pathname || '')) {
          router.push('/login');
        }
        return;
      }

      // Only try to get profile if we have a token and aren't on a public path
      try {
        setState(prev => ({ ...prev, isLoading: true }));
        const user = await authApi.getProfile();
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
          error: null
        });
      } catch (error) {
        console.error('Auth check failed:', error);
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: null
        });
        
        // Only redirect if we're not on a public path
        if (!PUBLIC_PATHS.includes(pathname || '')) {
          router.push('/login');
        }
      }
    };

    checkAuth();
  }, [pathname, router]);

  const login = async (email: string, password: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      const response = await authApi.login({ username: email, password });
      const user = await authApi.getProfile();
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null
      });
      router.push('/');
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Login failed'
      }));
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      await authApi.register({ email, password, full_name: fullName });
      router.push('/login');
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.response?.data?.message || 'Registration failed'
      }));
      throw error;
    }
  };

  const logout = () => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null
    });
    router.push('/');
  };

  // Show loading state only when explicitly loading
  // Remove this to prevent flash of loading state
  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <AuthContext.Provider 
      value={{ 
        ...state, 
        login, 
        register, 
        logout 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};