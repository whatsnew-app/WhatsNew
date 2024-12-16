'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { DatePicker } from '@/components/ui/date-picker';
import Link from 'next/link';
import { LogOut, Settings, User } from 'lucide-react';





interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { user, logout } = useAuth();
  const [selectedDate, setSelectedDate] = useState<Date>();

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        {/* Brand */}
        <div className="p-4 flex items-center space-x-2">
          <h1 className="text-xl font-bold">WhatsNews AI</h1>
          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded">
            {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </span>
        </div>

        {/* Date Picker */}
        <div className="p-4">
          <DatePicker
            date={selectedDate}
            onChange={setSelectedDate}
          />
        </div>

        {/* Navigation */}
        <nav className="mt-4">
          <Link href="/politics" className="block px-4 py-2 hover:bg-gray-50">
            Politics
          </Link>
          <Link href="/finance" className="block px-4 py-2 hover:bg-gray-50">
            Finance
          </Link>
          <Link href="/science" className="block px-4 py-2 hover:bg-gray-50">
            Science
          </Link>
          <Link href="/startups" className="block px-4 py-2 hover:bg-gray-50">
            Startups
          </Link>
        </nav>

        {/* User Section */}
        {user ? (
          <div className="absolute bottom-0 w-64 border-t">
            <Link href="/prompts" className="block p-4 hover:bg-gray-50">
              <div className="flex items-center space-x-2">
                <User size={20} />
                <span>My Prompts</span>
              </div>
            </Link>
            <Link href="/settings" className="block p-4 hover:bg-gray-50">
              <div className="flex items-center space-x-2">
                <Settings size={20} />
                <span>Settings</span>
              </div>
            </Link>
            <button
              onClick={logout}
              className="w-full p-4 hover:bg-gray-50 text-red-600 flex items-center space-x-2"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div className="absolute bottom-0 w-64 border-t p-4 space-y-2">
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

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  );
}