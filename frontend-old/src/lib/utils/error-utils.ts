// src/lib/utils/error-utils.ts
import { AxiosError } from 'axios';

// Error types
export interface ErrorDetails {
  context?: string;
  componentStack?: string;
  additional?: Record<string, unknown>;
}

export interface ApiError {
  message: string;
  code: string;
  details?: unknown;
}

// Function to get a user-friendly error message
export function getErrorMessage(error: Error | null | unknown): string {
  if (!error) {
    return 'An unknown error occurred';
  }

  // Handle Axios errors
  if (isAxiosError(error)) {
    return getAxiosErrorMessage(error);
  }

  // Handle standard errors
  if (error instanceof Error) {
    return error.message;
  }

  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }

  // Handle unknown error types
  return 'An unexpected error occurred';
}

// Type guard for Axios errors
function isAxiosError(error: unknown): error is AxiosError<ApiError> {
  return (error as AxiosError).isAxiosError === true;
}

// Get message from Axios error
function getAxiosErrorMessage(error: AxiosError<ApiError>): string {
  // Handle API error responses
  if (error.response?.data) {
    const apiError = error.response.data;
    if (typeof apiError === 'string') {
      return apiError;
    }
    if (apiError.message) {
      return apiError.message;
    }
  }

  // Handle network errors
  if (error.message === 'Network Error') {
    return 'Unable to connect to the server. Please check your internet connection.';
  }

  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return 'The request timed out. Please try again.';
  }

  // Default error message
  return error.message || 'An error occurred while communicating with the server';
}

// Error logging and tracking
export function captureError(error: Error, details?: ErrorDetails): void {
  // Log error to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error captured:', {
      error,
      ...details
    });
  }

  // Add error tracking service integration here
  // Example: Sentry, LogRocket, etc.
  if (typeof window !== 'undefined' && window.errorTrackingService) {
    window.errorTrackingService.captureException(error, {
      level: 'error',
      ...details
    });
  }
}

// HTTP status code checking
export function isNotFoundError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 404;
}

export function isUnauthorizedError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 401;
}

export function isForbiddenError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 403;
}

// Validation error helpers
export function isValidationError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 422;
}

export function getValidationErrors(error: unknown): Record<string, string[]> {
  if (!isValidationError(error)) {
    return {};
  }

  const validationErrors = error.response?.data?.detail || [];
  return validationErrors.reduce((acc: Record<string, string[]>, curr: any) => {
    const field = curr.loc[curr.loc.length - 1];
    if (!acc[field]) {
      acc[field] = [];
    }
    acc[field].push(curr.msg);
    return acc;
  }, {});
}

// Error retry logic
export interface RetryOptions {
  maxAttempts?: number;
  delayMs?: number;
  backoff?: boolean;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    delayMs = 1000,
    backoff = true
  } = options;

  let attempt = 1;

  while (true) {
    try {
      return await fn();
    } catch (error) {
      if (attempt >= maxAttempts) {
        throw error;
      }

      const delay = backoff ? delayMs * Math.pow(2, attempt - 1) : delayMs;
      await new Promise(resolve => setTimeout(resolve, delay));
      attempt++;
    }
  }
}

// Add type declaration for error tracking service
declare global {
  interface Window {
    errorTrackingService?: {
      captureException: (error: Error, details?: Record<string, unknown>) => void;
    };
  }
}