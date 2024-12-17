import { Shell } from "@/components/layout/shell"
import { NewsList } from "@/components/news/news-list"

export default function PromptPage({
  params,
}: {
  params: { id: string }
}) {
  return (
    <Shell>
      <NewsList promptId={params.id} />
    </Shell>
  )
}