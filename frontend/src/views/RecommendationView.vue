<script setup lang="ts">
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import { useGameSetupStore } from '@/stores/gameSetup'
import { CARD_LOOKUP } from '@/lib/cards'

const router = useRouter()
const setupStore = useGameSetupStore()
const { lastRecommendation, lastSubmittedPayload, isSubmitting } = storeToRefs(setupStore)

const selectedCard = ref<string | null>(null)

const bestEval = computed(() => {
  const rec = lastRecommendation.value
  if (!rec) return null
  return rec.evaluations.find(
    (e) => e.action.card === rec.recommended_action.card
  ) ?? null
})

const rankedEvals = computed(() => {
  const rec = lastRecommendation.value
  if (!rec) return []
  return rec.ranked_actions.map((ra) => {
    const ev = rec.evaluations.find(
      (e) => e.action.card === ra.action.card && e.action.player_index === ra.action.player_index
    )
    return { ...ra, eval: ev ?? null }
  })
})

const focusedEval = computed(() => {
  const rec = lastRecommendation.value
  if (!rec) return null
  if (!selectedCard.value) return bestEval.value
  return rec.evaluations.find((e) => e.action.card === selectedCard.value) ?? null
})

const focusedRanked = computed(() => {
  if (!selectedCard.value || !lastRecommendation.value) return null
  return lastRecommendation.value.ranked_actions.find(
    (r) => r.action.card === selectedCard.value
  ) ?? null
})

const isTopCard = computed(() =>
  !selectedCard.value || selectedCard.value === lastRecommendation.value?.recommended_action.card
)

// Score range for bar normalization
const scoreRange = computed(() => {
  const scores = rankedEvals.value.map((r) => r.eval?.expected_score ?? 0)
  const min = Math.min(...scores)
  const max = Math.max(...scores)
  return { min, max, span: max - min || 1 }
})

function barWidth(score: number): number {
  const { min, span } = scoreRange.value
  return Math.max(4, ((score - min) / span) * 100)
}

function winBarWidth(rate: number): number {
  return Math.max(4, rate * 100)
}

function selectCard(token: string) {
  selectedCard.value = selectedCard.value === token ? null : token
}

function formatScore(v: number | undefined): string {
  if (v === undefined) return '—'
  return v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2)
}

function formatPct(v: number | undefined): string {
  if (v === undefined) return '—'
  return `${(v * 100).toFixed(1)}%`
}

function riskLevel(std: number | undefined): { label: string; color: string } {
  if (std === undefined) return { label: '—', color: 'text-subtle' }
  if (std < 15) return { label: 'Faible', color: 'text-emerald' }
  if (std < 35) return { label: 'Modéré', color: 'text-amber' }
  return { label: 'Élevé', color: 'text-ruby' }
}

async function reSubmit() {
  const ok = await setupStore.submitRecommendation()
  if (ok) selectedCard.value = null
}
</script>

<template>
  <section class="animate-fade-in">
    <SectionHeader
      eyebrow="Recommandation"
      title="Cockpit de décision"
      description="Analyse Monte Carlo des coups légaux — classement par espérance de score, taux de victoire et distribution des quantiles."
    />

    <!-- Empty state -->
    <div
      v-if="!lastRecommendation || !lastSubmittedPayload"
      class="flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-border py-20 text-center"
    >
      <div class="text-4xl opacity-20 font-display">◆</div>
      <div class="text-sm text-subtle">Aucune recommandation disponible.</div>
      <button
        type="button"
        class="btn-gold rounded-xl px-6 py-2.5 text-sm"
        @click="router.push('/setup')"
      >
        Configurer une partie →
      </button>
    </div>

    <div v-else class="space-y-6">
      <!-- Top hero row: recommended card + key metrics -->
      <div class="grid gap-5 xl:grid-cols-[auto_1fr_1fr_1fr]">
        <!-- Hero card -->
        <div
          class="flex flex-col items-center justify-center gap-4 rounded-2xl p-6 xl:min-w-[180px]"
          style="background: linear-gradient(135deg, rgba(201,150,58,0.12) 0%, rgba(201,150,58,0.04) 100%); border: 1px solid rgba(201,150,58,0.3); box-shadow: 0 0 32px rgba(201,150,58,0.08);"
        >
          <div class="text-[10px] tracking-[0.3em] text-gold/70 uppercase font-medium">Coup recommandé</div>
          <!-- Big card visual -->
          <div
            class="relative flex flex-col items-center justify-center rounded-xl"
            style="width: 80px; height: 112px; background: linear-gradient(160deg, #1a1f35 0%, #0f1220 100%); border: 2px solid rgba(201,150,58,0.5); box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 20px rgba(201,150,58,0.15);"
          >
            <div class="font-display text-2xl font-bold metric-gold">
              {{ lastRecommendation.recommended_action.card.replace(/[SHDC]$/, '').replace('EXCUSE', '☽') }}
            </div>
            <div class="mt-1 text-xs text-subtle">
              {{ CARD_LOOKUP.get(lastRecommendation.recommended_action.card)?.label ?? lastRecommendation.recommended_action.card }}
            </div>
            <!-- Corner rank badge -->
            <div
              class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold text-deep"
              style="background: linear-gradient(135deg, #c9963a, #e8b55a);"
            >#1</div>
          </div>
          <div class="text-xs text-subtle text-center leading-relaxed max-w-[140px]">
            {{ lastRecommendation.rationale }}
          </div>
        </div>

        <!-- EV metric -->
        <div class="rounded-2xl border border-border bg-panel p-5 flex flex-col justify-between" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase">Espérance de score</div>
          <div>
            <div class="font-display text-3xl font-semibold metric-gold mt-2">
              {{ formatScore(bestEval?.expected_score) }}
            </div>
            <div class="text-xs text-subtle mt-1">vs. Q50 = {{ formatScore(bestEval?.score_q50) }}</div>
          </div>
          <!-- Mini bar -->
          <div class="mt-3 h-1.5 w-full rounded-full bg-border overflow-hidden">
            <div class="h-full rounded-full bg-gold transition-all duration-500" style="width: 100%"></div>
          </div>
        </div>

        <!-- Win rate metric -->
        <div class="rounded-2xl border border-border bg-panel p-5 flex flex-col justify-between" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase">Taux de victoire</div>
          <div>
            <div class="font-display text-3xl font-semibold text-emerald mt-2" style="text-shadow: 0 0 20px rgba(42,171,111,0.3);">
              {{ formatPct(bestEval?.win_rate) }}
            </div>
            <div class="text-xs text-subtle mt-1">Écart vs 2e: {{ formatPct(lastRecommendation.explanation.top_gap_win_rate) }}</div>
          </div>
          <div class="mt-3 h-1.5 w-full rounded-full bg-border overflow-hidden">
            <div
              class="h-full rounded-full bg-emerald transition-all duration-500"
              :style="{ width: `${(bestEval?.win_rate ?? 0) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Risk metric -->
        <div class="rounded-2xl border border-border bg-panel p-5 flex flex-col justify-between" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);">
          <div class="text-[10px] tracking-[0.25em] text-subtle uppercase">Volatilité</div>
          <div>
            <div
              class="font-display text-3xl font-semibold mt-2"
              :class="riskLevel(bestEval?.score_std).color"
            >{{ riskLevel(bestEval?.score_std).label }}</div>
            <div class="text-xs text-subtle mt-1">σ = {{ bestEval?.score_std?.toFixed(2) ?? '—' }}</div>
          </div>
          <!-- Q10/Q90 spread indicator -->
          <div class="mt-3 flex items-center gap-1 text-[10px] text-muted">
            <span>Q10 {{ formatScore(bestEval?.score_q10) }}</span>
            <div class="h-px flex-1 bg-border"></div>
            <span>Q90 {{ formatScore(bestEval?.score_q90) }}</span>
          </div>
        </div>
      </div>

      <!-- Main split: ranked list + detail panel -->
      <div class="grid gap-5 xl:grid-cols-[1fr_380px]">
        <!-- Ranked actions table -->
        <div class="rounded-2xl panel-base overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #1e2538;">
            <div>
              <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Actions classées</h3>
              <p class="text-xs text-subtle mt-0.5">Cliquer une ligne pour l'inspecter en détail</p>
            </div>
            <div class="rounded-lg border border-border bg-deep px-3 py-1.5 text-xs text-subtle font-mono">
              {{ rankedEvals.length }} coups légaux
            </div>
          </div>

          <div class="divide-y divide-border">
            <div
              v-for="item in rankedEvals"
              :key="item.action.card"
              class="group flex cursor-pointer items-center gap-4 px-5 py-3.5 transition-all duration-150"
              :class="[
                selectedCard === item.action.card
                  ? 'bg-gold/8 border-l-2 border-l-gold'
                  : item.rank === 1
                    ? 'bg-emerald/4 border-l-2 border-l-emerald/40 hover:bg-gold/5'
                    : 'border-l-2 border-l-transparent hover:bg-card',
              ]"
              @click="selectCard(item.action.card)"
            >
              <!-- Rank -->
              <div
                class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
                :class="item.rank === 1 ? 'bg-gold text-deep' : 'bg-border text-muted'"
              >{{ item.rank }}</div>

              <!-- Card pill -->
              <div class="shrink-0">
                <CardTokenPill :token="item.action.card" compact :active="selectedCard === item.action.card || item.rank === 1" />
              </div>

              <!-- EV bar -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs font-mono text-text">EV {{ formatScore(item.eval?.expected_score) }}</span>
                  <span class="text-xs text-subtle">WR {{ formatPct(item.eval?.win_rate) }}</span>
                </div>
                <div class="h-1.5 w-full rounded-full bg-border overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="item.rank === 1 ? 'bg-gold' : selectedCard === item.action.card ? 'bg-sapphire' : 'bg-rim'"
                    :style="{ width: `${barWidth(item.eval?.expected_score ?? 0)}%` }"
                  ></div>
                </div>
              </div>

              <!-- Win rate mini bar -->
              <div class="hidden w-20 shrink-0 sm:block">
                <div class="h-1.5 rounded-full bg-border overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="item.rank === 1 ? 'bg-emerald' : 'bg-rim'"
                    :style="{ width: `${winBarWidth(item.eval?.win_rate ?? 0)}%` }"
                  ></div>
                </div>
                <div class="text-[10px] text-muted mt-1 text-right font-mono">{{ formatPct(item.eval?.win_rate) }}</div>
              </div>

              <!-- Chevron -->
              <div class="shrink-0 text-muted text-xs transition group-hover:text-gold">›</div>
            </div>
          </div>
        </div>

        <!-- Detail panel -->
        <div class="space-y-4">
          <!-- Focused card detail -->
          <div class="rounded-2xl panel-base overflow-hidden">
            <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #1e2538;">
              <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">
                {{ isTopCard ? 'Meilleur coup' : 'Coup sélectionné' }}
              </h3>
              <div v-if="focusedEval" class="shrink-0">
                <CardTokenPill :token="focusedEval.action.card" :active="true" compact />
              </div>
            </div>

            <div v-if="focusedEval" class="px-5 py-4 space-y-4">
              <!-- Q distribution -->
              <div>
                <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-3">Distribution des scores</div>
                <!-- Q bar visual -->
                <div class="relative h-8 rounded-lg bg-deep overflow-hidden border border-border">
                  <!-- Q10–Q90 fill -->
                  <div
                    class="absolute inset-y-0 rounded-md"
                    :class="isTopCard ? 'bg-gold/20' : 'bg-sapphire/15'"
                    :style="{
                      left: `${barWidth(focusedEval.score_q10)}%`,
                      right: `${100 - barWidth(focusedEval.score_q90)}%`,
                    }"
                  ></div>
                  <!-- Q50 line -->
                  <div
                    class="absolute inset-y-0 w-0.5"
                    :class="isTopCard ? 'bg-gold' : 'bg-sapphire'"
                    :style="{ left: `${barWidth(focusedEval.score_q50)}%` }"
                  ></div>
                </div>
                <div class="mt-2 grid grid-cols-3 text-[10px] font-mono text-subtle">
                  <span>Q10 {{ formatScore(focusedEval.score_q10) }}</span>
                  <span class="text-center" :class="isTopCard ? 'text-gold' : 'text-sapphire'">Q50 {{ formatScore(focusedEval.score_q50) }}</span>
                  <span class="text-right">Q90 {{ formatScore(focusedEval.score_q90) }}</span>
                </div>
              </div>

              <!-- Metric grid -->
              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] tracking-widest text-subtle uppercase">EV</div>
                  <div class="font-display text-lg mt-1" :class="isTopCard ? 'metric-gold' : 'text-text'">
                    {{ formatScore(focusedEval.expected_score) }}
                  </div>
                </div>
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] tracking-widest text-subtle uppercase">Win rate</div>
                  <div class="font-display text-lg mt-1 text-emerald">{{ formatPct(focusedEval.win_rate) }}</div>
                </div>
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] tracking-widest text-subtle uppercase">Volatilité</div>
                  <div class="font-display text-lg mt-1" :class="riskLevel(focusedEval.score_std).color">
                    {{ riskLevel(focusedEval.score_std).label }}
                  </div>
                </div>
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] tracking-widest text-subtle uppercase">σ</div>
                  <div class="font-display text-lg mt-1 text-text font-mono">{{ focusedEval.score_std.toFixed(2) }}</div>
                </div>
              </div>

              <div v-if="focusedRanked" class="rounded-xl border border-border bg-deep p-3">
                <div class="text-[10px] tracking-widest text-subtle uppercase mb-1">Rang</div>
                <div class="text-sm text-text">#{{ focusedRanked.rank }} sur {{ rankedEvals.length }} coups légaux</div>
              </div>
            </div>
          </div>

          <!-- Explanation block -->
          <div class="rounded-2xl panel-base overflow-hidden">
            <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
              <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Explication</h3>
            </div>
            <div class="px-5 py-4 space-y-3">
              <p class="text-sm text-text leading-relaxed">{{ lastRecommendation.explanation.summary }}</p>

              <div class="rounded-xl border border-border bg-deep p-3 text-xs text-subtle leading-relaxed">
                {{ lastRecommendation.explanation.risk_comment }}
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] text-subtle uppercase tracking-widest">Écart EV</div>
                  <div class="font-mono text-sm mt-1" :class="lastRecommendation.explanation.top_gap_expected_score > 0 ? 'text-emerald' : 'text-ruby'">
                    {{ formatScore(lastRecommendation.explanation.top_gap_expected_score) }}
                  </div>
                </div>
                <div class="rounded-xl border border-border bg-deep p-3">
                  <div class="text-[10px] text-subtle uppercase tracking-widest">Écart WR</div>
                  <div class="font-mono text-sm mt-1" :class="lastRecommendation.explanation.top_gap_win_rate > 0 ? 'text-emerald' : 'text-ruby'">
                    {{ formatPct(lastRecommendation.explanation.top_gap_win_rate) }}
                  </div>
                </div>
              </div>

              <div v-if="lastRecommendation.explanation.alternatives_summary.length > 0" class="space-y-2">
                <div class="text-[10px] tracking-[0.25em] text-subtle uppercase">Alternatives</div>
                <div
                  v-for="note in lastRecommendation.explanation.alternatives_summary"
                  :key="note"
                  class="rounded-xl border border-border bg-deep px-3 py-2.5 text-xs text-subtle leading-snug"
                >{{ note }}</div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              class="btn-gold rounded-xl py-2.5 text-xs"
              :disabled="isSubmitting"
              @click="reSubmit"
            >
              {{ isSubmitting ? 'Simulation…' : 'Relancer →' }}
            </button>
            <button
              type="button"
              class="rounded-xl border border-border py-2.5 text-xs text-subtle transition hover:border-rim hover:text-text"
              @click="router.push('/setup')"
            >← Modifier</button>
          </div>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="lastRecommendation.warnings.length > 0" class="rounded-2xl border border-amber/20 bg-amber/5 px-5 py-4">
        <div class="text-[10px] tracking-[0.25em] text-amber uppercase mb-2">Avertissements engine</div>
        <div v-for="w in lastRecommendation.warnings" :key="w" class="text-xs text-amber/80 leading-snug">{{ w }}</div>
      </div>
    </div>
  </section>
</template>
