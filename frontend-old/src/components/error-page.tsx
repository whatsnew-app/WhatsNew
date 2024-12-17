// src/components/error-page.tsx
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { XCircle, RefreshCw, Home } from 'lucide-react';
import { getErrorMessage } from '@/lib/utils/error-utils';

interface ErrorPageProps {
  error: Error | null;
  reset?: () => void;
  fullPage?: boolean;
}

export function ErrorPage({ error, reset, fullPage = true }: ErrorPageProps) {
  const router = useRouter();
  const errorMessage = getErrorMessage(error);

  // Handle navigation back home
  const handleHomeClick = () => {
    router.push('/');
  };

  // Handle retry
  const handleRetry = () => {
    if (reset) {
      reset();
    } else {
      window.location.reload();
    }
  };

  const content = (
    <div className="flex flex-col items-center justify-center text-center">
      <XCircle className="h-16 w-16 text-red-500 mb-4" />
      
      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        Oops! Something went wrong
      </h1>
      
      <Alert variant="destructive" className="mb-6 max-w-md">
        <AlertTitle>Error Details</AlertTitle>
        <AlertDescription className="mt-2">
          {errorMessage}
        </AlertDescription>
      </Alert>

      <div className="flex gap-4">
        <Button
          onClick={handleRetry}
          className="flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </Button>

        <Button
          variant="outline"
          onClick={handleHomeClick}
          className="flex items-center gap-2"
        >
          <Home className="h-4 w-4" />
          Go Home
        </Button>
      </div>

      {process.env.NODE_ENV === 'development' && error?.stack && (
        <div className="mt-8 max-w-2xl">
          <details className="text-left bg-gray-50 p-4 rounded-lg">
            <summary className="cursor-pointer text-sm text-gray-600 mb-2">
              Stack Trace
            </summary>
            <pre className="text-xs text-gray-800 overflow-auto p-2">
              {error.stack}
            </pre>
          </details>
        </div>
      )}
    </div>
  );

  if (!fullPage) {
    return content;
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8">
        {content}
      </div>
    </div>
  );
}