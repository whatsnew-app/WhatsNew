'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/main-layout';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu';
import { ChevronDown, Save, Trash } from 'lucide-react';
import { promptApi } from '@/lib/api/prompt';
import type { Prompt, PromptUpdate } from '@/types/prompt';

export default function PromptPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<PromptUpdate>({
    name: '',
    content: '',
    type: 'public',
    news_sources: [],
    display_style: 'card'
  });

  useEffect(() => {
    if (params.id !== 'new') {
      loadPrompt();
    } else {
      setIsLoading(false);
    }
  }, [params.id]);

  const loadPrompt = async () => {
    try {
      setIsLoading(true);
      const data = await promptApi.getPrompts({ id: params.id });
      setPrompt(data[0]);
      setFormData({
        name: data[0].name,
        content: data[0].content,
        type: data[0].type,
        news_sources: data[0].news_sources,
        display_style: data[0].display_style
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load prompt');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSaving(true);

    try {
      if (params.id === 'new') {
        await promptApi.createPrompt(formData as any);
      } else {
        await promptApi.updatePrompt(params.id, formData);
      }
      router.push('/prompts');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save prompt');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this prompt?')) return;
    
    try {
      await promptApi.deletePrompt(params.id);
      router.push('/prompts');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete prompt');
    }
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">
            {params.id === 'new' ? 'Create Prompt' : 'Edit Prompt'}
          </h1>
          {params.id !== 'new' && (
            <Button variant="destructive" onClick={handleDelete}>
              <Trash className="mr-2 h-4 w-4" />
              Delete Prompt
            </Button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Prompt Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Content</label>
                <textarea
                  className="w-full h-32 rounded-md border border-gray-200 p-2"
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  required
                />
              </div>

              <div className="flex gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Type</label>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline">
                        {formData.type}
                        <ChevronDown className="ml-2 h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, type: 'public' }))}>
                        Public
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, type: 'internal' }))}>
                        Internal
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, type: 'private' }))}>
                        Private
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Display Style</label>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline">
                        {formData.display_style}
                        <ChevronDown className="ml-2 h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, display_style: 'card' }))}>
                        Card
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, display_style: 'rectangle' }))}>
                        Rectangle
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setFormData(prev => ({ ...prev, display_style: 'highlight' }))}>
                        Highlight
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">News Sources</label>
                <div className="flex flex-wrap gap-2">
                  <Input
                    placeholder="Add news source URL"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        const value = (e.target as HTMLInputElement).value.trim();
                        if (value) {
                          setFormData(prev => ({
                            ...prev,
                            news_sources: [...prev.news_sources, value]
                          }));
                          (e.target as HTMLInputElement).value = '';
                        }
                      }
                    }}
                  />
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {formData.news_sources.map((source, index) => (
                    <div
                      key={index}
                      className="bg-gray-100 px-3 py-1 rounded-full flex items-center gap-2"
                    >
                      <span className="text-sm">{source}</span>
                      <button
                        type="button"
                        className="text-gray-500 hover:text-red-500"
                        onClick={() => {
                          setFormData(prev => ({
                            ...prev,
                            news_sources: prev.news_sources.filter((_, i) => i !== index)
                          }));
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/prompts')}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSaving}>
                  <Save className="mr-2 h-4 w-4" />
                  {isSaving ? 'Saving...' : 'Save Prompt'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}