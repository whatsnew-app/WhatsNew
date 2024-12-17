import { Shell } from "@/components/layout/shell"
import { NewsList } from "@/components/news/news-list"

export default function HomePage() {
  return (
    <Shell>
      <NewsList />
    </Shell>
  )
}