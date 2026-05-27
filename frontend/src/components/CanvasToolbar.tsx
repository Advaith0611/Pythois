import { Bot, Braces, CircleDot, Eraser, MousePointer2, PenLine, Sparkles, Square, Type } from 'lucide-react'
import type { Editor } from 'tldraw'
import toast from 'react-hot-toast'
import { generateInterface } from '../ai/api'
import { getSerializableShapes } from '../canvas/shapes'
import { useAppStore } from '../store/useAppStore'

interface CanvasToolbarProps {
  editor: Editor
}

export function CanvasToolbar({ editor }: CanvasToolbarProps) {
  const {
    prompt,
    selectedOnly,
    isGenerating,
    setGeneratedUI,
    setIsGenerating,
    setLastShapes,
    setStatus,
  } = useAppStore()

  const setTool = (tool: string) => {
    editor.setCurrentTool(tool)
  }

  const generate = async () => {
    const shapes = getSerializableShapes(editor, selectedOnly)
    setLastShapes(shapes)
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
  }

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
