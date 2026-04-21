import type { ContractCode, MoveRecommendationRequest, MoveRecommendationResponse } from '@/types/api';
export interface TrickEntryDraft {
    playerIndex: number | null;
    card: string | null;
}
export interface TrickDraft {
    id: string;
    entries: TrickEntryDraft[];
}
export declare const useGameSetupStore: import("pinia").StoreDefinition<"gameSetup", Pick<{
    remainingHand: import("vue").Ref<string[], string[]>;
    contract: import("vue").Ref<ContractCode, ContractCode>;
    playerIndex: import("vue").Ref<number, number>;
    takerIndex: import("vue").Ref<number, number>;
    partnerIndex: import("vue").Ref<number | null, number | null>;
    nextPlayerIndex: import("vue").Ref<number, number>;
    nSamples: import("vue").Ref<number, number>;
    seed: import("vue").Ref<number, number>;
    policy: import("vue").Ref<"expected_score", "expected_score">;
    currentTrick: {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    };
    completedTricks: import("vue").Ref<{
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[], TrickDraft[] | {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[]>;
    isSubmitting: import("vue").Ref<boolean, boolean>;
    apiError: import("vue").Ref<string | null, string | null>;
    lastRecommendation: import("vue").Ref<{
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null, MoveRecommendationResponse | {
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null>;
    lastSubmittedPayload: import("vue").Ref<{
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null, MoveRecommendationRequest | {
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null>;
    selectedCardSet: import("vue").ComputedRef<Set<string>>;
    validationErrors: import("vue").ComputedRef<string[]>;
    canSubmit: import("vue").ComputedRef<boolean>;
    toggleRemainingHandCard: (token: string) => void;
    setEntryCard: (target: TrickDraft, index: number, token: string | null) => void;
    setEntryPlayer: (target: TrickDraft, index: number, playerIndexValue: number | null) => void;
    addCompletedTrick: () => void;
    removeCompletedTrick: (id: string) => void;
    resetAll: () => void;
    submitRecommendation: () => Promise<boolean>;
}, "contract" | "seed" | "policy" | "remainingHand" | "playerIndex" | "takerIndex" | "partnerIndex" | "nextPlayerIndex" | "nSamples" | "currentTrick" | "completedTricks" | "isSubmitting" | "apiError" | "lastRecommendation" | "lastSubmittedPayload">, Pick<{
    remainingHand: import("vue").Ref<string[], string[]>;
    contract: import("vue").Ref<ContractCode, ContractCode>;
    playerIndex: import("vue").Ref<number, number>;
    takerIndex: import("vue").Ref<number, number>;
    partnerIndex: import("vue").Ref<number | null, number | null>;
    nextPlayerIndex: import("vue").Ref<number, number>;
    nSamples: import("vue").Ref<number, number>;
    seed: import("vue").Ref<number, number>;
    policy: import("vue").Ref<"expected_score", "expected_score">;
    currentTrick: {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    };
    completedTricks: import("vue").Ref<{
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[], TrickDraft[] | {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[]>;
    isSubmitting: import("vue").Ref<boolean, boolean>;
    apiError: import("vue").Ref<string | null, string | null>;
    lastRecommendation: import("vue").Ref<{
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null, MoveRecommendationResponse | {
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null>;
    lastSubmittedPayload: import("vue").Ref<{
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null, MoveRecommendationRequest | {
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null>;
    selectedCardSet: import("vue").ComputedRef<Set<string>>;
    validationErrors: import("vue").ComputedRef<string[]>;
    canSubmit: import("vue").ComputedRef<boolean>;
    toggleRemainingHandCard: (token: string) => void;
    setEntryCard: (target: TrickDraft, index: number, token: string | null) => void;
    setEntryPlayer: (target: TrickDraft, index: number, playerIndexValue: number | null) => void;
    addCompletedTrick: () => void;
    removeCompletedTrick: (id: string) => void;
    resetAll: () => void;
    submitRecommendation: () => Promise<boolean>;
}, "selectedCardSet" | "validationErrors" | "canSubmit">, Pick<{
    remainingHand: import("vue").Ref<string[], string[]>;
    contract: import("vue").Ref<ContractCode, ContractCode>;
    playerIndex: import("vue").Ref<number, number>;
    takerIndex: import("vue").Ref<number, number>;
    partnerIndex: import("vue").Ref<number | null, number | null>;
    nextPlayerIndex: import("vue").Ref<number, number>;
    nSamples: import("vue").Ref<number, number>;
    seed: import("vue").Ref<number, number>;
    policy: import("vue").Ref<"expected_score", "expected_score">;
    currentTrick: {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    };
    completedTricks: import("vue").Ref<{
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[], TrickDraft[] | {
        id: string;
        entries: {
            playerIndex: number | null;
            card: string | null;
        }[];
    }[]>;
    isSubmitting: import("vue").Ref<boolean, boolean>;
    apiError: import("vue").Ref<string | null, string | null>;
    lastRecommendation: import("vue").Ref<{
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null, MoveRecommendationResponse | {
        recommended_action: {
            player_index: number;
            card: string;
        };
        policy_name: string;
        rationale: string;
        warnings: string[];
        ranked_actions: {
            rank: number;
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
        }[];
        evaluations: {
            action: {
                player_index: number;
                card: string;
            };
            expected_score: number;
            win_rate: number;
            score_std: number;
            score_q10: number;
            score_q50: number;
            score_q90: number;
            n_samples: number;
        }[];
        explanation: {
            summary: string;
            top_gap_expected_score: number;
            top_gap_win_rate: number;
            risk_comment: string;
            alternatives_summary: string[];
        };
    } | null>;
    lastSubmittedPayload: import("vue").Ref<{
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null, MoveRecommendationRequest | {
        remaining_hand: string;
        contract: ContractCode;
        player_index: number;
        taker_index: number;
        partner_index: number | null;
        current_trick: string;
        completed_tricks: string[];
        next_player_index: number;
        n_samples: number;
        seed: number;
        policy: "expected_score";
    } | null>;
    selectedCardSet: import("vue").ComputedRef<Set<string>>;
    validationErrors: import("vue").ComputedRef<string[]>;
    canSubmit: import("vue").ComputedRef<boolean>;
    toggleRemainingHandCard: (token: string) => void;
    setEntryCard: (target: TrickDraft, index: number, token: string | null) => void;
    setEntryPlayer: (target: TrickDraft, index: number, playerIndexValue: number | null) => void;
    addCompletedTrick: () => void;
    removeCompletedTrick: (id: string) => void;
    resetAll: () => void;
    submitRecommendation: () => Promise<boolean>;
}, "toggleRemainingHandCard" | "setEntryCard" | "setEntryPlayer" | "addCompletedTrick" | "removeCompletedTrick" | "resetAll" | "submitRecommendation">>;
