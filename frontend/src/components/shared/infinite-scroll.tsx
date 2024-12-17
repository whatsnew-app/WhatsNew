"use client"

import { useEffect, useRef, useCallback } from 'react'

interface InfiniteScrollProps {
  children: React.ReactNode
  loading: boolean
  hasMore: boolean
  onLoadMore: () => void
  className?: string
}

export function InfiniteScroll({
  children,
  loading,
  hasMore,
  onLoadMore,
  className,
}: InfiniteScrollProps) {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const loadingRef = useRef<HTMLDivElement>(null)

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const target = entries[0]
      if (target.isIntersecting && hasMore && !loading) {
        onLoadMore()
      }
    },
    [hasMore, loading, onLoadMore]
  )

  useEffect(() => {
    const options = {
      root: null,
      rootMargin: "20px",
      threshold: 0,
    }

    observerRef.current = new IntersectionObserver(handleObserver, options)

    if (loadingRef.current) {
      observerRef.current.observe(loadingRef.current)
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [handleObserver])

  return (
    <div className={className}>
      {children}
      <div ref={loadingRef} className="h-10">
        {loading && (
          <div className="flex items-center justify-center p-4">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        )}
      </div>
    </div>
  )
}