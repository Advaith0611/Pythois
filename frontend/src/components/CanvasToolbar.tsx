import { Bot, Braces, CircleDot, Eraser, MousePointer2, PenLine, Sparkles, Square, Type } from 'lucide-react'
import { memo, useCallback } from 'react'
import type { Editor } from 'tldraw'
import toast from 'react-hot-toast'
import { generateInterface } from '../ai/api'
import { getSerializableShapes } from '../canvas/shapes'
import { useAppStore } from '../store/useAppStore'
import { useRenderCounter } from '../canvas/performanceInstrumentation'

interface CanvasToolbarProps {
  editor: Editor
}

function CanvasToolbarComponent({ editor }: CanvasToolbarProps) {
  useRenderCounter('CanvasToolbar')

  const prompt = useAppStore((state) => state.prompt)
  const selectedOnly = useAppStore((state) => state.selectedOnly)
  const isGenerating = useAppStore((state) => state.isGenerating)
  const setGeneratedUI = useAppStore((state) => state.setGeneratedUI)
  const setIsGenerating = useAppStore((state) => state.setIsGenerating)
  const setLastShapeCount = useAppStore((state) => state.setLastShapeCount)
  const setStatus = useAppStore((state) => state.setStatus)

  const setTool = useCallback((tool: string) => {
    editor.setCurrentTool(tool)
  }, [editor])

  const generate = useCallback(async () => {
    const shapes = getSerializableShapes(editor, selectedOnly)
    setLastShapeCount(shapes.length)
    setIsGenerating(true)
    setStatus(shapes.length ? `Parsing ${shapes.length} canvas objects` : 'Generating starter interface')

    try {
      const ui = await generateInterface({ shapes, prompt, selectedOnly })
      setGeneratedUI(ui)
      setStatus(ui.source === 'backend' ? 'Generated through backend' : 'Generated locally')
      toast.success(ui.source === 'backend' ? 'Interface generated' : 'Generated locally')
    } catch (error) {
      console.error(error)
      setStatus('Generation failed')
      toast.error('Generation failed')
    } finally {
      setIsGenerating(false)
    }
  }, [editor, prompt, selectedOnly, setGeneratedUI, setIsGenerating, setLastShapeCount, setStatus])

  return (
    <div className="canvas-toolbar" aria-label="Spatial tools">
      <button type="button" onClick={() => setTool('select')} title="Select">
        <MousePointer2 size={18} />
      </button>
      <button type="button" onClick={() => setTool('draw')} title="Draw">
        <PenLine size={18} />
      </button>
      <button type="button" onClick={() => setTool('geo')} title="Shape">
        <Square size={18} />
      </button>
      <button type="button" onClick={() => setTool('text')} title="Text">
        <Type size={18} />
      </button>
      <button type="button" onClick={() => setTool('arrow')} title="Arrow">
        <CircleDot size={18} />
      </button>
      <button type="button" onClick={() => setTool('eraser')} title="Erase">
        <Eraser size={18} />
      </button>
      <span className="toolbar-divider" />
      <button type="button" onClick={generate} className="generate-button" disabled={isGenerating} title="Generate interface">
        {isGenerating ? <Braces size={18} /> : <Sparkles size={18} />}
        <span>{isGenerating ? 'Generating' : 'Generate'}</span>
      </button>
      <div className="ai-badge" title="Backend with local fallback">
        <Bot size={16} />
        AI
      </div>
    </div>
  )
}

export const CanvasToolbar = memo(CanvasToolbarComponent)
