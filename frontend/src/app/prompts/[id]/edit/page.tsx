import { Shell } from "@/components/layout/shell"
import { PromptForm } from "@/components/prompts/prompt-form"

export default function EditPromptPage({
  params,
}: {
  params: { id: string }
}) {
  return (
    <Shell>
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-8 text-2xl font-bold">Edit Prompt</h1>
        <PromptForm initialData={{ id: params.id }} />
      </div>
    </Shell>
  )
}