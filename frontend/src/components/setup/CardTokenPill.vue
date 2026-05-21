<script setup lang="ts">
import { computed } from 'vue'
import { CARD_LOOKUP, type CardSuit } from '@/lib/cards'

const props = defineProps<{
  token: string
  active?: boolean
  compact?: boolean
  rank?: number
}>()

const cardData = computed(() => CARD_LOOKUP.get(props.token))

const SUIT_SYMBOL: Record<CardSuit, string> = {
  SPADES:   '♠',
  HEARTS:   '♥',
  DIAMONDS: '♦',
  CLUBS:    '♣',
  TRUMPS:   '★',
  SPECIAL:  '✦',
}

const suitSymbol = computed(() => {
  const suit = cardData.value?.suit
  return suit ? SUIT_SYMBOL[suit] : ''
})

const isRed = computed(() => {
  const suit = cardData.value?.suit
  return suit === 'HEARTS' || suit === 'DIAMONDS'
})

const isTrump = computed(() => cardData.value?.suit === 'TRUMPS')
const isSpecial = computed(() => cardData.value?.suit === 'SPECIAL')

// Short display: just rank part
const shortToken = computed(() => {
  if (!props.token) return ''
  if (props.token === 'EXCUSE') return '☽'
  // Remove suit suffix for colored suits
  return props.token.replace(/[SHDC]$/, '')
})
</script>

<template>
  <div
    class="relative overflow-hidden rounded-lg border transition-all duration-150 select-none"
    :class="[
      compact ? 'px-2.5 py-1.5' : 'px-3 py-2.5',
      active
        ? isTrump
          ? 'border-gold/60 bg-gold/15 shadow-glow-gold'
          : isSpecial
            ? 'border-purple-400/50 bg-purple-400/10'
            : isRed
              ? 'border-ruby/50 bg-ruby/10'
              : 'border-sapphire/50 bg-sapphire/10'
        : 'border-border bg-card hover:border-rim hover:bg-card/80',
    ]"
  >
    <!-- Rank badge (for recommendation list) -->
    <div
      v-if="rank !== undefined"
      class="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold"
      :class="rank === 1 ? 'bg-gold text-deep' : 'bg-border text-subtle'"
    >{{ rank }}</div>

    <div class="flex items-center gap-1.5">
      <!-- Suit symbol -->
      <span
        class="text-xs font-bold leading-none"
        :class="[
          isRed ? 'text-ruby' : '',
          isTrump ? 'text-gold' : '',
          isSpecial ? 'text-purple-400' : '',
          !isRed && !isTrump && !isSpecial ? 'text-sapphire' : '',
        ]"
      >{{ suitSymbol }}</span>
      <!-- Token -->
      <span
        class="font-mono font-semibold leading-none"
        :class="[
          compact ? 'text-xs' : 'text-sm',
          active
            ? isTrump ? 'text-gold-light' : isRed ? 'text-red-200' : 'text-blue-200'
            : 'text-text',
        ]"
      >{{ shortToken }}</span>
    </div>
    <div v-if="!compact && cardData" class="mt-1 text-[10px] text-subtle leading-none truncate">
      {{ cardData.label }}
    </div>
  </div>
</template>
