// src/components/layout/sidebar.tsx
'use client';

import React, { useMemo } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { DatePicker } from '@/components/ui/date-picker';
import {
  LogOut,
  Settings,
  User,
  Home,
  BookOpen,
  Briefcase,
  Flask,
  Rocket,
  FileText,
  PlusCircle,
  Terminal,
  Image as ImageIcon,
  Activity,
  ListChecks,
  LayoutDashboard
} from 'lucide-react';

interface SidebarProps {
  onDateChange?: (date: Date | undefined) => void;
  selectedDate?: Date;
}

export function Sidebar({ onDateChange, selectedDate }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();

  // Memoized navigation items to prevent unnecessary recalculations
  const navigationStructure = useMemo(() => ({
    public: [
      { name: 'Latest News', href: '/', icon: Home },
      { name: 'Politics', href: '/politics', icon: BookOpen },
      { name: 'Finance', href: '/finance', icon: Briefcase },
      { name: 'Science', href: '/science', icon: Flask },
      { name: 'Startups', href: '/startups', icon: Rocket },
    ],
    private: [
      { name: 'My News Feed', href: '/news/my', icon: FileText },
      { name: 'My Prompts', href: '/prompts', icon: PlusCircle },
    ],
    admin: [
      {
        title: 'Dashboard',
        items: [
          { name: 'Overview', href: '/admin', icon: LayoutDashboard },
          { name: 'Statistics', href: '/admin/stats', icon: Activity },
        ]
      },
      {
        title: 'AI Configuration',
        items: [
          { name: 'LLM Settings', href: '/admin/ai-config/llm', icon: Terminal },
          { name: 'Image Generation', href: '/admin/ai-config/image', icon: ImageIcon },
        ]
      },
      {
        title: 'Management',
        items: [
          { name: 'Templates', href: '/admin/templates', icon: FileText },
          { name: 'Tasks', href: '/admin/tasks', icon: ListChecks },
        ]
      }
    ]
  }), []);

  // Navigation item renderer
  const renderNavItem = (item: { name: string; href: string; icon: any }) => {
    const Icon = item.icon;
    return (
      <Link
        key={item.href}
        href={item.href}
        className={cn(
          "flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors",
          pathname === item.href && "bg-gray-100 text-blue-600 font-medium"
        )}
      >
        <Icon className="mr-3 h-4 w-4" />
        {item.name}
      </Link>
    );
  };

  return (
    <div className="w-64 bg-white shadow-lg h-full flex flex-col">
      {/* Brand */}
      <div className="p-4 flex items-center space-x-2 border-b">
        <Link href="/" className="flex items-center space-x-2">
          <Home className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold">WhatsNew!</h1>
        </Link>
      </div>

      {/* Date Picker */}
      <div className="p-4 border-b">
        <DatePicker
          date={selectedDate}
          onChange={onDateChange}
        />
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {/* Public Section */}
        <div className="mb-6">
          <div className="px-4 mb-2">
            <h3 className="text-sm font-medium text-gray-500">News Categories</h3>
          </div>
          {navigationStructure.public.map(renderNavItem)}
        </div>

        {/* Private Section - Only for authenticated users */}
        {isAuthenticated && (
          <div className="mb-6">
            <div className="px-4 mb-2">
              <h3 className="text-sm font-medium text-gray-500">Personal</h3>
            </div>
            {navigationStructure.private.map(renderNavItem)}
          </div>
        )}

        {/* Admin Section - Only for superusers */}
        {user?.is_superuser && (
          <>
            {navigationStructure.admin.map((section, index) => (
              <div key={index} className="mb-6">
                <div className="px-4 mb-2">
                  <h3 className="text-sm font-medium text-gray-500">{section.title}</h3>
                </div>
                {section.items.map(renderNavItem)}
              </div>
            ))}
          </>
        )}
      </nav>

      {/* User Section */}
      <div className="border-t p-4">
        {isAuthenticated ? (
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <User className="h-6 w-6 text-gray-400" />
              <div className="flex-1">
                <p className="text-sm font-medium">{user?.full_name || 'User'}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
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
          <div className="space-y-2">
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