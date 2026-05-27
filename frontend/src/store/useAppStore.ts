import { create } from 'zustand'
import type { GeneratedUI } from '../types'

interface AppState {
  generatedUI: GeneratedUI | null
  prompt: string
  selectedOnly: boolean
  lastShapeCount: number
  isGenerating: boolean
  status: string
  setGeneratedUI: (ui: GeneratedUI | null) => void
  setPrompt: (prompt: string) => void
  setSelectedOnly: (selectedOnly: boolean) => void
  setLastShapeCount: (count: number) => void
  setIsGenerating: (isGenerating: boolean) => void
  setStatus: (status: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  generatedUI: null,
  prompt: '',
  selectedOnly: false,
  lastShapeCount: 0,
  isGenerating: false,
  status: 'Ready',
  setGeneratedUI: (generatedUI) => set({ generatedUI }),
  setPrompt: (prompt) => set({ prompt }),
  setSelectedOnly: (selectedOnly) => set({ selectedOnly }),
  setLastShapeCount: (lastShapeCount) => set({ lastShapeCount }),
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  setStatus: (status) => set({ status }),
}))
