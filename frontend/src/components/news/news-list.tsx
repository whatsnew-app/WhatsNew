"use client"

import { useEffect } from "react"
import { useNewsStore } from "@/stores/news-store"
import { NewsCard } from "@/components/news/news-card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"

interface NewsListProps {
  promptId?: string
}

export function NewsList({ promptId }: NewsListProps) {
  const { articles, isLoading, error, fetchNews } = useNewsStore()

  useEffect(() => {
    fetchNews(true)
  }, [fetchNews])

  if (isLoading && articles.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (articles.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-muted-foreground">
        <p>No articles found</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {articles.map((article) => (
        <NewsCard
          key={article.id}
          title={article.title}
          content={article.content}
          summary={article.summary}
          publishedDate={article.published_date}
          imageUrl={article.image_url}
          promptName={article.prompt_name}
        />
      ))}
    </div>
  )
}