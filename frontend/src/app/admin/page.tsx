'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Users, FileText, Calendar } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPrompts: 0,
    totalArticles: 0,
    activeTasks: 0,
  });

  useEffect(() => {
    // Fetch stats from API
    fetch('/api/v1/admin/stats')
      .then(res => res.json())
      .catch(err => console.error('Failed to load stats:', err));
  }, []);

  const cards = [
    {
      title: 'Total Users',
      value: stats.totalUsers,
      icon: Users,
    },
    {
      title: 'Total Prompts',
      value: stats.totalPrompts,
      icon: FileText,
    },
    {
      title: 'Total Articles',
      value: stats.totalArticles,
      icon: Activity,
    },
    {
      title: 'Active Tasks',
      value: stats.activeTasks,
      icon: Calendar,
    },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <card.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}