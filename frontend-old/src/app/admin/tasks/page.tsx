'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Play, Trash, AlertCircle } from 'lucide-react';
import type { TaskResponse, TaskStatus } from '@/types/api';

const getStatusColor = (status: TaskStatus) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'in_progress':
      return 'bg-blue-100 text-blue-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/v1/admin/tasks');
      const data = await response.json();
      setTasks(data.tasks);
    } catch (err) {
      setError('Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const triggerNewsGeneration = async () => {
    try {
      await fetch('/api/v1/admin/tasks/news-generation', {
        method: 'POST'
      });
      loadTasks();
    } catch (err) {
      setError('Failed to trigger news generation');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Task Management</h1>
        <div className="space-x-4">
          <Button onClick={triggerNewsGeneration}>
            <Play className="mr-2 h-4 w-4" />
            Generate News
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Task
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {tasks.map((task) => (
          <Card key={task.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-lg font-semibold">
                  {task.name}
                  <span className={`ml-2 text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}>
                    {task.status}
                  </span>
                </CardTitle>
                <p className="text-sm text-gray-500">{task.type}</p>
              </div>
              <Button variant="destructive" size="sm">
                <Trash className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {task.error_message && (
                  <div className="flex items-start space-x-2 text-red-600">
                    <AlertCircle className="h-5 w-5 mt-0.5" />
                    <span>{task.error_message}</span>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="font-medium">Created At</label>
                    <p>{new Date(task.created_at).toLocaleString()}</p>
                  </div>
                  {task.started_at && (
                    <div>
                      <label className="font-medium">Started At</label>
                      <p>{new Date(task.started_at).toLocaleString()}</p>
                    </div>
                  )}
                  {task.completed_at && (
                    <div>
                      <label className="font-medium">Completed At</label>
                      <p>{new Date(task.completed_at).toLocaleString()}</p>
                    </div>
                  )}
                  {task.next_run_at && (
                    <div>
                      <label className="font-medium">Next Run</label>
                      <p>{new Date(task.next_run_at).toLocaleString()}</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}