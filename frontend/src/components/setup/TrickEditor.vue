<script setup lang="ts">
import { computed } from 'vue'

import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import { CARD_OPTIONS } from '@/lib/cards'
import type { TrickDraft } from '@/stores/gameSetup'

const props = defineProps<{
  title: string
  description: string
  modelValue: TrickDraft
  usedTokens: string[]
  allowPartial: boolean
  removable?: boolean
}>()

const emit = defineEmits<{
  updatePlayer: [index: number, playerIndex: number | null]
  updateCard: [index: number, token: string | null]
  remove: []
}>()

const playerOptions = [0, 1, 2, 3, 4]
const usedSet = computed(() => new Set(props.usedTokens))

function onCardChange(index: number, value: string): void {
  emit('updateCard', index, value === '' ? null : value)
}
function onPlayerChange(index: number, value: string): void {
  emit('updatePlayer', index, value === '' ? null : Number(value))
}
function isCardDisabled(token: string, currentToken: string | null): boolean {
  return usedSet.value.has(token) && currentToken !== token
}

const filledCount = computed(() =>
  props.modelValue.entries.filter((e) => e.card !== null).length
)
</script>

<template>
  <div class="rounded-2xl panel-base overflow-hidden">
    <div class="flex items-start justify-between gap-4 px-5 py-4" style="border-bottom: 1px solid #1e2538;">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">{{ title }}</h3>
          <span class="rounded-full bg-border px-2 py-0.5 text-[10px] font-medium text-subtle">{{ filledCount }}/5</span>
        </div>
        <p class="mt-1 text-xs text-subtle">{{ description }}</p>
      </div>
      <button
        v-if="removable"
        type="button"
        class="rounded-lg border border-ruby/20 px-3 py-1.5 text-xs text-ruby/70 transition hover:bg-ruby/10 hover:text-ruby hover:border-ruby/40"
        @click="emit('remove')"
      >
        Supprimer
      </button>
    </div>

    <div class="divide-y divide-border">
      <div
        v-for="(entry, index) in modelValue.entries"
        :key="`${modelValue.id}-${index}`"
        class="flex items-center gap-3 px-5 py-3"
        :class="entry.card ? 'bg-gold/3' : ''"
      >
        <!-- Play order indicator -->
        <div
          class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold"
          :class="index === 0 ? 'bg-gold/20 text-gold' : 'bg-border text-muted'"
        >{{ index + 1 }}</div>

        <!-- Seat selector -->
        <select
          class="w-24 shrink-0 rounded-lg border border-border bg-deep px-2 py-2 text-xs text-text outline-none transition focus:border-gold/40"
          :value="entry.playerIndex ?? ''"
          @change="onPlayerChange(index, ($event.target as HTMLSelectElement).value)"
        >
          <option value="">—</option>
          <option v-for="player in playerOptions" :key="player" :value="player">J{{ player }}</option>
        </select>

        <!-- Card selector -->
        <select
          class="flex-1 rounded-lg border border-border bg-deep px-2 py-2 text-xs text-text outline-none transition focus:border-gold/40"
          :value="entry.card ?? ''"
          @change="onCardChange(index, ($event.target as HTMLSelectElement).value)"
        >
          <option value="">Aucune carte</option>
          <option
            v-for="card in CARD_OPTIONS"
            :key="card.token"
            :value="card.token"
            :disabled="isCardDisabled(card.token, entry.card)"
          >
            {{ card.token }} — {{ card.label }}
          </option>
        </select>

        <!-- Card preview -->
        <div class="shrink-0">
          <CardTokenPill v-if="entry.card" :token="entry.card" compact />
          <div v-else class="h-8 w-14 rounded-lg border border-dashed border-border"></div>
        </div>
      </div>
    </div>
  </div>
</template>
