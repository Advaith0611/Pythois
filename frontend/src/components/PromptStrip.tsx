import { RefreshCw, WandSparkles } from 'lucide-react'
import { memo, useCallback } from 'react'
import type { Editor } from 'tldraw'
import { generateInterface } from '../ai/api'
import { getSerializableShapes } from '../canvas/shapes'
import { useAppStore } from '../store/useAppStore'
import { useRenderCounter } from '../canvas/performanceInstrumentation'

interface PromptStripProps {
  editor: Editor
}

function PromptStripComponent({ editor }: PromptStripProps) {
  useRenderCounter('PromptStrip')

  const prompt = useAppStore((state) => state.prompt)
  const selectedOnly = useAppStore((state) => state.selectedOnly)
  const isGenerating = useAppStore((state) => state.isGenerating)
  const setPrompt = useAppStore((state) => state.setPrompt)
  const setSelectedOnly = useAppStore((state) => state.setSelectedOnly)
  const setGeneratedUI = useAppStore((state) => state.setGeneratedUI)
  const setIsGenerating = useAppStore((state) => state.setIsGenerating)
  const setLastShapeCount = useAppStore((state) => state.setLastShapeCount)
  const setStatus = useAppStore((state) => state.setStatus)

  const regenerate = useCallback(async () => {
    const shapes = getSerializableShapes(editor, selectedOnly)
    setLastShapeCount(shapes.length)
    setIsGenerating(true)
    setStatus(selectedOnly ? 'Regenerating selected region' : 'Regenerating full canvas')
    try {
      setGeneratedUI(await generateInterface({ shapes, prompt, selectedOnly }))
      setStatus('Preview updated')
    } finally {
      setIsGenerating(false)
    }
  }, [editor, prompt, selectedOnly, setGeneratedUI, setIsGenerating, setLastShapeCount, setStatus])

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

export const PromptStrip = memo(PromptStripComponent)
