'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { DatePicker } from '@/components/ui/date-picker';
import { LogOut, Settings, User, Home, BookOpen, Briefcase, Flask, Rocket } from 'lucide-react';

interface SidebarProps {
  onDateChange?: (date: Date | undefined) => void;
  selectedDate?: Date;
}

export function Sidebar({ onDateChange, selectedDate }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navigationItems = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Politics', href: '/politics', icon: BookOpen },
    { name: 'Finance', href: '/finance', icon: Briefcase },
    { name: 'Science', href: '/science', icon: Flask },
    { name: 'Startups', href: '/startups', icon: Rocket },
  ];

  return (
    <div className="w-64 bg-white shadow-lg h-full flex flex-col">
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
          onChange={onDateChange}
        />
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50",
                pathname === item.href && "bg-gray-100 text-blue-600"
              )}
            >
              <Icon className="mr-3 h-4 w-4" />
              {item.name}
            </Link>
          );
        })}

        {user && (
          <>
            <div className="px-4 py-2 mt-4">
              <h3 className="text-sm font-medium text-gray-500">Private Prompts</h3>
            </div>
            {/* Add private prompts here */}
          </>
        )}
      </nav>

      {/* User Section */}
      <div className="border-t">
        {user ? (
          <div className="p-4 space-y-2">
            <Link href="/prompts">
              <Button variant="ghost" className="w-full justify-start">
                <User className="mr-2 h-4 w-4" />
                My Prompts
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
            </Link>
            <Button
              variant="ghost"
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={() => logout()}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        ) : (
          <div className="p-4 space-y-2">
            <Link href="/login">
              <Button className="w-full">Login</Button>
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
  );
}