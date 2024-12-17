"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { usePromptStore, Prompt } from "@/stores/prompt-store"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { AlertCircle } from "lucide-react"
import api from "@/lib/api"

interface PromptFormProps {
  initialData?: Partial<Prompt>
  onSuccess?: () => void
}

interface Template {
  id: string
  name: string
}

export function PromptForm({ initialData, onSuccess }: PromptFormProps) {
  const [name, setName] = useState(initialData?.name || "")
  const [content, setContent] = useState(initialData?.content || "")
  const [type, setType] = useState<Prompt["type"]>(initialData?.type || "public")
  const [generateImage, setGenerateImage] = useState(initialData?.generate_image || false)
  const [displayStyle, setDisplayStyle] = useState<Prompt["display_style"]>(
    initialData?.display_style || "card"
  )
  const [newsSources, setNewsSources] = useState<string[]>(initialData?.news_sources || [])
  const [templateId, setTemplateId] = useState(initialData?.template_id || "")
  const [templates, setTemplates] = useState<Template[]>([])
  const [error, setError] = useState<string | null>(null)
  
  const router = useRouter()
  const { createPrompt, updatePrompt, isLoading } = usePromptStore()

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await api.get('/api/v1/admin/templates')
        setTemplates(response.data)
      } catch (error) {
        console.error('Failed to fetch templates:', error)
      }
    }

    fetchTemplates()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const promptData = {
      name,
      content,
      type,
      generate_image: generateImage,
      display_style: displayStyle,
      news_sources: newsSources,
      template_id: templateId,
    }

    try {
      if (initialData?.id) {
        await updatePrompt(initialData.id, promptData)
      } else {
        await createPrompt(promptData)
      }

      onSuccess?.()
      router.push('/prompts')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save prompt')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <p>{error}</p>
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="content">Content</Label>
        <Textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          className="min-h-[200px]"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="type">Type</Label>
        <Select value={type} onValueChange={(value: Prompt["type"]) => setType(value)}>
          <SelectTrigger id="type">
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="public">Public</SelectItem>
            <SelectItem value="internal">Internal</SelectItem>
            <SelectItem value="private">Private</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="template">Template</Label>
        <Select value={templateId} onValueChange={setTemplateId}>
          <SelectTrigger id="template">
            <SelectValue placeholder="Select template" />
          </SelectTrigger>
          <SelectContent>
            {templates.map((template) => (
              <SelectItem key={template.id} value={template.id}>
                {template.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="displayStyle">Display Style</Label>
        <Select
          value={displayStyle}
          onValueChange={(value: Prompt["display_style"]) => setDisplayStyle(value)}
        >
          <SelectTrigger id="displayStyle">
            <SelectValue placeholder="Select display style" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="card">Card</SelectItem>
            <SelectItem value="rectangle">Rectangle</SelectItem>
            <SelectItem value="highlight">Highlight</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="generateImage"
          checked={generateImage}
          onCheckedChange={setGenerateImage}
        />
        <Label htmlFor="generateImage">Generate Image</Label>
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Saving..." : initialData?.id ? "Update Prompt" : "Create Prompt"}
      </Button>
    </form>
  )
}