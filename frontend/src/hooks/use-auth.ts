import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { setCookie, deleteCookie } from 'cookies-next';
import { authApi } from '@/lib/api/auth';
import type { User, LoginCredentials, RegisterCredentials } from '@/types/auth';

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const user = await authApi.getProfile();
      setUser(user);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      setError(null);
      const tokens = await authApi.login(credentials);
      setCookie('access_token', tokens.access_token);
      setCookie('refresh_token', tokens.refresh_token);
      await checkAuth();
      router.push('/');
    } catch (error: any) {
      setError(error.response?.data?.message || 'Login failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterCredentials) => {
    try {
      setIsLoading(true);
      setError(null);
      await authApi.register(data);
      router.push('/login');
    } catch (error: any) {
      setError(error.response?.data?.message || 'Registration failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    setUser(null);
    router.push('/login');
  };

  return {
    user,
    isLoading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };
}