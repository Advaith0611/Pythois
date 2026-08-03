import axios from 'axios'
import type { GenerationRequest, GenerationResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const GENERATE_TIMEOUT_MS = 30000

function generationErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) return error instanceof Error ? error.message : String(error)

  const status = error.response?.status
  const detail = error.response?.data
  if (status) return `Generate API returned ${status}: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`
  if (error.code === 'ECONNABORTED') return 'Generate API timed out'
  return error.message
}

export async function generateInterface(request: GenerationRequest): Promise<GenerationResponse> {
  try {
    const response = await axios.post<GenerationResponse>(`${API_URL}/generate`, request, { timeout: GENERATE_TIMEOUT_MS })
    return response.data
  } catch (error) {
    throw new Error(generationErrorMessage(error), { cause: error })
  }
}
