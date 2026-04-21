<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterLink } from 'vue-router'

import SectionHeader from '@/components/ui/SectionHeader.vue'
import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import { useGameSetupStore } from '@/stores/gameSetup'
import { CARD_LOOKUP } from '@/lib/cards'

const setupStore = useGameSetupStore()
const { lastRecommendation, lastSubmittedPayload, contract, playerIndex, takerIndex, nSamples } = storeToRefs(setupStore)

// Score distribution across all evaluated actions
const allEvals = computed(() => lastRecommendation.value?.evaluations ?? [])

const scoreStats = computed(() => {
  const scores = allEvals.value.map((e) => e.expected_score)
  if (!scores.length) return null
  const sorted = [...scores].sort((a, b) => a - b)
  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    mean: scores.reduce((s, v) => s + v, 0) / scores.length,
    spread: sorted[sorted.length - 1] - sorted[0],
  }
})

const winRateStats = computed(() => {
  const rates = allEvals.value.map((e) => e.win_rate)
  if (!rates.length) return null
  return {
    min: Math.min(...rates),
    max: Math.max(...rates),
    mean: rates.reduce((s, v) => s + v, 0) / rates.length,
  }
})

function formatScore(v: number): string {
  return v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2)
}
function formatPct(v: number): string {
  return `${(v * 100).toFixed(1)}%`
}

// Per-action detail for the scatter-style table
const actionMatrix = computed(() =>
  allEvals.value.map((e) => {
    const ranked = lastRecommendation.value?.ranked_actions.find(
      (r) => r.action.card === e.action.card
    )
    const spread = e.score_q90 - e.score_q10
    return {
      card: e.action.card,
      label: CARD_LOOKUP.get(e.action.card)?.label ?? e.action.card,
      rank: ranked?.rank ?? 99,
      ev: e.expected_score,
      winRate: e.win_rate,
      std: e.score_std,
      q10: e.score_q10,
      q50: e.score_q50,
      q90: e.score_q90,
      spread,
    }
  }).sort((a, b) => a.rank - b.rank)
)

const isEmpty = computed(() => !lastRecommendation.value)
</script>

<template>
  <section class="animate-fade-in">
    <SectionHeader
      eyebrow="Analyse"
      title="Espace de recherche"
      description="Vue matricielle complète de toutes les actions évaluées — distribution des scores, volatilité et comparaisons inter-coups."
    />

    <!-- Empty state -->
    <div
      v-if="isEmpty"
      class="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border py-20 text-center"
    >
      <span class="text-4xl opacity-20 font-display">◉</span>
      <div class="text-sm text-subtle">Aucune évaluation disponible.</div>
      <RouterLink to="/setup" class="btn-gold rounded-xl px-6 py-2.5 text-sm">Configurer →</RouterLink>
    </div>

    <div v-else class="space-y-5">
      <!-- Context strip -->
      <div class="grid gap-3 sm:grid-cols-4">
        <div class="rounded-xl border border-border bg-panel p-4">
          <div class="text-[10px] tracking-widest text-subtle uppercase mb-1">Contrat</div>
          <div class="font-display text-lg font-semibold text-gold">{{ contract }}</div>
        </div>
        <div class="rounded-xl border border-border bg-panel p-4">
          <div class="text-[10px] tracking-widest text-subtle uppercase mb-1">Coups légaux</div>
          <div class="font-display text-lg font-semibold text-text">{{ allEvals.length }}</div>
        </div>
        <div class="rounded-xl border border-border bg-panel p-4">
          <div class="text-[10px] tracking-widest text-subtle uppercase mb-1">Simulations MC</div>
          <div class="font-mono text-sm font-semibold text-text">{{ nSamples.toLocaleString() }}</div>
        </div>
        <div class="rounded-xl border border-border bg-panel p-4">
          <div class="text-[10px] tracking-widest text-subtle uppercase mb-1">Joueur observé</div>
          <div class="font-display text-lg font-semibold text-text">J{{ playerIndex }} · Preneur J{{ takerIndex }}</div>
        </div>
      </div>

      <!-- Summary stats -->
      <div v-if="scoreStats && winRateStats" class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-2xl panel-base p-5">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-3">EV — Plage des scores</div>
          <div class="flex items-end gap-3">
            <div>
              <div class="text-[10px] text-muted">Min</div>
              <div class="font-mono font-semibold text-ruby">{{ formatScore(scoreStats.min) }}</div>
            </div>
            <div class="flex-1 pb-1">
              <div class="h-1 rounded-full bg-border overflow-hidden">
                <div class="h-full rounded-full" style="background: linear-gradient(90deg, #c0374a, #c9963a, #2aab6f); width: 100%;"></div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-[10px] text-muted">Max</div>
              <div class="font-mono font-semibold text-emerald">{{ formatScore(scoreStats.max) }}</div>
            </div>
          </div>
          <div class="mt-2 text-xs text-subtle">Écart = {{ formatScore(scoreStats.spread) }} · Moyenne = {{ formatScore(scoreStats.mean) }}</div>
        </div>

        <div class="rounded-2xl panel-base p-5">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-3">Win rate — Distribution</div>
          <div class="flex items-end gap-3">
            <div>
              <div class="text-[10px] text-muted">Min</div>
              <div class="font-mono font-semibold text-ruby">{{ formatPct(winRateStats.min) }}</div>
            </div>
            <div class="flex-1 pb-1">
              <div class="h-1 rounded-full bg-border overflow-hidden">
                <div class="h-full rounded-full bg-emerald" :style="`width: ${winRateStats.mean * 100}%`"></div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-[10px] text-muted">Max</div>
              <div class="font-mono font-semibold text-emerald">{{ formatPct(winRateStats.max) }}</div>
            </div>
          </div>
          <div class="mt-2 text-xs text-subtle">Moyenne = {{ formatPct(winRateStats.mean) }}</div>
        </div>

        <div class="rounded-2xl panel-base p-5">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-3">Snapshot soumis</div>
          <div class="space-y-1.5 text-xs">
            <div class="flex justify-between">
              <span class="text-subtle">Main restante</span>
              <span class="font-mono text-text">{{ lastSubmittedPayload?.remaining_hand.split(',').length ?? 0 }} cartes</span>
            </div>
            <div class="flex justify-between">
              <span class="text-subtle">Plis terminés</span>
              <span class="font-mono text-text">{{ lastSubmittedPayload?.completed_tricks.length ?? 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-subtle">Poli. évaluation</span>
              <span class="font-mono text-gold">expected_score</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Full action matrix -->
      <div class="rounded-2xl panel-base overflow-hidden">
        <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
          <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Matrice complète des actions</h3>
          <p class="text-xs text-subtle mt-0.5">Toutes les actions légales triées par rang. Q10/Q50/Q90 = quantiles des scores simulés.</p>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full text-xs">
            <thead>
              <tr style="border-bottom: 1px solid #1e2538; background: rgba(12,14,22,0.8);">
                <th class="px-4 py-3 text-left text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Rang</th>
                <th class="px-4 py-3 text-left text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Carte</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">EV</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Win %</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">σ</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Q10</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Q50</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Q90</th>
                <th class="px-4 py-3 text-right text-[10px] tracking-[0.2em] text-subtle uppercase font-medium">Spread</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border">
              <tr
                v-for="action in actionMatrix"
                :key="action.card"
                class="transition-colors hover:bg-card"
                :class="action.rank === 1 ? 'bg-gold/4' : ''"
              >
                <td class="px-4 py-3">
                  <div
                    class="flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold"
                    :class="action.rank === 1 ? 'bg-gold text-deep' : 'bg-border text-muted'"
                  >{{ action.rank }}</div>
                </td>
                <td class="px-4 py-3">
                  <CardTokenPill :token="action.card" compact :active="action.rank === 1" />
                </td>
                <td class="px-4 py-3 text-right font-mono" :class="action.ev > 0 ? 'text-emerald' : 'text-ruby'">
                  {{ formatScore(action.ev) }}
                </td>
                <td class="px-4 py-3 text-right font-mono text-text">{{ formatPct(action.winRate) }}</td>
                <td class="px-4 py-3 text-right font-mono text-subtle">{{ action.std.toFixed(2) }}</td>
                <td class="px-4 py-3 text-right font-mono text-ruby/80">{{ formatScore(action.q10) }}</td>
                <td class="px-4 py-3 text-right font-mono text-gold">{{ formatScore(action.q50) }}</td>
                <td class="px-4 py-3 text-right font-mono text-emerald/80">{{ formatScore(action.q90) }}</td>
                <td class="px-4 py-3 text-right font-mono text-subtle">{{ formatScore(action.spread) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Future slots -->
      <div class="grid gap-3 sm:grid-cols-3">
        <div class="rounded-xl border border-dashed border-border bg-deep p-5 text-center">
          <div class="text-2xl opacity-20 mb-2">⬡</div>
          <div class="text-xs text-muted">Heatmap probabilités postérieures</div>
          <div class="text-[10px] text-subtle/50 mt-1">Prochaine itération</div>
        </div>
        <div class="rounded-xl border border-dashed border-border bg-deep p-5 text-center">
          <div class="text-2xl opacity-20 mb-2">◎</div>
          <div class="text-xs text-muted">Percentile de force de main</div>
          <div class="text-[10px] text-subtle/50 mt-1">Prochaine itération</div>
        </div>
        <div class="rounded-xl border border-dashed border-border bg-deep p-5 text-center">
          <div class="text-2xl opacity-20 mb-2">◆</div>
          <div class="text-xs text-muted">Synergies et impact de carte</div>
          <div class="text-[10px] text-subtle/50 mt-1">Prochaine itération</div>
        </div>
      </div>
    </div>
  </section>
</template>
