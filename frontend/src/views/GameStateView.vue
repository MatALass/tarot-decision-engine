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
    (entry): entry is { playerIndex: number; card: string } => entry.playerIndex !== null && entry.card !== null,
  )
}

const currentTrickRows = computed<TrickRow[]>(() => {
  const normalized = normalizeEntries(currentTrick.value.entries)
  return normalized.map((entry, index) => ({
    seat: entry.playerIndex,
    card: entry.card,
    lead: index === 0,
    winner: false,
  }))
})

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
  () => currentTrickRows.value.length + completedTrickViews.value.reduce((total, trick) => total + trick.cards.length, 0),
)

const observedPlayedCount = computed(() => {
  const currentCount = currentTrickRows.value.filter((row) => row.seat === playerIndex.value).length
  const historyCount = completedTrickViews.value.reduce(
    (total, trick) => total + trick.cards.filter((card) => card.seat === playerIndex.value).length,
    0,
  )
  return currentCount + historyCount
})

const seatCards = computed(() => {
  const cardsBySeat = new Map<number, string[]>()
  for (let seat = 0; seat < 5; seat += 1) {
    cardsBySeat.set(seat, [])
  }
  cardsBySeat.set(playerIndex.value, [...remainingHand.value])
  return cardsBySeat
})

const seatSummaries = computed(() =>
  Array.from({ length: 5 }, (_, seat) => {
    const roleParts: string[] = []
    if (seat === playerIndex.value) roleParts.push('Observed hand')
    if (seat === takerIndex.value) roleParts.push('Taker')
    if (partnerIndex.value !== null && seat === partnerIndex.value) roleParts.push('Partner')
    if (roleParts.length === 0) roleParts.push('Opponent seat')

    let status = 'Hidden remaining hand.'
    if (seat === playerIndex.value) {
      status = `${remainingHand.value.length} cards known in hand, ${observedPlayedCount.value} already committed.`
    } else if (seat === nextPlayerIndex.value) {
      status = 'Next actor in turn order.'
    }

    return {
      seat,
      role: roleParts.join(' • '),
      status,
      highlighted: seat === playerIndex.value || seat === nextPlayerIndex.value,
      cards: seatCards.value.get(seat) ?? [],
      meta: seat === nextPlayerIndex.value ? 'Next to play' : '',
    }
  }),
)

const recommendationSummary = computed(() => {
  if (!lastRecommendation.value) {
    return null
  }
  const best = lastRecommendation.value.evaluations.find(
    (item) => item.action.card === lastRecommendation.value?.recommended_action.card,
  )
  return {
    action: lastRecommendation.value.recommended_action.card,
    rationale: lastRecommendation.value.rationale,
    expectedScore: best?.expected_score ?? null,
    winRate: best?.win_rate ?? null,
  }
})
</script>

<template>
  <section>
    <SectionHeader
      eyebrow="Observable state"
      title="Current state cockpit"
      description="Move seamlessly from setup into a premium operational view of the observable state: current trick, completed-trick timeline, seat roles, and the latest recommendation context."
    />

    <div v-if="remainingHand.length === 0 && completedTricks.length === 0 && currentTrickRows.length === 0" class="rounded-3xl border border-dashed border-border bg-slate-950/20 px-6 py-10 text-sm text-slate-400">
      No synchronized game state yet. Configure a game on the Setup page first, then come back here to inspect the observable state.
    </div>

    <div v-else class="space-y-6">
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StateMetricCard label="Observed hand" :value="`${remainingHand.length} cards`" hint="Cards still known in the observed player's hand." />
        <StateMetricCard label="Cards already played" :value="`${playedCardCount}`" hint="Across current trick and trick history." />
        <StateMetricCard label="Contract" :value="contract" :hint="`Taker: Player ${takerIndex}${partnerIndex !== null ? ` • Partner: Player ${partnerIndex}` : ''}`" />
        <StateMetricCard label="Turn focus" :value="`Player ${nextPlayerIndex}`" :hint="'Next to act according to the synchronized setup state.'" />
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <TrickTable
          title="Current trick"
          subtitle="Read the partial trick exactly as captured from setup. Lead order is preserved and the next actor stays visible in the surrounding context panels."
          :rows="currentTrickRows"
          empty-message="No card has been played yet in the current trick."
        />

        <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h3 class="text-lg font-medium text-white">Decision continuity</h3>
              <p class="mt-2 text-sm text-slate-400">The setup state, current-state cockpit, and recommendation page now share the same synchronized source of truth.</p>
            </div>
            <div class="rounded-2xl border border-border bg-slate-900/50 px-4 py-2 text-sm text-slate-300">
              {{ isSubmitting ? 'Evaluating…' : 'Synced' }}
            </div>
          </div>

          <div class="mt-6 space-y-4">
            <div class="rounded-2xl border border-border bg-slate-900/40 p-4">
              <div class="text-xs uppercase tracking-[0.22em] text-slate-500">Observed hand rail</div>
              <div v-if="remainingHand.length === 0" class="mt-3 text-sm text-slate-500">No known card remaining.</div>
              <div v-else class="mt-4 grid gap-3 sm:grid-cols-2">
                <CardTokenPill v-for="card in remainingHand" :key="card" :token="card" compact />
              </div>
            </div>

            <div class="rounded-2xl border border-border bg-slate-900/40 p-4">
              <div class="text-xs uppercase tracking-[0.22em] text-slate-500">Recommendation status</div>
              <div v-if="recommendationSummary" class="mt-3 space-y-3 text-sm text-slate-300">
                <div class="flex items-center gap-3">
                  <CardTokenPill :token="recommendationSummary.action" compact />
                  <span>{{ recommendationSummary.rationale }}</span>
                </div>
                <div class="grid gap-3 sm:grid-cols-2">
                  <div class="rounded-2xl border border-border bg-slate-950/45 px-3 py-3">
                    <div class="text-xs uppercase tracking-[0.18em] text-slate-500">Expected score</div>
                    <div class="mt-2 text-lg font-semibold text-white">{{ recommendationSummary.expectedScore === null ? '—' : recommendationSummary.expectedScore.toFixed(2) }}</div>
                  </div>
                  <div class="rounded-2xl border border-border bg-slate-950/45 px-3 py-3">
                    <div class="text-xs uppercase tracking-[0.18em] text-slate-500">Win rate</div>
                    <div class="mt-2 text-lg font-semibold text-white">{{ recommendationSummary.winRate === null ? '—' : `${(recommendationSummary.winRate * 100).toFixed(1)}%` }}</div>
                  </div>
                </div>
              </div>
              <div v-else class="mt-3 text-sm text-slate-500">No recommendation captured yet. Submit the setup to populate the recommendation cockpit.</div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <RouterLink
                to="/setup"
                class="rounded-2xl border border-border px-4 py-3 text-center text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:bg-slate-900/50"
              >
                Edit setup
              </RouterLink>
              <RouterLink
                to="/recommendation"
                class="rounded-2xl bg-accent px-4 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-accent-light"
              >
                Open recommendation view
              </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div class="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
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
