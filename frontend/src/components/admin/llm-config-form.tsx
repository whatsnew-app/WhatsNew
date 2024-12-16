'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';
import type { LLMConfig, LLMProvider } from '@/types/api';

interface LLMConfigFormProps {
  isOpen: boolean;
  onClose: () => void;
  config?: LLMConfig;
  onSubmit: (data: any) => Promise<void>;
}

export function LLMConfigForm({ isOpen, onClose, config, onSubmit }: LLMConfigFormProps) {
  const [formData, setFormData] = useState({
    name: config?.name || '',
    description: config?.description || '',
    provider: config?.provider || 'openai',
    model_name: config?.model_name || '',
    api_key: config?.api_key || '',
    endpoint_url: config?.endpoint_url || '',
    parameters: config?.parameters || {},
    is_active: config?.is_active ?? true,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save configuration');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={config ? 'Edit LLM Configuration' : 'New LLM Configuration'}
      className="w-full max-w-2xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Provider</label>
            <select
              className="mt-1 block w-full rounded-md border border-gray-300 py-2 px-3"
              value={formData.provider}
              onChange={(e) => setFormData(prev => ({ ...prev, provider: e.target.value as LLMProvider }))}
              required
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Model Name</label>
            <Input
              value={formData.model_name}
              onChange={(e) => setFormData(prev => ({ ...prev, model_name: e.target.value }))}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">API Key</label>
            <Input
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData(prev => ({ ...prev, api_key: e.target.value }))}
              required
            />
          </div>

          {formData.provider === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Endpoint URL</label>
              <Input
                value={formData.endpoint_url}
                onChange={(e) => setFormData(prev => ({ ...prev, endpoint_url: e.target.value }))}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="mt-1 block w-full rounded-md border border-gray-300 py-2 px-3"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
              id="is_active"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
              Active
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Configuration'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}