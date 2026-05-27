import { memo, useCallback, useRef, useState } from 'react'
import { Tldraw, type Editor } from 'tldraw'
import { CanvasHints } from '../components/CanvasHints'
import { CanvasToolbar } from '../components/CanvasToolbar'
import { PromptStrip } from '../components/PromptStrip'
import {
  useBoundEditorHistory,
  useDisableTldrawPersistenceCleanup,
  usePerformanceInstrumentation,
  useRenderCounter,
} from './performanceInstrumentation'
import { useCanvasSizeGuard } from './useCanvasSizeGuard'

function CanvasWorkspaceComponent() {
  useRenderCounter('CanvasWorkspace')

  const containerRef = useRef<HTMLElement | null>(null)
  const editorRef = useRef<Editor | null>(null)
  const [editor, setEditor] = useState<Editor | null>(null)

  useCanvasSizeGuard(containerRef)
  useDisableTldrawPersistenceCleanup()
  usePerformanceInstrumentation(editorRef)
  useBoundEditorHistory(editorRef)

  const handleMount = useCallback((mountedEditor: Editor) => {
    editorRef.current = mountedEditor
    setEditor(mountedEditor)
    mountedEditor.setCurrentTool('draw')

    return () => {
      editorRef.current = null
      setEditor(null)
    }
  }, [])

  return (
    <section className="canvas-stage" ref={containerRef}>
      <div className="tldraw-viewport">
        <Tldraw
          className="pythios-tldraw"
          autoFocus
          hideUi
          onMount={handleMount}
        />
      </div>
      {editor ? (
        <div className="canvas-overlays">
          <CanvasToolbar editor={editor} />
          <PromptStrip editor={editor} />
          <CanvasHints />
        </div>
      ) : null}
    </section>
  )
}

export const CanvasWorkspace = memo(CanvasWorkspaceComponent)
