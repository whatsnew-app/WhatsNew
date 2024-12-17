'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Pencil, Trash, Check } from 'lucide-react';
import { LLMConfigForm } from '@/components/admin/llm-config-form';
import type { LLMConfig } from '@/types/api';

export default function LLMConfigPage() {
  const [configs, setConfigs] = useState<LLMConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<LLMConfig | undefined>();

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const response = await fetch('/api/v1/admin/ai-config/llm');
      const data = await response.json();
      setConfigs(data);
    } catch (err) {
      setError('Failed to load configurations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (data: any) => {
    try {
      const url = selectedConfig 
        ? `/api/v1/admin/ai-config/llm/${selectedConfig.id}`
        : '/api/v1/admin/ai-config/llm';
      
      const response = await fetch(url, {
        method: selectedConfig ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to save configuration');
      }

      await loadConfigs();
      setIsFormOpen(false);
      setSelectedConfig(undefined);
    } catch (err: any) {
      throw new Error(err.message || 'Failed to save configuration');
    }
  };

  const handleDelete = async (configId: string) => {
    if (!confirm('Are you sure you want to delete this configuration?')) return;

    try {
      await fetch(`/api/v1/admin/ai-config/llm/${configId}`, {
        method: 'DELETE',
      });
      await loadConfigs();
    } catch (err) {
      setError('Failed to delete configuration');
    }
  };

  const openEditForm = (config: LLMConfig) => {
    setSelectedConfig(config);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setSelectedConfig(undefined);
  };

  return (
    <>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">LLM Configuration</h1>
          <Button onClick={() => setIsFormOpen(true)}>
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
                <CardTitle className="text-lg font-semibold flex items-center">
                  {config.name}
                  {config.is_default && (
                    <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Default
                    </span>
                  )}
                  {!config.is_active && (
                    <span className="ml-2 text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
                      Inactive
                    </span>
                  )}
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" onClick={() => openEditForm(config)}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(config.id)}>
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

      <LLMConfigForm
        isOpen={isFormOpen}
        onClose={closeForm}
        config={selectedConfig}
        onSubmit={handleSubmit}
      />
    </>
  );
}