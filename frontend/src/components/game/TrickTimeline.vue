<script setup lang="ts">
import CardTokenPill from '@/components/setup/CardTokenPill.vue'

export interface CompletedTrickView {
  id: string
  trickNumber: number
  leadSeat: number | null
  winnerSeat: number | null
  cards: Array<{ seat: number; card: string }>
}

defineProps<{
  tricks: CompletedTrickView[]
}>()
</script>

<template>
  <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="text-lg font-medium text-white">Completed trick timeline</h3>
        <p class="mt-2 text-sm text-slate-400">Read the full game flow with lead seat, winner, and every card already committed to history.</p>
      </div>
      <div class="rounded-2xl border border-border bg-slate-900/50 px-4 py-2 text-sm text-slate-300">
        {{ tricks.length }} trick{{ tricks.length > 1 ? 's' : '' }}
      </div>
    </div>

    <div v-if="tricks.length === 0" class="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-500">
      No completed tricks yet. The timeline will populate as the setup captures earlier play.
    </div>

    <div v-else class="mt-6 space-y-4">
      <article
        v-for="trick in tricks"
        :key="trick.id"
        class="rounded-3xl border border-border bg-slate-900/35 p-5"
      >
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div class="text-xs uppercase tracking-[0.22em] text-slate-500">Trick {{ trick.trickNumber }}</div>
            <div class="mt-2 text-base font-semibold text-white">
              Lead: <span class="text-slate-200">{{ trick.leadSeat === null ? 'Unknown' : `Player ${trick.leadSeat}` }}</span>
            </div>
          </div>
          <div class="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-100">
            Winner: {{ trick.winnerSeat === null ? 'Unknown' : `Player ${trick.winnerSeat}` }}
          </div>
        </div>

        <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <div
            v-for="(entry, index) in trick.cards"
            :key="`${trick.id}-${index}`"
            class="rounded-2xl border border-border bg-slate-950/45 p-3"
          >
            <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Play #{{ index + 1 }}</div>
            <div class="mt-2 text-sm text-slate-300">Player {{ entry.seat }}</div>
            <div class="mt-3"><CardTokenPill :token="entry.card" compact /></div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>
