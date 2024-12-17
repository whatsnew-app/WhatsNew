"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import { format } from "date-fns"
import { CalendarIcon, Settings, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/stores/auth-store"
import api from "@/lib/api"

interface SidebarProps {
  className?: string
}

interface Prompt {
  id: string
  name: string
  type: "public" | "private" | "internal"
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(true)
  
  const { user, logout } = useAuthStore()

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setIsLoadingPrompts(true)
        const response = await api.get('/api/v1/public/prompts')
        setPrompts(response.data)
      } catch (error) {
        console.error('Failed to fetch prompts:', error)
      } finally {
        setIsLoadingPrompts(false)
      }
    }

    fetchPrompts()
  }, [])

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

  return (
    <aside className={cn(
      "flex h-screen w-72 flex-col bg-background",
      className
    )}>
      {/* Logo */}
      <div className="border-b px-6 py-4">
        <Link href="/" className="flex items-center space-x-2">
          <h1 className="text-xl font-bold">WhatsNews AI</h1>
        </Link>
      </div>

      {/* Date selection */}
      <div className="border-b px-6 py-4">
        <Button
          variant="outline"
          className="w-full justify-start text-left font-normal"
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {format(selectedDate, "PPP")}
        </Button>
      </div>

      {/* Prompts list */}
      <div className="flex-1 overflow-auto px-4 py-6">
        <nav className="flex flex-col space-y-1">
          {isLoadingPrompts ? (
            <div className="flex items-center justify-center py-4">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : (
            prompts.map((prompt) => (
              <Link
                key={prompt.id}
                href={`/prompts/${prompt.id}`}
                className={cn(
                  "px-2 py-1.5 text-sm font-medium rounded-md",
                  pathname === `/prompts/${prompt.id}`
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                {prompt.name}
              </Link>
            ))
          )}
        </nav>
      </div>

      {/* Bottom actions */}
      <div className="mt-auto border-t px-6 py-4">
        {user ? (
          <div className="flex flex-col space-y-2">
            <Link href="/prompts">
              <Button variant="ghost" className="w-full justify-start">
                My Prompts
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
            </Link>
            <Button 
              variant="ghost" 
              className="w-full justify-start text-destructive"
              onClick={handleLogout}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        ) : (
          <div className="flex flex-col space-y-2">
            <Link href="/auth/login">
              <Button className="w-full">Login</Button>
            </Link>
            <Link href="/auth/signup">
              <Button variant="outline" className="w-full">
                Sign Up
              </Button>
            </Link>
          </div>
        )}
      </div>
    </aside>
  )
}