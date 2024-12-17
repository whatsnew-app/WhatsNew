import { Shell } from "@/components/layout/shell"
import { PromptForm } from "@/components/prompts/prompt-form"

export default function NewPromptPage() {
  return (
    <Shell>
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-8 text-2xl font-bold">Create New Prompt</h1>
        <PromptForm />
      </div>
    </Shell>
  )
}