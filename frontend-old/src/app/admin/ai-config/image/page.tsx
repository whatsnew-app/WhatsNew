'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Plus, Pencil, Trash, Check, X } from 'lucide-react';
import { ImageConfig, ImageProvider } from '@/types/api';

export default function ImageConfigPage() {
  const [configs, setConfigs] = useState<ImageConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const response = await fetch('/api/v1/admin/ai-config/image');
      const data = await response.json();
      setConfigs(data);
    } catch (err) {
      setError('Failed to load configurations');
    } finally {
      setIsLoading(false);
    }
  };

  const setDefaultConfig = async (configId: string) => {
    try {
      await fetch(`/api/v1/admin/ai-config/image/${configId}/set-default`, {
        method: 'PUT',
      });
      loadConfigs();
    } catch (err) {
      setError('Failed to set default configuration');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Image Generation Configuration</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Configuration
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {configs.map((config) => (
          <Card key={config.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-semibold">
                {config.name}
                {config.is_default && (
                  <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    Default
                  </span>
                )}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={() => setIsEditing(config.id)}>
                  <Pencil className="h-4 w-4" />
                </Button>
                {!config.is_default && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setDefaultConfig(config.id)}
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                )}
                <Button variant="destructive" size="sm">
                  <Trash className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Provider
                  </label>
                  <p className="mt-1">{config.provider}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Model
                  </label>
                  <p className="mt-1">{config.model_name}</p>
                </div>
                {config.description && (
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <p className="mt-1 text-gray-600">{config.description}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}