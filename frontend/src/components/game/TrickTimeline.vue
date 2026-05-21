<script setup lang="ts">
import { ref } from 'vue'
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

const expanded = ref<Set<string>>(new Set())
function toggle(id: string) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
}
</script>

<template>
  <div class="rounded-2xl panel-base overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #1e2538;">
      <div>
        <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Timeline des plis</h3>
        <p class="text-xs text-subtle mt-0.5">Historique complet de la partie en cours.</p>
      </div>
      <div class="rounded-lg border border-border bg-deep px-3 py-1.5 text-xs font-mono text-subtle">
        {{ tricks.length }} pli{{ tricks.length > 1 ? 's' : '' }}
      </div>
    </div>

    <div
      v-if="tricks.length === 0"
      class="flex items-center justify-center gap-2 px-5 py-10 text-xs text-subtle"
    >
      <span class="opacity-30 text-lg">◎</span>
      Aucun pli terminé pour l'instant.
    </div>

    <!-- Timeline -->
    <div v-else class="relative px-5 py-4 space-y-0">
      <!-- Vertical line -->
      <div class="absolute left-[36px] top-4 bottom-4 w-px bg-border"></div>

      <div v-for="trick in tricks" :key="trick.id">
        <div
          class="relative flex cursor-pointer items-start gap-4 rounded-xl px-3 py-3 transition-all duration-150 hover:bg-card"
          @click="toggle(trick.id)"
        >
          <!-- Timeline dot -->
          <div
            class="relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold"
            :class="trick.winnerSeat !== null
              ? 'border-emerald/40 bg-emerald/10 text-emerald'
              : 'border-border bg-deep text-muted'"
          >{{ trick.trickNumber }}</div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-xs font-medium text-text">Pli #{{ trick.trickNumber }}</span>
                <span class="text-[10px] text-subtle">Entame J{{ trick.leadSeat ?? '?' }}</span>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <span
                  v-if="trick.winnerSeat !== null"
                  class="rounded-full border border-emerald/25 bg-emerald/8 px-2 py-0.5 text-[10px] text-emerald"
                >J{{ trick.winnerSeat }}</span>
                <span class="text-muted text-xs transition" :class="expanded.has(trick.id) ? 'rotate-90' : ''">›</span>
              </div>
            </div>

            <!-- Compact card row preview (always visible) -->
            <div class="mt-2 flex flex-wrap gap-1">
              <CardTokenPill
                v-for="(entry, i) in trick.cards"
                :key="`${trick.id}-${i}`"
                :token="entry.card"
                compact
              />
            </div>
          </div>
        </div>

        <!-- Expanded detail -->
        <div
          v-if="expanded.has(trick.id)"
          class="ml-10 mb-2 rounded-xl border border-border bg-deep overflow-hidden"
        >
          <div class="divide-y divide-border">
            <div
              v-for="(entry, i) in trick.cards"
              :key="`exp-${trick.id}-${i}`"
              class="flex items-center gap-3 px-4 py-2.5"
            >
              <div class="w-5 text-[10px] text-muted font-mono">#{{ i + 1 }}</div>
              <div class="text-xs text-subtle w-12">J{{ entry.seat }}</div>
              <CardTokenPill :token="entry.card" compact />
              <div class="ml-auto">
                <span
                  v-if="i === 0"
                  class="text-[10px] text-sapphire border border-sapphire/20 rounded px-1.5 py-0.5"
                >Entame</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
