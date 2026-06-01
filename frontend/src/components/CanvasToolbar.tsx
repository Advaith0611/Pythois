import { Bot, Braces, CircleDot, Eraser, FileUp, Globe2, ImagePlus, MousePointer2, PenLine, Sparkles, Square, Type, X } from 'lucide-react'
import { memo, useCallback, useRef, useState } from 'react'
import type { Editor } from 'tldraw'
import toast from 'react-hot-toast'
import { generateInterface } from '../ai/api'
import { getSerializableShapes } from '../canvas/shapes'
import { useAppStore } from '../store/useAppStore'
import { useRenderCounter } from '../canvas/performanceInstrumentation'
import type { EmbeddedCanvasObject, EmbeddedCanvasObjectKind } from '../types'

interface CanvasToolbarProps {
  editor: Editor
}

function createEmbeddedObjectId() {
  return `embed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function readFileAsDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

function fileKind(file: File): EmbeddedCanvasObjectKind {
  if (file.type.startsWith('image/')) return 'image'
  if (file.type === 'application/pdf') return 'pdf'
  return 'file'
}

function normalizeUrl(value: string) {
  const trimmed = value.trim()
  if (!trimmed) return null
  const withProtocol = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`

  try {
    return new URL(withProtocol).toString()
  } catch {
    return null
  }
}

function CanvasToolbarComponent({ editor }: CanvasToolbarProps) {
  useRenderCounter('CanvasToolbar')

  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const imageInputRef = useRef<HTMLInputElement | null>(null)
  const [isWebDialogOpen, setIsWebDialogOpen] = useState(false)
  const [webUrl, setWebUrl] = useState('')
  const prompt = useAppStore((state) => state.prompt)
  const selectedOnly = useAppStore((state) => state.selectedOnly)
  const isGenerating = useAppStore((state) => state.isGenerating)
  const addEmbeddedObject = useAppStore((state) => state.addEmbeddedObject)
  const setGeneratedUI = useAppStore((state) => state.setGeneratedUI)
  const setIsGenerating = useAppStore((state) => state.setIsGenerating)
  const setLastShapeCount = useAppStore((state) => state.setLastShapeCount)
  const setStatus = useAppStore((state) => state.setStatus)

  const setTool = useCallback((tool: string) => {
    editor.setCurrentTool(tool)
  }, [editor])

  const getDropPoint = useCallback(() => {
    const center = editor.screenToPage(editor.getViewportScreenCenter())
    return { x: center.x - 180, y: center.y - 120 }
  }, [editor])

  const addFiles = useCallback(async (files: FileList | null) => {
    if (!files?.length) return

    const point = getDropPoint()

    try {
      const objects = await Promise.all(
        Array.from(files).map(async (file, index): Promise<EmbeddedCanvasObject> => {
          const kind = fileKind(file)
          const dataUrl = await readFileAsDataUrl(file)

          return {
            id: createEmbeddedObjectId(),
            kind,
            x: point.x + index * 28,
            y: point.y + index * 28,
            w: kind === 'image' ? 360 : 420,
            h: kind === 'image' ? 260 : 300,
            title: file.name,
            mimeType: file.type || 'Unknown type',
            size: file.size,
            dataUrl,
            createdAt: new Date().toISOString(),
          }
        }),
      )

      objects.forEach(addEmbeddedObject)
      toast.success(objects.length === 1 ? 'File embedded' : `${objects.length} files embedded`)
    } catch (error) {
      console.error(error)
      toast.error('Could not embed file')
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }, [addEmbeddedObject, getDropPoint])

  const addWebpage = useCallback(() => {
    const url = normalizeUrl(webUrl)
    if (!url) {
      toast.error('Enter a valid URL')
      return
    }

    const point = getDropPoint()
    addEmbeddedObject({
      id: createEmbeddedObjectId(),
      kind: 'webpage',
      x: point.x,
      y: point.y,
      w: 560,
      h: 380,
      title: new URL(url).hostname.replace(/^www\./, ''),
      url,
      createdAt: new Date().toISOString(),
    })
    setWebUrl('')
    setIsWebDialogOpen(false)
    toast.success('Webpage embedded')
  }, [addEmbeddedObject, getDropPoint, webUrl])

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
      <div className="toolbar-brand">
        <img src="/logo.png" alt="Pythios" />
      </div>
      <span className="toolbar-divider" />
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
      <input
        ref={fileInputRef}
        type="file"
        hidden
        multiple
        accept=".pdf,.txt,.md,.markdown,.csv,.json,.ts,.tsx,.js,.jsx,.py,.html,.css"
        onChange={(event) => void addFiles(event.target.files)}
      />
      <input
        ref={imageInputRef}
        type="file"
        hidden
        multiple
        accept="image/*"
        onChange={(event) => void addFiles(event.target.files)}
      />
      <button type="button" onClick={() => fileInputRef.current?.click()} title="Upload file">
        <FileUp size={18} />
      </button>
      <button type="button" onClick={() => imageInputRef.current?.click()} title="Upload image">
        <ImagePlus size={18} />
      </button>
      <button type="button" onClick={() => setIsWebDialogOpen(true)} title="Embed webpage">
        <Globe2 size={18} />
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
      {isWebDialogOpen ? (
        <form
          className="web-embed-popover"
          onSubmit={(event) => {
            event.preventDefault()
            addWebpage()
          }}
        >
          <button type="button" className="popover-close" title="Close" onClick={() => setIsWebDialogOpen(false)}>
            <X size={15} />
          </button>
          <label htmlFor="web-embed-url">Webpage URL</label>
          <div>
            <input
              id="web-embed-url"
              value={webUrl}
              onChange={(event) => setWebUrl(event.target.value)}
              placeholder="https://example.com"
              autoFocus
            />
            <button type="submit">
              <Globe2 size={15} />
              <span>Add</span>
            </button>
          </div>
          <p>Sites with X-Frame-Options or restrictive CSP will show an embed warning.</p>
        </form>
      ) : null}
    </div>
  )
}

export const CanvasToolbar = memo(CanvasToolbarComponent)
