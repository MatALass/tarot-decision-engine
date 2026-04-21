export type CardSuit = 'SPADES' | 'HEARTS' | 'DIAMONDS' | 'CLUBS' | 'TRUMPS' | 'SPECIAL';
export interface CardOption {
    token: string;
    label: string;
    suit: CardSuit;
    sortOrder: number;
}
export declare const CARD_OPTIONS: CardOption[];
export declare const CARD_LOOKUP: Map<string, CardOption>;
export declare const CARD_GROUPS: Array<{
    key: CardSuit;
    label: string;
}>;
export declare function sortCardTokens(tokens: string[]): string[];
export declare function formatCardLabel(token: string): string;
