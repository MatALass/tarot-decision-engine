import axios from 'axios'

import type { HealthResponse, MoveRecommendationRequest, MoveRecommendationResponse } from '@/types/api'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 30000,
})

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/api/v1/health')
  return data
}

export async function recommendMove(payload: MoveRecommendationRequest): Promise<MoveRecommendationResponse> {
  const { data } = await apiClient.post<MoveRecommendationResponse>('/api/v1/moves/recommend', payload)
  return data
}
