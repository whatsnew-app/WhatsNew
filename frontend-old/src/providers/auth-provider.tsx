// src/providers/auth-provider.tsx
'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import type { User, AuthState } from '@/types/auth';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Comprehensive list of public paths
const PUBLIC_PATHS = [
  '/',
  '/login',
  '/register',
  '/public/news',
  '/politics',
  '/finance',
  '/science',
  '/startups'
];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null
  });

  // Token refresh logic
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshToken = getCookie('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await authApi.refreshToken(refreshToken);
      setCookie('access_token', response.access_token);
      setCookie('refresh_token', response.refresh_token);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }, []);

  // Check token expiration
  const isTokenExpired = useCallback((token: string): boolean => {
    try {
      const decoded = jwtDecode(token);
      if (!decoded.exp) return true;
      // Add 1 minute buffer
      return decoded.exp * 1000 <= Date.now() + 60000;
    } catch {
      return true;
    }
  }, []);

  // Enhanced authentication check
  const checkAuth = useCallback(async () => {
    try {
      // Skip auth check for public paths
      if (PUBLIC_PATHS.some(path => pathname?.startsWith(path))) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          user: null,
          isAuthenticated: false
        }));
        return;
      }

      const accessToken = getCookie('access_token');
      
      // If no token, clear state and redirect if needed
      if (!accessToken) {
        setState(prev => ({ ...prev, isLoading: false }));
        if (!PUBLIC_PATHS.some(path => pathname?.startsWith(path))) {
          router.push('/login');
        }
        return;
      }

      // Check token expiration
      if (isTokenExpired(accessToken.toString())) {
        const refreshSuccessful = await refreshToken();
        if (!refreshSuccessful) {
          throw new Error('Token refresh failed');
        }
      }

      // Get user profile
      const user = await authApi.getProfile();
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null
      });
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear tokens on auth failure
      deleteCookie('access_token');
      deleteCookie('refresh_token');
      
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null
      });

      // Only redirect if not on a public path
      if (!PUBLIC_PATHS.some(path => pathname?.startsWith(path))) {
        router.push('/login');
      }
    }
  }, [pathname, router, refreshToken, isTokenExpired]);

  // Run auth check on mount and path change
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Enhanced login with proper error handling
  const login = async (email: string, password: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      const tokens = await authApi.login({ username: email, password });
      
      // Store tokens
      setCookie('access_token', tokens.access_token);
      setCookie('refresh_token', tokens.refresh_token);
      
      // Get user profile
      const user = await authApi.getProfile();
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null
      });
      
      router.push('/');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Login failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw new Error(errorMessage);
    }
  };

  // Enhanced register with proper error handling
  const register = async (email: string, password: string, fullName?: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      await authApi.register({ email, password, full_name: fullName });
      router.push('/login');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Registration failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw new Error(errorMessage);
    }
  };

  // Enhanced logout with cleanup
  const logout = useCallback(() => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null
    });
    router.push('/');
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        refreshToken
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