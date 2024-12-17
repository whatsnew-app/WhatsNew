// src/components/layout/main-layout.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { DatePicker } from '@/components/ui/date-picker';
import Link from 'next/link';
import { LogOut, Settings, User, Shield } from 'lucide-react';

interface MainLayoutProps {
  children: React.ReactNode;
  onDateChange?: (date?: Date) => void;
}

export function MainLayout({ children, onDateChange }: MainLayoutProps) {
  const { user, logout, isAuthenticated } = useAuth();
  const [selectedDate, setSelectedDate] = useState<Date>();

  const handleDateChange = (date?: Date) => {
    setSelectedDate(date);
    onDateChange?.(date);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        {/* Brand */}
        <div className="p-4 flex items-center space-x-2">
          <Link href="/">
            <h1 className="text-xl font-bold">WhatsNews AI</h1>
          </Link>
          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded">
            {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </span>
        </div>

        {/* Navigation */}
        <nav className="mt-4">
          <Link href="/" className="block px-4 py-2 hover:bg-gray-50">
            Latest News
          </Link>
          {isAuthenticated && (
            <>
              <Link href="/prompts" className="block px-4 py-2 hover:bg-gray-50">
                My Prompts
              </Link>
              <Link href="/settings" className="block px-4 py-2 hover:bg-gray-50">
                Settings
              </Link>
            </>
          )}
        </nav>

        {/* Date Picker */}
        <div className="p-4">
          <DatePicker
            date={selectedDate}
            onDateChange={handleDateChange}
          />
        </div>

        {/* User Section */}
        <div className="absolute bottom-0 w-64 border-t">
          {isAuthenticated ? (
            <>
              {user?.is_superuser && (
                <Link href="/admin" className="block p-4 hover:bg-gray-50">
                  <div className="flex items-center space-x-2 text-blue-600">
                    <Shield size={20} />
                    <span>Admin Panel</span>
                  </div>
                </Link>
              )}
              <div className="p-4 border-t">
                <div className="flex items-center space-x-2 mb-2">
                  <User size={20} />
                  <span className="font-medium">{user?.email}</span>
                </div>
                <button
                  onClick={() => logout()}
                  className="w-full flex items-center space-x-2 text-red-600 hover:text-red-700"
                >
                  <LogOut size={20} />
                  <span>Logout</span>
                </button>
              </div>
            </>
          ) : (
            <div className="p-4 space-y-2">
              <Link href="/login">
                <Button variant="default" className="w-full">
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button variant="outline" className="w-full">
                  Register
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  );
}