import 'tldraw/tldraw.css'
import { Toaster } from 'react-hot-toast'
import { CanvasWorkspace } from './canvas/CanvasWorkspace'
import { GeneratedRenderer } from './components/GeneratedRenderer'
import './App.css'

export default function App() {
  return (
    <main className="app-shell">
      <Toaster position="top-center" toastOptions={{ style: { background: '#101318', color: '#f5f7fb' } }} />
      <CanvasWorkspace />
      <GeneratedRenderer />
    </main>
  )
}
