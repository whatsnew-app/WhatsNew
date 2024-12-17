import axios from 'axios';
import { getCookie, setCookie, deleteCookie } from 'cookies-next';

const PUBLIC_ENDPOINTS = [
    '/public/news',
    '/public/prompts'
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Check if the request is for a public endpoint
const isPublicEndpoint = (url?: string) => {
  if (!url) return false;
  return PUBLIC_ENDPOINTS.some(endpoint => url.includes(endpoint));
};

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  // Don't add token for public endpoints
  if (isPublicEndpoint(config.url)) {
    return config;
  }
  
  const token = getCookie('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // If it's a public endpoint, just return the error
      if (isPublicEndpoint(originalRequest.url)) {
        return Promise.reject(error);
      }

      // If error is not 401 or request already retried, reject immediately
      if (error.response?.status !== 401 || originalRequest._retry) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = getCookie('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await apiClient.post('/auth/refresh', { 
          refresh_token: refreshToken 
        });
        
        const { access_token } = response.data;
        setCookie('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        processQueue(null, access_token);
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        // Only clear tokens and redirect for non-public endpoints
        if (!isPublicEndpoint(originalRequest.url)) {
          deleteCookie('access_token');
          deleteCookie('refresh_token');
          if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
);

export default apiClient;