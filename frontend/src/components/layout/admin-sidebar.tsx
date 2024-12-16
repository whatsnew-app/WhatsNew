'use client';

import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { 
  Settings, 
  Database, 
  Terminal, 
  Image as ImageIcon, 
  Activity,
  CalendarDays,
  Gauge,
  FileText,
  ListChecks
} from 'lucide-react';

export function AdminSidebar() {
  const pathname = usePathname();
  
  const menuItems = [
    {
      title: 'AI Configuration',
      items: [
        {
          name: 'LLM Configuration',
          href: '/admin/ai-config/llm',
          icon: Terminal,
          description: 'Manage language model settings'
        },
        {
          name: 'Image Generation',
          href: '/admin/ai-config/image',
          icon: ImageIcon,
          description: 'Configure image generation models'
        }
      ]
    },
    {
      title: 'Content Management',
      items: [
        {
          name: 'Templates',
          href: '/admin/templates',
          icon: FileText,
          description: 'Manage prompt templates'
        }
      ]
    },
    {
      title: 'Task Management',
      items: [
        {
          name: 'Tasks',
          href: '/admin/tasks',
          icon: ListChecks,
          description: 'View and manage system tasks'
        },
        {
          name: 'News Generation',
          href: '/admin/tasks/news-generation',
          icon: CalendarDays,
          description: 'Trigger news generation'
        }
      ]
    },
    {
      title: 'System',
      items: [
        {
          name: 'System Stats',
          href: '/admin/stats',
          icon: Activity,
          description: 'View system statistics'
        },
        {
          name: 'Daily Stats',
          href: '/admin/stats/daily',
          icon: Gauge,
          description: 'View daily statistics'
        }
      ]
    }
  ];

  return (
    <div className="w-64 bg-gray-900 h-screen text-white p-6 overflow-y-auto">
      <div className="flex items-center space-x-2 mb-8">
        <Settings className="h-6 w-6" />
        <h1 className="text-xl font-bold">Admin Panel</h1>
      </div>

      <nav className="space-y-8">
        {menuItems.map((section, index) => (
          <div key={index}>
            <h2 className="text-xs uppercase tracking-wide text-gray-400 mb-3">
              {section.title}
            </h2>
            <div className="space-y-1">
              {section.items.map((item) => (
                <Link 
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-3 px-3 py-2 rounded-md transition-colors",
                    pathname === item.href 
                      ? "bg-blue-600 text-white" 
                      : "text-gray-300 hover:bg-gray-800 hover:text-white"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </div>
  );
}