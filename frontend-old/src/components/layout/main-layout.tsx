// src/components/layout/main-layout.tsx
'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout/sidebar';
import { useAuth } from '@/providers/auth-provider';
import { Toaster } from '@/components/ui/toaster';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { isLoading, error } = useAuth();
  const pathname = usePathname();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  // Handle date changes from the sidebar
  const handleDateChange = (date: Date | undefined) => {
    if (date) {
      setSelectedDate(date);
      // You can add additional date-related logic here
    }
  };

  // Effect to reset selected date when pathname changes
  useEffect(() => {
    if (pathname?.includes('/news/') || pathname === '/') {
      setSelectedDate(new Date());
    }
  }, [pathname]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        selectedDate={selectedDate}
        onDateChange={handleDateChange}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="m-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-6">
            {children}
          </div>
        </main>

        {/* Toast Notifications */}
        <Toaster />
      </div>
    </div>
  );
}