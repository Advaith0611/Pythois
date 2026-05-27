import { Tldraw, useEditor } from 'tldraw'
import 'tldraw/tldraw.css'
import { Toaster } from 'react-hot-toast'
import { CanvasHints } from './components/CanvasHints'
import { CanvasToolbar } from './components/CanvasToolbar'
import { GeneratedRenderer } from './components/GeneratedRenderer'
import { PromptStrip } from './components/PromptStrip'
import './App.css'

function CanvasChrome() {
  const editor = useEditor()

  return (
    <>
      <CanvasToolbar editor={editor} />
      <PromptStrip editor={editor} />
      <CanvasHints />
    </>
  )
}

export default function App() {
  return (
    <main className="app-shell">
      <Toaster position="top-center" toastOptions={{ style: { background: '#101318', color: '#f5f7fb' } }} />
      <section className="canvas-stage">
        <Tldraw persistenceKey="pythios-spatial-ai">
          <CanvasChrome />
        </Tldraw>
      </section>
      <GeneratedRenderer />
    </main>
  )
}
