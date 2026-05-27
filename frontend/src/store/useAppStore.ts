import { create } from 'zustand'
import type { GeneratedUI, SpatialShape } from '../types'

interface AppState {
  generatedUI: GeneratedUI | null
  prompt: string
  selectedOnly: boolean
  lastShapes: SpatialShape[]
  isGenerating: boolean
  status: string
  setGeneratedUI: (ui: GeneratedUI | null) => void
  setPrompt: (prompt: string) => void
  setSelectedOnly: (selectedOnly: boolean) => void
  setLastShapes: (shapes: SpatialShape[]) => void
  setIsGenerating: (isGenerating: boolean) => void
  setStatus: (status: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  generatedUI: null,
  prompt: '',
  selectedOnly: false,
  lastShapes: [],
  isGenerating: false,
  status: 'Ready',
  setGeneratedUI: (generatedUI) => set({ generatedUI }),
  setPrompt: (prompt) => set({ prompt }),
  setSelectedOnly: (selectedOnly) => set({ selectedOnly }),
  setLastShapes: (lastShapes) => set({ lastShapes }),
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  setStatus: (status) => set({ status }),
}))
