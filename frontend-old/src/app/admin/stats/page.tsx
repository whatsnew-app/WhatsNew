'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Activity, 
  Users, 
  FileText, 
  Calendar,
  TrendingUp,
  Clock
} from 'lucide-react';

interface SystemStats {
  total_users: number;
  total_prompts: number;
  total_articles: number;
  active_tasks: number;
  daily_stats: {
    date: string;
    articles_generated: number;
    processing_time: number;
  }[];
}

export default function StatsPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [statsResponse, dailyResponse] = await Promise.all([
        fetch('/api/v1/admin/stats'),
        fetch('/api/v1/admin/stats/daily')
      ]);
      const [statsData, dailyData] = await Promise.all([
        statsResponse.json(),
        dailyResponse.json()
      ]);
      setStats({ ...statsData, daily_stats: dailyData });
    } catch (err) {
      setError('Failed to load statistics');
    } finally {
      setIsLoading(false);
    }
  };

  const statsCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      icon: Users,
      description: 'Active users on the platform'
    },
    {
      title: 'Total Prompts',
      value: stats?.total_prompts || 0,
      icon: FileText,
      description: 'Created prompt templates'
    },
    {
      title: 'Total Articles',
      value: stats?.total_articles || 0,
      icon: Activity,
      description: 'Generated news articles'
    },
    {
      title: 'Active Tasks',
      value: stats?.active_tasks || 0,
      icon: Calendar,
      description: 'Currently running tasks'
    }
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">System Statistics</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? (
                  <div className="h-8 w-24 animate-pulse bg-gray-200 rounded" />
                ) : (
                  stat.value.toLocaleString()
                )}
              </div>
              <p className="text-xs text-gray-600 mt-1">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {stats?.daily_stats && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Daily Performance</h2>
          <div className="grid grid-cols-1 gap-6">
            {stats.daily_stats.map((day, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-sm">
                    {new Date(day.date).toLocaleDateString()}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="text-sm font-medium">Articles Generated</p>
                        <p className="text-2xl font-bold">{day.articles_generated}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium">Avg. Processing Time</p>
                        <p className="text-2xl font-bold">{day.processing_time.toFixed(2)}s</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}