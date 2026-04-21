<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import CardPicker from '@/components/setup/CardPicker.vue'
import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import TrickEditor from '@/components/setup/TrickEditor.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import { sortCardTokens } from '@/lib/cards'
import { useGameSetupStore } from '@/stores/gameSetup'
import type { ContractCode } from '@/types/api'

const router = useRouter()
const setupStore = useGameSetupStore()
const {
  remainingHand,
  contract,
  playerIndex,
  takerIndex,
  partnerIndex,
  nextPlayerIndex,
  nSamples,
  seed,
  currentTrick,
  completedTricks,
  validationErrors,
  canSubmit,
  selectedCardSet,
  apiError,
  isSubmitting,
} = storeToRefs(setupStore)

const contractOptions: ContractCode[] = ['PRISE', 'GARDE', 'GARDE_SANS', 'GARDE_CONTRE']
const playerOptions = [0, 1, 2, 3, 4]

const usedOutsideHand = computed(() =>
  sortCardTokens([...selectedCardSet.value].filter((token) => !remainingHand.value.includes(token))),
)

const ownPlayedCount = computed(() => {
  const ownCurrent = currentTrick.value.entries.filter((entry) => entry.playerIndex === playerIndex.value && entry.card !== null).length
  const ownCompleted = completedTricks.value.reduce(
    (count, trick) => count + trick.entries.filter((entry) => entry.playerIndex === playerIndex.value && entry.card !== null).length,
    0,
  )
  return ownCurrent + ownCompleted
})

async function submitForm(): Promise<void> {
  const ok = await setupStore.submitRecommendation()
  if (ok) {
    await router.push('/game')
  }
}
</script>

<template>
  <section>
    <SectionHeader
      eyebrow="Setup"
      title="Real game setup"
      description="Configure a real intermediate game state with a visual remaining-hand picker, explicit seat metadata, and strict validation before asking the engine for a move recommendation."
    />

    <div class="grid gap-6 2xl:grid-cols-[1.35fr_0.65fr]">
      <div class="space-y-6">
        <CardPicker
          title="Observed remaining hand"
          description="Select the cards still in the observed player's hand. The engine will reconstruct the initial 15-card hand by combining these cards with the cards already played by that same player in the trick editors below."
          :selected="remainingHand"
          :disabled-tokens="usedOutsideHand"
          :max-selection="15"
          @toggle="setupStore.toggleRemainingHandCard"
        />

        <div class="grid gap-6 xl:grid-cols-2">
          <TrickEditor
            title="Current trick"
            description="Enter the current partial trick in play order. Leave unused rows empty."
            :model-value="currentTrick"
            :used-tokens="[...selectedCardSet]"
            :allow-partial="true"
            @update-player="(index, value) => setupStore.setEntryPlayer(currentTrick, index, value)"
            @update-card="(index, value) => setupStore.setEntryCard(currentTrick, index, value)"
          />

          <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
            <h3 class="text-lg font-medium text-white">Game context</h3>
            <p class="mt-2 text-sm text-slate-400">These values control the observable state and the Monte Carlo evaluation request sent to the backend API.</p>

            <div class="mt-6 grid gap-4 sm:grid-cols-2">
              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Contract</span>
                <select v-model="contract" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40">
                  <option v-for="item in contractOptions" :key="item" :value="item">{{ item }}</option>
                </select>
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Observed player</span>
                <select v-model.number="playerIndex" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40">
                  <option v-for="player in playerOptions" :key="player" :value="player">Player {{ player }}</option>
                </select>
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Taker</span>
                <select v-model.number="takerIndex" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40">
                  <option v-for="player in playerOptions" :key="player" :value="player">Player {{ player }}</option>
                </select>
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Partner</span>
                <select v-model="partnerIndex" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40">
                  <option :value="null">None</option>
                  <option v-for="player in playerOptions" :key="player" :value="player">Player {{ player }}</option>
                </select>
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Next player</span>
                <select v-model.number="nextPlayerIndex" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40">
                  <option v-for="player in playerOptions" :key="player" :value="player">Player {{ player }}</option>
                </select>
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Monte Carlo samples</span>
                <input v-model.number="nSamples" type="number" min="1" max="100000" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40" />
              </label>

              <label class="space-y-2">
                <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Seed</span>
                <input v-model.number="seed" type="number" class="w-full rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent/40" />
              </label>

              <div class="rounded-2xl border border-border bg-slate-900/50 px-4 py-4 text-sm text-slate-300">
                <div class="text-xs uppercase tracking-[0.2em] text-slate-500">Reconstruction check</div>
                <div class="mt-2 text-white">{{ remainingHand.length }} remaining + {{ ownPlayedCount }} played by player {{ playerIndex }} = {{ remainingHand.length + ownPlayedCount }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-medium text-white">Completed tricks</h3>
              <p class="mt-1 text-sm text-slate-400">Each completed trick must contain exactly five cards in play order.</p>
            </div>
            <button
              type="button"
              class="rounded-2xl border border-accent/30 bg-accent/10 px-4 py-3 text-sm font-medium text-accent-light transition hover:bg-accent/20"
              @click="setupStore.addCompletedTrick"
            >
              Add completed trick
            </button>
          </div>

          <div v-if="completedTricks.length === 0" class="rounded-3xl border border-dashed border-border bg-slate-950/20 px-6 py-8 text-sm text-slate-500">
            No completed tricks entered yet. This is valid for an early-game recommendation.
          </div>

          <TrickEditor
            v-for="(trick, trickIndex) in completedTricks"
            :key="trick.id"
            :title="`Completed trick #${trickIndex + 1}`"
            description="Fill all five rows. Each player can appear only once and each card must be unique globally."
            :model-value="trick"
            :used-tokens="[...selectedCardSet]"
            :allow-partial="false"
            removable
            @update-player="(index, value) => setupStore.setEntryPlayer(trick, index, value)"
            @update-card="(index, value) => setupStore.setEntryCard(trick, index, value)"
            @remove="setupStore.removeCompletedTrick(trick.id)"
          />
        </div>
      </div>

      <aside class="space-y-6">
        <div class="rounded-3xl border border-border bg-panel/80 p-6 shadow-soft">
          <h3 class="text-lg font-medium text-white">Validation</h3>
          <div v-if="validationErrors.length === 0" class="mt-4 rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-4 text-sm text-emerald-100">
            The setup is structurally valid for the backend move recommendation endpoint.
          </div>
          <ul v-else class="mt-4 space-y-3">
            <li v-for="error in validationErrors" :key="error" class="rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-4 text-sm text-red-100">
              {{ error }}
            </li>
          </ul>
          <div v-if="apiError" class="mt-4 rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-4 text-sm text-red-100">
            {{ apiError }}
          </div>
        </div>

        <div class="rounded-3xl border border-border bg-panel/80 p-6 shadow-soft">
          <h3 class="text-lg font-medium text-white">Selected remaining cards</h3>
          <div v-if="remainingHand.length === 0" class="mt-4 text-sm text-slate-500">No card selected yet.</div>
          <div v-else class="mt-4 grid gap-3 sm:grid-cols-2">
            <CardTokenPill v-for="token in remainingHand" :key="token" :token="token" compact />
          </div>
        </div>

        <div class="rounded-3xl border border-border bg-panel/80 p-6 shadow-soft">
          <h3 class="text-lg font-medium text-white">Action</h3>
          <p class="mt-2 text-sm text-slate-400">Submit the setup to the Python engine and open the recommendation cockpit with ranked actions and explanation blocks.</p>
          <div class="mt-6 flex flex-col gap-3">
            <button
              type="button"
              class="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-accent-light disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!canSubmit"
              @click="submitForm"
            >
              {{ isSubmitting ? 'Evaluating…' : 'Get move recommendation' }}
            </button>
            <button
              type="button"
              class="rounded-2xl border border-border px-4 py-3 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:bg-slate-900/50"
              @click="setupStore.resetAll"
            >
              Reset setup
            </button>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
