"use client"

import { useState } from "react"
import Image from "next/image"
import { format } from "date-fns"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface NewsCardProps {
  title: string
  content: string
  summary?: string | null
  publishedDate: string
  imageUrl?: string | null
  promptName: string
  className?: string
}

export function NewsCard({
  title,
  content,
  summary,
  publishedDate,
  imageUrl,
  promptName,
  className,
}: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            {format(new Date(publishedDate), "PPp")}
          </span>
          <span className="text-sm font-medium text-primary">
            {promptName}
          </span>
        </div>
        <h2 className="news-title">{title}</h2>
      </CardHeader>
      
      {imageUrl && (
        <div className="relative h-48 w-full">
          <Image
            src={imageUrl}
            alt={title}
            fill
            className="object-cover"
          />
        </div>
      )}
      
      <CardContent className="space-y-4">
        <div className={cn(
          "prose prose-sm dark:prose-invert max-w-none",
          !isExpanded && "line-clamp-3"
        )}>
          {isExpanded ? content : (summary || content)}
        </div>
      </CardContent>
      
      <CardFooter>
        <Button
          variant="ghost"
          className="w-full"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? "Show Less" : "Read More"}
        </Button>
      </CardFooter>
    </Card>
  )
}