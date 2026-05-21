<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterLink } from 'vue-router'

import SeatStatusCard from '@/components/game/SeatStatusCard.vue'
import StateMetricCard from '@/components/game/StateMetricCard.vue'
import TrickTable, { type TrickRow } from '@/components/game/TrickTable.vue'
import TrickTimeline, { type CompletedTrickView } from '@/components/game/TrickTimeline.vue'
import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import { useGameSetupStore } from '@/stores/gameSetup'

const setupStore = useGameSetupStore()
const {
  remainingHand,
  contract,
  playerIndex,
  takerIndex,
  partnerIndex,
  nextPlayerIndex,
  currentTrick,
  completedTricks,
  lastRecommendation,
  isSubmitting,
} = storeToRefs(setupStore)

function normalizeEntries(entries: Array<{ playerIndex: number | null; card: string | null }>) {
  return entries.filter(
    (entry): entry is { playerIndex: number; card: string } =>
      entry.playerIndex !== null && entry.card !== null,
  )
}

const currentTrickRows = computed<TrickRow[]>(() =>
  normalizeEntries(currentTrick.value.entries).map((entry, index) => ({
    seat: entry.playerIndex,
    card: entry.card,
    lead: index === 0,
    winner: false,
  })),
)

const completedTrickViews = computed<CompletedTrickView[]>(() =>
  completedTricks.value.map((trick, trickIndex) => {
    const entries = normalizeEntries(trick.entries)
    return {
      id: trick.id,
      trickNumber: trickIndex + 1,
      leadSeat: entries[0]?.playerIndex ?? null,
      winnerSeat: entries.length === 5 ? entries[entries.length - 1].playerIndex : null,
      cards: entries.map((entry) => ({ seat: entry.playerIndex, card: entry.card })),
    }
  }),
)

const playedCardCount = computed(
  () =>
    currentTrickRows.value.length +
    completedTrickViews.value.reduce((total, trick) => total + trick.cards.length, 0),
)

const observedPlayedCount = computed(() => {
  const inCurrent = currentTrickRows.value.filter((row) => row.seat === playerIndex.value).length
  const inHistory = completedTrickViews.value.reduce(
    (total, trick) => total + trick.cards.filter((card) => card.seat === playerIndex.value).length,
    0,
  )
  return inCurrent + inHistory
})

const seatSummaries = computed(() =>
  Array.from({ length: 5 }, (_, seat) => {
    const roles: string[] = []
    if (seat === playerIndex.value) roles.push('Main observée')
    if (seat === takerIndex.value) roles.push('Preneur')
    if (partnerIndex.value !== null && seat === partnerIndex.value) roles.push('Partenaire')
    if (roles.length === 0) roles.push('Adversaire')

    let status = 'Main inconnue.'
    if (seat === playerIndex.value)
      status = `${remainingHand.value.length} cartes connues, ${observedPlayedCount.value} jouées.`
    else if (seat === nextPlayerIndex.value)
      status = 'Prochain à jouer.'

    return {
      seat,
      role: roles.join(' · '),
      status,
      highlighted: seat === playerIndex.value || seat === nextPlayerIndex.value,
      cards: seat === playerIndex.value ? remainingHand.value : [],
      meta: seat === nextPlayerIndex.value ? 'À jouer' : '',
    }
  }),
)

const recommendationSummary = computed(() => {
  if (!lastRecommendation.value) return null
  const best = lastRecommendation.value.evaluations.find(
    (item) => item.action.card === lastRecommendation.value?.recommended_action.card,
  )
  return {
    card: lastRecommendation.value.recommended_action.card,
    rationale: lastRecommendation.value.rationale,
    expectedScore: best?.expected_score ?? null,
    winRate: best?.win_rate ?? null,
  }
})

const isEmpty = computed(
  () =>
    remainingHand.value.length === 0 &&
    completedTricks.value.length === 0 &&
    currentTrickRows.value.length === 0,
)
</script>

<template>
  <section class="animate-fade-in">
    <SectionHeader
      eyebrow="État de partie"
      title="Cockpit observable"
      description="Vue synchronisée de l'état courant : pli en jeu, historique, rôles des sièges et dernière recommandation."
    />

    <!-- Empty state -->
    <div
      v-if="isEmpty"
      class="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border py-20 text-center"
    >
      <span class="text-4xl opacity-20 font-display">◈</span>
      <div class="text-sm text-subtle">Aucun état synchronisé.</div>
      <RouterLink
        to="/setup"
        class="btn-gold rounded-xl px-6 py-2.5 text-sm"
      >Configurer une partie →</RouterLink>
    </div>

    <div v-else class="space-y-5">
      <!-- Metric strip -->
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StateMetricCard
          label="Main observée"
          :value="`${remainingHand.length} cartes`"
          :hint="`Joueur ${playerIndex} · ${observedPlayedCount} déjà jouées`"
        />
        <StateMetricCard
          label="Cartes jouées"
          :value="`${playedCardCount}`"
          hint="Pli courant + historique"
        />
        <StateMetricCard
          label="Contrat"
          :value="contract"
          :hint="`Preneur: J${takerIndex}${partnerIndex !== null ? ` · Partenaire: J${partnerIndex}` : ''}`"
        />
        <StateMetricCard
          label="Prochain joueur"
          :value="`Joueur ${nextPlayerIndex}`"
          hint="Prochain à jouer dans l'état synchronisé"
        />
      </div>

      <!-- Current trick + Decision panel -->
      <div class="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <TrickTable
          title="Pli courant"
          subtitle="Cartes déjà jouées dans ce pli, dans l'ordre d'entame."
          :rows="currentTrickRows"
          empty-message="Aucune carte jouée dans le pli courant."
        />

        <!-- Decision continuity panel -->
        <div class="rounded-2xl panel-base overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #1e2538;">
            <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Décision</h3>
            <div
              class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[10px] font-medium"
              :class="isSubmitting
                ? 'border-amber/25 bg-amber/8 text-amber'
                : 'border-emerald/25 bg-emerald/8 text-emerald'"
            >
              <div
                class="h-1.5 w-1.5 rounded-full"
                :class="isSubmitting ? 'bg-amber animate-pulse' : 'bg-emerald'"
              ></div>
              {{ isSubmitting ? 'Évaluation…' : 'Synchronisé' }}
            </div>
          </div>

          <div class="px-5 py-4 space-y-4">
            <!-- Hand rail -->
            <div class="rounded-xl border border-border bg-deep p-3">
              <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-2">Main connue</div>
              <div v-if="remainingHand.length === 0" class="text-xs text-muted italic">Aucune carte.</div>
              <div v-else class="flex flex-wrap gap-1.5">
                <CardTokenPill
                  v-for="card in remainingHand"
                  :key="card"
                  :token="card"
                  compact
                />
              </div>
            </div>

            <!-- Recommendation status -->
            <div
              class="rounded-xl border p-3"
              :class="recommendationSummary
                ? 'border-gold/25 bg-gold/5'
                : 'border-border bg-deep'"
            >
              <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-2">Recommandation</div>
              <div v-if="recommendationSummary" class="space-y-2">
                <div class="flex items-center gap-2.5">
                  <CardTokenPill :token="recommendationSummary.card" compact :active="true" />
                  <span class="text-xs text-subtle flex-1">{{ recommendationSummary.rationale }}</span>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <div class="rounded-lg border border-border bg-deep px-3 py-2">
                    <div class="text-[10px] text-subtle">EV</div>
                    <div class="font-mono text-sm font-semibold metric-gold">
                      {{ recommendationSummary.expectedScore !== null
                        ? (recommendationSummary.expectedScore > 0 ? '+' : '') + recommendationSummary.expectedScore.toFixed(2)
                        : '—' }}
                    </div>
                  </div>
                  <div class="rounded-lg border border-border bg-deep px-3 py-2">
                    <div class="text-[10px] text-subtle">Win rate</div>
                    <div class="font-mono text-sm font-semibold text-emerald">
                      {{ recommendationSummary.winRate !== null
                        ? `${(recommendationSummary.winRate * 100).toFixed(1)}%`
                        : '—' }}
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-xs text-muted italic">
                Soumettez d'abord la configuration pour obtenir une recommandation.
              </div>
            </div>

            <!-- Nav buttons -->
            <div class="grid grid-cols-2 gap-2">
              <RouterLink
                to="/setup"
                class="rounded-xl border border-border py-2.5 text-center text-xs font-medium text-subtle transition hover:border-rim hover:text-text"
              >← Modifier</RouterLink>
              <RouterLink
                to="/recommendation"
                class="btn-gold rounded-xl py-2.5 text-center text-xs"
              >Analyse →</RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Seats + Timeline -->
      <div class="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <div class="grid grid-cols-2 gap-3 content-start">
          <SeatStatusCard
            v-for="seat in seatSummaries"
            :key="seat.seat"
            :seat="seat.seat"
            :role="seat.role"
            :status="seat.status"
            :highlighted="seat.highlighted"
            :cards="seat.cards"
            :meta="seat.meta"
          />
        </div>
        <TrickTimeline :tricks="completedTrickViews" />
      </div>
    </div>
  </section>
</template>
