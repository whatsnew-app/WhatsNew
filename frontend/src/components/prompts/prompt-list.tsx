"use client"

import { useEffect } from "react"
import Link from "next/link"
import { usePromptStore } from "@/stores/prompt-store"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { PencilIcon, TrashIcon, PlusCircle } from "lucide-react"
import { format } from "date-fns"

export function PromptList() {
  const { prompts, isLoading, error, fetchPrompts, deletePrompt } = usePromptStore()

  useEffect(() => {
    fetchPrompts(true)
  }, [fetchPrompts])

  if (error) {
    return (
      <div className="flex items-center justify-center p-8 text-destructive">
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Prompts</h1>
        <Link href="/prompts/new">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Prompt
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-8">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : prompts.length === 0 ? (
        <div className="flex flex-col items-center justify-center space-y-4 p-8 text-center">
          <p className="text-muted-foreground">No prompts found</p>
          <Link href="/prompts/new">
            <Button>Create your first prompt</Button>
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {prompts.map((prompt) => (
            <Card key={prompt.id}>
              <CardHeader>
                <CardTitle>{prompt.name}</CardTitle>
                <CardDescription>
                  Created {format(new Date(prompt.created_at), "PPP")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {prompt.content}
                </p>
                <div className="mt-4 flex items-center space-x-2">
                  <span className="text-xs text-muted-foreground">Type:</span>
                  <span className="text-xs font-medium capitalize">{prompt.type}</span>
                </div>
              </CardContent>
              <CardFooter className="justify-end space-x-2">
                <Link href={`/prompts/${prompt.id}/edit`}>
                  <Button variant="outline" size="sm">
                    <PencilIcon className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                </Link>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" size="sm">
                      <TrashIcon className="mr-2 h-4 w-4" />
                      Delete
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        Delete prompt &quot;{prompt.name}&quot;?
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete the
                        prompt and all associated news articles.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        onClick={() => deletePrompt(prompt.id).catch((error) => {
                          console.error('Failed to delete prompt:', error)
                        })}
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}