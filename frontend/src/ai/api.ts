import axios from 'axios'
import { generateLocalInterface } from './localGenerator'
import type { GeneratedUI, GenerationRequest } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function generateInterface(request: GenerationRequest): Promise<GeneratedUI> {
  try {
    const response = await axios.post<GeneratedUI>(`${API_URL}/generate`, request, { timeout: 10000 })
    return { ...response.data, source: 'backend' }
  } catch (error) {
    console.warn('Backend generation unavailable, using local generator.', error)
    return generateLocalInterface(request)
  }
}
