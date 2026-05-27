import { RefreshCw, WandSparkles } from 'lucide-react'
import type { Editor } from 'tldraw'
import { generateInterface } from '../ai/api'
import { getSerializableShapes } from '../canvas/shapes'
import { useAppStore } from '../store/useAppStore'

interface PromptStripProps {
  editor: Editor
}

export function PromptStrip({ editor }: PromptStripProps) {
  const {
    prompt,
    selectedOnly,
    isGenerating,
    setPrompt,
    setSelectedOnly,
    setGeneratedUI,
    setIsGenerating,
    setLastShapes,
    setStatus,
  } = useAppStore()

  const regenerate = async () => {
    const shapes = getSerializableShapes(editor, selectedOnly)
    setLastShapes(shapes)
    setIsGenerating(true)
    setStatus(selectedOnly ? 'Regenerating selected region' : 'Regenerating full canvas')
    try {
      setGeneratedUI(await generateInterface({ shapes, prompt, selectedOnly }))
      setStatus('Preview updated')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <form
      className="prompt-strip"
      onSubmit={(event) => {
        event.preventDefault()
        void regenerate()
      }}
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
      <button type="submit" disabled={isGenerating}>
        <RefreshCw size={16} />
        <span>Update</span>
      </button>
    </form>
  )
}
