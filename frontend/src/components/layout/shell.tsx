"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { MenuIcon, XIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sidebar } from "@/components/layout/sidebar"

interface ShellProps {
  children: React.ReactNode
  className?: string
}

// src/components/layout/shell.tsx

export function Shell({ children, className }: ShellProps) {
    const [sidebarOpen, setSidebarOpen] = useState(false)
  
    return (
      <div className="relative flex min-h-screen">
        {/* Mobile sidebar backdrop */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute left-4 top-4 z-50 lg:hidden"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? (
            <XIcon className="h-6 w-6" />
          ) : (
            <MenuIcon className="h-6 w-6" />
          )}
        </Button>
  
        {/* Sidebar */}
        <Sidebar
          className={cn(
            "fixed inset-y-0 left-0 z-40 -translate-x-full border-r bg-background transition-transform lg:relative lg:translate-x-0",
            sidebarOpen && "translate-x-0"
          )}
        />
  
        {/* Main content */}
        <main className={cn(
          "flex-1 overflow-auto p-4 lg:p-8",
          className
        )}>
          {children}
        </main>
      </div>
    )
  }