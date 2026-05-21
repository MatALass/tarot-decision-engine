export type ContractCode = 'PRISE' | 'GARDE' | 'GARDE_SANS' | 'GARDE_CONTRE'

export interface HealthResponse {
  status: string
  service: string
  api_version: string
}

export interface ApiErrorResponse {
  detail: string
}

export interface ActionRef {
  player_index: number
  card: string
}

export interface RankedActionItem {
  rank: number
  action: ActionRef
  expected_score: number
  win_rate: number
}

export interface MoveExplanation {
  summary: string
  top_gap_expected_score: number
  top_gap_win_rate: number
  risk_comment: string
  alternatives_summary: string[]
}

export interface MoveRecommendationRequest {
  remaining_hand: string
  contract: ContractCode
  player_index: number
  taker_index: number
  partner_index: number | null
  current_trick: string
  completed_tricks: string[]
  next_player_index: number
  n_samples: number
  seed: number
  policy: 'expected_score'
}

export interface MoveRecommendationResponse {
  recommended_action: ActionRef
  policy_name: string
  rationale: string
  warnings: string[]
  ranked_actions: RankedActionItem[]
  evaluations: Array<{
    action: ActionRef
    expected_score: number
    win_rate: number
    score_std: number
    score_q10: number
    score_q50: number
    score_q90: number
    n_samples: number
  }>
  explanation: MoveExplanation
}
