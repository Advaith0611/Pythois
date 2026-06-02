import { WandSparkles } from 'lucide-react'
import { memo } from 'react'
import type { Editor } from 'tldraw'
import { useAppStore } from '../store/useAppStore'
import { useRenderCounter } from '../canvas/performanceInstrumentation'

interface PromptStripProps {
  editor: Editor
}

function PromptStripComponent({ editor }: PromptStripProps) {
  void editor
  useRenderCounter('PromptStrip')

  const prompt = useAppStore((state) => state.prompt)
  const selectedOnly = useAppStore((state) => state.selectedOnly)
  const setPrompt = useAppStore((state) => state.setPrompt)
  const setSelectedOnly = useAppStore((state) => state.setSelectedOnly)

  return (
    <div
      className="prompt-strip"
    >
      <WandSparkles size={18} />
      <input
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Add intent, e.g. SaaS analytics dashboard with filters and a billing table"
        aria-label="Spatial intent"
      />
      <label className="selected-toggle">
        <input
          type="checkbox"
          checked={selectedOnly}
          onChange={(event) => setSelectedOnly(event.target.checked)}
        />
        <span>Selected</span>
      </label>
    </div>
  )
}

export const PromptStrip = memo(PromptStripComponent)
