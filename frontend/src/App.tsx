import 'tldraw/tldraw.css'
import { Toaster } from 'react-hot-toast'
import { CanvasWorkspace } from './canvas/CanvasWorkspace'
import { GeneratedRenderer } from './components/GeneratedRenderer'
import { useAppStore } from './store/useAppStore'
import './App.css'

export default function App() {
  const isSidebarCollapsed = useAppStore((state) => state.isSidebarCollapsed)

  return (
    <main className={`app-shell${isSidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
      <Toaster position="top-center" toastOptions={{ style: { background: '#101318', color: '#f5f7fb' } }} />
      <CanvasWorkspace />
      <GeneratedRenderer />
    </main>
  )
}
