import axios from 'axios'
import type { GenerationRequest, GenerationResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function generateInterface(request: GenerationRequest): Promise<GenerationResponse> {
  const response = await axios.post<GenerationResponse>(`${API_URL}/generate`, request, { timeout: 10000 })
  return response.data
}
