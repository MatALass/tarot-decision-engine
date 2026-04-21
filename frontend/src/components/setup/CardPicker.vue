<script setup lang="ts">
import { computed } from 'vue'

import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import { CARD_GROUPS, CARD_OPTIONS } from '@/lib/cards'

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

const disabledSet = computed(() => new Set(props.disabledTokens ?? []))
const selectedSet = computed(() => new Set(props.selected))
const groupedCards = computed(() =>
  CARD_GROUPS.map((group) => ({
    ...group,
    cards: CARD_OPTIONS.filter((card) => card.suit === group.key),
  })),
)

function isDisabled(token: string): boolean {
  return disabledSet.value.has(token) && !selectedSet.value.has(token)
}
</script>

<template>
  <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
    <div class="flex items-start justify-between gap-6">
      <div>
        <h3 class="text-lg font-medium text-white">{{ title }}</h3>
        <p class="mt-2 max-w-2xl text-sm text-slate-400">{{ description }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-slate-900/60 px-4 py-3 text-right">
        <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Selected</div>
        <div class="mt-1 text-2xl font-semibold text-white">{{ selected.length }}<span v-if="maxSelection">/{{ maxSelection }}</span></div>
      </div>
    </div>

    <div class="mt-6 space-y-5">
      <section v-for="group in groupedCards" :key="group.key">
        <div class="mb-3 flex items-center justify-between">
          <h4 class="text-sm font-medium text-slate-200">{{ group.label }}</h4>
          <div class="text-xs uppercase tracking-[0.2em] text-slate-500">{{ group.cards.length }} cards</div>
        </div>
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-6">
          <button
            v-for="card in group.cards"
            :key="card.token"
            type="button"
            class="text-left"
            :disabled="isDisabled(card.token)"
            @click="emit('toggle', card.token)"
          >
            <CardTokenPill
              :token="card.token"
              :active="selectedSet.has(card.token)"
              :class="isDisabled(card.token) ? 'cursor-not-allowed opacity-35' : 'cursor-pointer'"
            />
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
