<script setup lang="ts">
import { computed, ref } from 'vue'

import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import { CARD_GROUPS, CARD_OPTIONS, type CardSuit } from '@/lib/cards'

const props = defineProps<{
  selected: string[]
  disabledTokens?: string[]
  title: string
  description: string
  maxSelection?: number
}>()

const emit = defineEmits<{
  toggle: [token: string]
}>()

const activeGroup = ref<CardSuit | 'ALL'>('ALL')

const disabledSet = computed(() => new Set(props.disabledTokens ?? []))
const selectedSet = computed(() => new Set(props.selected))

const groupedCards = computed(() =>
  CARD_GROUPS.map((group) => ({
    ...group,
    cards: CARD_OPTIONS.filter((card) => card.suit === group.key),
    selectedCount: CARD_OPTIONS.filter((c) => c.suit === group.key && selectedSet.value.has(c.token)).length,
  })),
)

const displayedGroups = computed(() =>
  activeGroup.value === 'ALL'
    ? groupedCards.value
    : groupedCards.value.filter((g) => g.key === activeGroup.value),
)

function isDisabled(token: string): boolean {
  return disabledSet.value.has(token) && !selectedSet.value.has(token)
}

const SUIT_LABELS: Record<string, string> = {
  SPADES: '♠', HEARTS: '♥', DIAMONDS: '♦', CLUBS: '♣', TRUMPS: '★', SPECIAL: '✦',
}

const fillPct = computed(() =>
  props.maxSelection ? Math.round((props.selected.length / props.maxSelection) * 100) : 0,
)
</script>

<template>
  <div class="rounded-2xl panel-base overflow-hidden">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4 px-6 pt-5 pb-4" style="border-bottom: 1px solid #1e2538;">
      <div>
        <h3 class="font-display text-base font-semibold tracking-wider text-gold-light">{{ title }}</h3>
        <p class="mt-1 text-sm text-subtle max-w-xl leading-relaxed">{{ description }}</p>
      </div>
      <div class="shrink-0 rounded-xl border border-border bg-deep px-4 py-2.5 text-right">
        <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-1">Sélection</div>
        <div class="font-display text-2xl font-semibold metric-gold">
          {{ selected.length }}<span class="text-sm text-subtle font-body" v-if="maxSelection">/{{ maxSelection }}</span>
        </div>
        <!-- Progress bar -->
        <div v-if="maxSelection" class="mt-2 h-1 w-24 rounded-full bg-border overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="fillPct >= 100 ? 'bg-emerald' : 'bg-gold'"
            :style="{ width: `${Math.min(fillPct, 100)}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Group tabs -->
    <div class="flex gap-1.5 overflow-x-auto px-6 py-3" style="border-bottom: 1px solid #1e2538;">
      <button
        type="button"
        class="shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-all duration-150"
        :class="activeGroup === 'ALL' ? 'bg-gold/15 text-gold border border-gold/30' : 'text-subtle hover:text-text hover:bg-card border border-transparent'"
        @click="activeGroup = 'ALL'"
      >Toutes</button>
      <button
        v-for="group in groupedCards"
        :key="group.key"
        type="button"
        class="shrink-0 flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all duration-150"
        :class="activeGroup === group.key ? 'bg-gold/15 text-gold border border-gold/30' : 'text-subtle hover:text-text hover:bg-card border border-transparent'"
        @click="activeGroup = group.key"
      >
        <span>{{ SUIT_LABELS[group.key] }}</span>
        <span>{{ group.label }}</span>
        <span
          v-if="group.selectedCount > 0"
          class="rounded-full bg-gold/25 px-1.5 text-[10px] text-gold font-semibold"
        >{{ group.selectedCount }}</span>
      </button>
    </div>

    <!-- Card grid -->
    <div class="px-6 py-4 space-y-5">
      <section v-for="group in displayedGroups" :key="group.key">
        <div class="mb-3 flex items-center gap-2">
          <span class="text-xs font-semibold tracking-widest text-subtle uppercase">{{ group.label }}</span>
          <div class="h-px flex-1 bg-border"></div>
          <span class="text-[10px] text-muted">{{ group.cards.length }} cartes</span>
        </div>
        <div class="grid gap-2" :class="group.key === 'TRUMPS' ? 'grid-cols-7 lg:grid-cols-11' : 'grid-cols-4 sm:grid-cols-7 lg:grid-cols-10 xl:grid-cols-7 2xl:grid-cols-10'">
          <button
            v-for="card in group.cards"
            :key="card.token"
            type="button"
            class="text-left transition-transform duration-100"
            :class="isDisabled(card.token) ? 'opacity-25 cursor-not-allowed' : 'hover:scale-105 active:scale-95 cursor-pointer'"
            :disabled="isDisabled(card.token)"
            @click="emit('toggle', card.token)"
          >
            <CardTokenPill
              :token="card.token"
              :active="selectedSet.has(card.token)"
            />
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
