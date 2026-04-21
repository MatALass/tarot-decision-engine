<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import { useGameSetupStore } from '@/stores/gameSetup'

const setupStore = useGameSetupStore()
const { lastRecommendation, lastSubmittedPayload } = storeToRefs(setupStore)

const bestEvaluation = computed(() => {
  const response = lastRecommendation.value
  if (!response) {
    return null
  }
  return response.evaluations.find(
    (evaluation) =>
      evaluation.action.card === response.recommended_action.card
      && evaluation.action.player_index === response.recommended_action.player_index,
  ) ?? null
})
</script>

<template>
  <section>
    <SectionHeader
      eyebrow="Decision"
      title="Move recommendation cockpit"
      description="Compare legal actions, inspect the top recommendation, and keep a direct link between the submitted intermediate state and the engine output."
    />

    <div v-if="!lastRecommendation || !lastSubmittedPayload" class="rounded-3xl border border-dashed border-border bg-slate-950/20 px-6 py-10 text-sm text-slate-400">
      No recommendation yet. Build a valid game setup first, then submit it from the Setup page.
    </div>

    <div v-else class="space-y-6">
      <div class="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div class="space-y-6">
          <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
            <div class="flex items-start justify-between gap-6">
              <div>
                <div class="text-xs uppercase tracking-[0.3em] text-slate-500">Best move</div>
                <h3 class="mt-2 text-2xl font-semibold text-white">Player {{ lastRecommendation.recommended_action.player_index }}</h3>
                <p class="mt-2 text-sm text-slate-400">{{ lastRecommendation.rationale }}</p>
              </div>
              <CardTokenPill :token="lastRecommendation.recommended_action.card" />
            </div>

            <div v-if="bestEvaluation" class="mt-6 grid gap-4 sm:grid-cols-2">
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Expected score</div>
                <div class="mt-2 text-2xl font-semibold text-white">{{ bestEvaluation.expected_score.toFixed(2) }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Win rate</div>
                <div class="mt-2 text-2xl font-semibold text-white">{{ (bestEvaluation.win_rate * 100).toFixed(1) }}%</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Q10 / Q50 / Q90</div>
                <div class="mt-2 text-sm text-slate-300">{{ bestEvaluation.score_q10.toFixed(2) }} / {{ bestEvaluation.score_q50.toFixed(2) }} / {{ bestEvaluation.score_q90.toFixed(2) }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Score std</div>
                <div class="mt-2 text-2xl font-semibold text-white">{{ bestEvaluation.score_std.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
            <h3 class="text-lg font-medium text-white">Structured explanation</h3>
            <p class="mt-3 text-sm leading-6 text-slate-300">{{ lastRecommendation.explanation.summary }}</p>
            <div class="mt-5 grid gap-4 md:grid-cols-2">
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Top EV gap</div>
                <div class="mt-2 text-xl font-semibold text-white">{{ lastRecommendation.explanation.top_gap_expected_score.toFixed(2) }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Top win-rate gap</div>
                <div class="mt-2 text-xl font-semibold text-white">{{ (lastRecommendation.explanation.top_gap_win_rate * 100).toFixed(1) }}%</div>
              </div>
            </div>
            <div class="mt-5 rounded-2xl border border-border bg-slate-900/50 p-4 text-sm text-slate-300">
              {{ lastRecommendation.explanation.risk_comment }}
            </div>
            <div v-if="lastRecommendation.explanation.alternatives_summary.length > 0" class="mt-5 space-y-3">
              <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Alternative notes</div>
              <div v-for="item in lastRecommendation.explanation.alternatives_summary" :key="item" class="rounded-2xl border border-border px-4 py-3 text-sm text-slate-300">
                {{ item }}
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
            <h3 class="text-lg font-medium text-white">Ranked legal actions</h3>
            <div class="mt-4 overflow-hidden rounded-2xl border border-border">
              <table class="min-w-full divide-y divide-border text-sm">
                <thead class="bg-slate-900/80 text-left text-slate-400">
                  <tr>
                    <th class="px-4 py-3 font-medium">Rank</th>
                    <th class="px-4 py-3 font-medium">Action</th>
                    <th class="px-4 py-3 font-medium">Expected score</th>
                    <th class="px-4 py-3 font-medium">Win rate</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border bg-slate-950/40 text-slate-200">
                  <tr v-for="item in lastRecommendation.ranked_actions" :key="`${item.rank}-${item.action.card}`">
                    <td class="px-4 py-4">{{ item.rank }}</td>
                    <td class="px-4 py-4">
                      <div class="flex items-center gap-3">
                        <CardTokenPill :token="item.action.card" compact />
                        <span>Player {{ item.action.player_index }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-4">{{ item.expected_score.toFixed(2) }}</td>
                    <td class="px-4 py-4">{{ (item.win_rate * 100).toFixed(1) }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
            <h3 class="text-lg font-medium text-white">Submitted state snapshot</h3>
            <div class="mt-4 grid gap-4 sm:grid-cols-2">
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4 text-sm text-slate-300">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Remaining hand</div>
                <div class="mt-2 break-words text-slate-100">{{ lastSubmittedPayload.remaining_hand }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4 text-sm text-slate-300">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Current trick</div>
                <div class="mt-2 break-words text-slate-100">{{ lastSubmittedPayload.current_trick || 'None' }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4 text-sm text-slate-300">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Completed tricks</div>
                <div class="mt-2 break-words text-slate-100">{{ lastSubmittedPayload.completed_tricks.length }}</div>
              </div>
              <div class="rounded-2xl border border-border bg-slate-900/50 p-4 text-sm text-slate-300">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Monte Carlo samples</div>
                <div class="mt-2 break-words text-slate-100">{{ lastSubmittedPayload.n_samples }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
