export type CardSuit = 'SPADES' | 'HEARTS' | 'DIAMONDS' | 'CLUBS' | 'TRUMPS' | 'SPECIAL'

export interface CardOption {
  token: string
  label: string
  suit: CardSuit
  sortOrder: number
}

const suitedRanks = [
  { token: 'AS', label: 'As' },
  { token: 'K', label: 'Roi' },
  { token: 'Q', label: 'Dame' },
  { token: 'C', label: 'Cavalier' },
  { token: 'J', label: 'Valet' },
  { token: '10', label: '10' },
  { token: '9', label: '9' },
  { token: '8', label: '8' },
  { token: '7', label: '7' },
  { token: '6', label: '6' },
  { token: '5', label: '5' },
  { token: '4', label: '4' },
  { token: '3', label: '3' },
  { token: '2', label: '2' },
]

const suits = [
  { key: 'SPADES' as const, suffix: 'S', name: 'Pique' },
  { key: 'HEARTS' as const, suffix: 'H', name: 'Cœur' },
  { key: 'DIAMONDS' as const, suffix: 'D', name: 'Carreau' },
  { key: 'CLUBS' as const, suffix: 'C', name: 'Trèfle' },
]

export const CARD_OPTIONS: CardOption[] = [
  ...suits.flatMap((suit, suitIndex) =>
    suitedRanks.map((rank, rankIndex) => ({
      token: `${rank.token}${suit.suffix}`,
      label: `${rank.label} ${suit.name}`,
      suit: suit.key,
      sortOrder: suitIndex * 100 + rankIndex,
    })),
  ),
  ...Array.from({ length: 21 }, (_, index) => ({
    token: `T${index + 1}`,
    label: `Atout ${index + 1}`,
    suit: 'TRUMPS' as const,
    sortOrder: 500 + index,
  })),
  {
    token: 'EXCUSE',
    label: 'Excuse',
    suit: 'SPECIAL' as const,
    sortOrder: 1000,
  },
]

export const CARD_LOOKUP = new Map(CARD_OPTIONS.map((card) => [card.token, card]))

export const CARD_GROUPS: Array<{ key: CardSuit; label: string }> = [
  { key: 'SPADES', label: 'Piques' },
  { key: 'HEARTS', label: 'Cœurs' },
  { key: 'DIAMONDS', label: 'Carreaux' },
  { key: 'CLUBS', label: 'Trèfles' },
  { key: 'TRUMPS', label: 'Atouts' },
  { key: 'SPECIAL', label: 'Spéciale' },
]

export function sortCardTokens(tokens: string[]): string[] {
  return [...tokens].sort((left, right) => {
    const leftOrder = CARD_LOOKUP.get(left)?.sortOrder ?? 99_999
    const rightOrder = CARD_LOOKUP.get(right)?.sortOrder ?? 99_999
    return leftOrder - rightOrder
  })
}

export function formatCardLabel(token: string): string {
  return CARD_LOOKUP.get(token)?.label ?? token
}
