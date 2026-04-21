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
</script>

<template>
  <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
    <div class="flex items-start justify-between gap-6">
      <div>
        <h3 class="text-lg font-medium text-white">{{ title }}</h3>
        <p class="mt-2 text-sm text-slate-400">{{ description }}</p>
      </div>
      <button
        v-if="removable"
        type="button"
        class="rounded-2xl border border-border px-3 py-2 text-sm text-slate-300 transition hover:border-red-400/40 hover:bg-red-500/10 hover:text-red-100"
        @click="emit('remove')"
      >
        Remove
      </button>
    </div>

    <div class="mt-5 grid gap-3">
      <div
        v-for="(entry, index) in modelValue.entries"
        :key="`${modelValue.id}-${index}`"
        class="grid gap-3 rounded-2xl border border-border bg-slate-900/40 p-4 xl:grid-cols-[0.18fr_0.42fr_1fr]"
      >
        <label class="space-y-2">
          <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Seat</span>
          <select
            class="w-full rounded-2xl border border-border bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40"
            :value="entry.playerIndex ?? ''"
            @change="onPlayerChange(index, ($event.target as HTMLSelectElement).value)"
          >
            <option value="">None</option>
            <option v-for="player in playerOptions" :key="player" :value="player">Player {{ player }}</option>
          </select>
        </label>

        <label class="space-y-2">
          <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Card</span>
          <select
            class="w-full rounded-2xl border border-border bg-slate-950 px-3 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40"
            :value="entry.card ?? ''"
            @change="onCardChange(index, ($event.target as HTMLSelectElement).value)"
          >
            <option value="">None</option>
            <option
              v-for="card in CARD_OPTIONS"
              :key="card.token"
              :value="card.token"
              :disabled="isCardDisabled(card.token, entry.card)"
            >
              {{ card.token }} — {{ card.label }}
            </option>
          </select>
        </label>

        <div class="space-y-2">
          <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Preview</span>
          <CardTokenPill v-if="entry.card" :token="entry.card" compact />
          <div v-else class="rounded-2xl border border-dashed border-border px-3 py-3 text-xs text-slate-500">No card assigned</div>
        </div>
      </div>
    </div>
  </div>
</template>
