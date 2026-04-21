import type { HealthResponse, MoveRecommendationRequest, MoveRecommendationResponse } from '@/types/api';
export declare function fetchHealth(): Promise<HealthResponse>;
export declare function recommendMove(payload: MoveRecommendationRequest): Promise<MoveRecommendationResponse>;
