// src/lib/api/client.ts
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';

// Define API response types
interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Updated comprehensive list of public endpoints
const PUBLIC_ENDPOINTS = [
  '/public/news',
  '/public/prompts',
  '/auth/login',
  '/auth/register',
  '/politics',
  '/finance',
  '/science',
  '/startups'
];

// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh state management
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

// Add callback to refresh subscribers
const addRefreshSubscriber = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

// Execute refresh token subscribers
const onRefreshSuccess = (token: string) => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

// Clear refresh token subscribers
const onRefreshFailure = (error: AxiosError) => {
  refreshSubscribers.forEach((callback) => callback(''));
  refreshSubscribers = [];
  throw error;
};

// Check if endpoint is public
const isPublicEndpoint = (url?: string): boolean => {
  if (!url) return false;
  return PUBLIC_ENDPOINTS.some(endpoint => url.includes(endpoint));
};

// Handle refresh token
const handleTokenRefresh = async (): Promise<string> => {
  try {
    const refreshToken = getCookie('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post<RefreshTokenResponse>(
      `${API_URL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken },
      { baseURL: '' } // Avoid interceptors
    );

    const { access_token, refresh_token } = response.data;
    setCookie('access_token', access_token);
    setCookie('refresh_token', refresh_token);

    return access_token;
  } catch (error) {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    throw error;
  }
};

// Request interceptor
apiClient.interceptors.request.use(
  async (config: AxiosRequestConfig) => {
    // Skip token for public endpoints
    if (isPublicEndpoint(config.url)) {
      return config;
    }

    const token = getCookie('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // If it's a public endpoint or not a 401 error, reject immediately
    if (
      !originalRequest ||
      isPublicEndpoint(originalRequest.url) ||
      error.response?.status !== 401 ||
      (originalRequest as any)._retry
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Wait for token refresh
      try {
        const token = await new Promise<string>((resolve) => {
          addRefreshSubscriber((token: string) => {
            resolve(token);
          });
        });

        if (token && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    // Start token refresh process
    isRefreshing = true;
    (originalRequest as any)._retry = true;

    try {
      const newToken = await handleTokenRefresh();
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      onRefreshSuccess(newToken);
      return apiClient(originalRequest);
    } catch (refreshError) {
      onRefreshFailure(refreshError as AxiosError);
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

// API error handler
const handleApiError = (error: AxiosError): never => {
  const errorMessage = error.response?.data?.detail || error.message;
  throw new Error(errorMessage);
};

// Export wrapped client with error handling
export default {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.get<T>(url, config);
      return response;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.post<T>(url, data, config);
      return response;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.put<T>(url, data, config);
      return response;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.delete<T>(url, config);
      return response;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  }
};