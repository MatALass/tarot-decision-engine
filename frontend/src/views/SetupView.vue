<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import CardPicker from '@/components/setup/CardPicker.vue'
import CardTokenPill from '@/components/setup/CardTokenPill.vue'
import TrickEditor from '@/components/setup/TrickEditor.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
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

const contractOptions: Array<{ code: ContractCode; label: string }> = [
  { code: 'PRISE', label: 'Prise' },
  { code: 'GARDE', label: 'Garde' },
  { code: 'GARDE_SANS', label: 'Garde Sans' },
  { code: 'GARDE_CONTRE', label: 'Garde Contre' },
]
const playerOptions = [0, 1, 2, 3, 4]

const usedOutsideHand = computed(() =>
  sortCardTokens([...selectedCardSet.value].filter((token) => !remainingHand.value.includes(token))),
)

const ownPlayedCount = computed(() => {
  const ownCurrent = currentTrick.value.entries.filter(
    (entry) => entry.playerIndex === playerIndex.value && entry.card !== null,
  ).length
  const ownCompleted = completedTricks.value.reduce(
    (count, trick) =>
      count + trick.entries.filter((entry) => entry.playerIndex === playerIndex.value && entry.card !== null).length,
    0,
  )
  return ownCurrent + ownCompleted
})

const handTotal = computed(() => remainingHand.value.length + ownPlayedCount.value)
const handValid = computed(() => handTotal.value === 15)

async function submitForm(): Promise<void> {
  const ok = await setupStore.submitRecommendation()
  if (ok) {
    await router.push('/recommendation')
  }
}

const selectClass = 'w-full rounded-xl border border-border bg-deep px-3 py-2.5 text-sm text-text outline-none transition focus:border-gold/40'
</script>

<template>
  <section class="animate-fade-in">
    <SectionHeader
      eyebrow="Configuration"
      title="État de partie"
      description="Définissez l'état observable : main restante, plis joués, contexte de la donne. L'engine Monte Carlo évaluera les coups légaux."
    />

    <div class="grid gap-6 2xl:grid-cols-[1fr_320px]">
      <!-- Left column -->
      <div class="space-y-5 min-w-0">
        <!-- Card picker -->
        <CardPicker
          title="Main restante"
          description="Sélectionnez les cartes encore en main. La reconstitution doit atteindre exactement 15 cartes avec les coups déjà joués."
          :selected="remainingHand"
          :disabled-tokens="usedOutsideHand"
          :max-selection="15"
          @toggle="setupStore.toggleRemainingHandCard"
        />

        <!-- Context grid -->
        <div class="grid gap-5 xl:grid-cols-[1fr_1fr]">
          <!-- Current trick -->
          <TrickEditor
            title="Pli courant"
            description="Entrez les cartes déjà jouées dans ce pli, dans l'ordre de jeu."
            :model-value="currentTrick"
            :used-tokens="[...selectedCardSet]"
            :allow-partial="true"
            @update-player="(index, value) => setupStore.setEntryPlayer(currentTrick, index, value)"
            @update-card="(index, value) => setupStore.setEntryCard(currentTrick, index, value)"
          />

          <!-- Game context -->
          <div class="rounded-2xl panel-base overflow-hidden">
            <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
              <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Contexte de partie</h3>
              <p class="mt-1 text-xs text-subtle">Paramètres envoyés à l'API de recommandation.</p>
            </div>
            <div class="px-5 py-4 grid gap-3 sm:grid-cols-2">
              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Contrat</span>
                <select v-model="contract" :class="selectClass">
                  <option v-for="item in contractOptions" :key="item.code" :value="item.code">{{ item.label }}</option>
                </select>
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Joueur observé</span>
                <select v-model.number="playerIndex" :class="selectClass">
                  <option v-for="p in playerOptions" :key="p" :value="p">Joueur {{ p }}</option>
                </select>
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Preneur</span>
                <select v-model.number="takerIndex" :class="selectClass">
                  <option v-for="p in playerOptions" :key="p" :value="p">Joueur {{ p }}</option>
                </select>
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Partenaire</span>
                <select v-model="partnerIndex" :class="selectClass">
                  <option :value="null">Aucun</option>
                  <option v-for="p in playerOptions" :key="p" :value="p">Joueur {{ p }}</option>
                </select>
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Prochain joueur</span>
                <select v-model.number="nextPlayerIndex" :class="selectClass">
                  <option v-for="p in playerOptions" :key="p" :value="p">Joueur {{ p }}</option>
                </select>
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Simulations MC</span>
                <input v-model.number="nSamples" type="number" min="1" max="100000" :class="selectClass" />
              </label>

              <label class="space-y-1.5">
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Graine aléatoire</span>
                <input v-model.number="seed" type="number" :class="selectClass" />
              </label>

              <!-- Reconstruction check -->
              <div
                class="rounded-xl border px-3 py-3 text-sm flex items-center gap-3"
                :class="handValid ? 'border-emerald/30 bg-emerald/5' : 'border-border bg-deep'"
              >
                <div
                  class="h-2 w-2 shrink-0 rounded-full"
                  :class="handValid ? 'bg-emerald' : 'bg-muted'"
                  :style="handValid ? 'box-shadow: 0 0 6px rgba(42,171,111,0.6)' : ''"
                ></div>
                <div>
                  <div class="text-[10px] tracking-[0.2em] text-subtle uppercase mb-0.5">Reconstitution</div>
                  <div :class="handValid ? 'text-emerald font-semibold' : 'text-text'">
                    {{ remainingHand.length }} + {{ ownPlayedCount }} = {{ handTotal }}<span class="text-muted">/15</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed tricks -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <div class="h-px w-4 bg-gold/40"></div>
                <span class="text-[10px] tracking-[0.25em] text-subtle uppercase">Plis terminés</span>
              </div>
              <h3 class="font-display text-sm font-semibold text-text">Historique des plis</h3>
            </div>
            <button
              type="button"
              class="flex items-center gap-2 rounded-xl border border-gold/25 bg-gold/8 px-4 py-2 text-xs font-medium text-gold transition hover:bg-gold/15 hover:border-gold/40"
              @click="setupStore.addCompletedTrick"
            >
              <span class="text-base leading-none">+</span>
              Ajouter un pli
            </button>
          </div>

          <div
            v-if="completedTricks.length === 0"
            class="flex items-center gap-3 rounded-xl border border-dashed border-border px-5 py-6 text-sm text-subtle"
          >
            <span class="text-xl opacity-40">◈</span>
            Aucun pli terminé. Valide pour un état de début de partie.
          </div>

          <TrickEditor
            v-for="(trick, trickIndex) in completedTricks"
            :key="trick.id"
            :title="`Pli terminé #${trickIndex + 1}`"
            description="5 cartes, un joueur par entrée, aucune carte dupliquée."
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

      <!-- Right sidebar -->
      <aside class="space-y-4">
        <!-- Validation -->
        <div class="rounded-2xl panel-base overflow-hidden">
          <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
            <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Validation</h3>
          </div>
          <div class="px-5 py-4">
            <div
              v-if="validationErrors.length === 0"
              class="flex items-center gap-2.5 rounded-xl border border-emerald/25 bg-emerald/8 px-4 py-3"
            >
              <div class="h-1.5 w-1.5 rounded-full bg-emerald" style="box-shadow: 0 0 6px rgba(42,171,111,0.5);"></div>
              <span class="text-xs font-medium text-emerald">Configuration valide</span>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="error in validationErrors"
                :key="error"
                class="flex items-start gap-2.5 rounded-xl border border-ruby/20 bg-ruby/8 px-4 py-3"
              >
                <span class="text-ruby mt-0.5 shrink-0 text-xs">✕</span>
                <span class="text-xs text-red-200 leading-snug">{{ error }}</span>
              </div>
            </div>
            <div
              v-if="apiError"
              class="mt-3 flex items-start gap-2.5 rounded-xl border border-amber/25 bg-amber/8 px-4 py-3"
            >
              <span class="text-amber text-xs shrink-0 mt-0.5">⚠</span>
              <span class="text-xs text-amber leading-snug">{{ apiError }}</span>
            </div>
          </div>
        </div>

        <!-- Hand preview -->
        <div class="rounded-2xl panel-base overflow-hidden">
          <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
            <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Main sélectionnée</h3>
          </div>
          <div class="px-5 py-4">
            <div v-if="remainingHand.length === 0" class="text-xs text-subtle italic">
              Aucune carte sélectionnée.
            </div>
            <div v-else class="flex flex-wrap gap-1.5">
              <CardTokenPill v-for="token in remainingHand" :key="token" :token="token" compact />
            </div>
          </div>
        </div>

        <!-- Action -->
        <div class="rounded-2xl panel-base overflow-hidden">
          <div class="px-5 py-4" style="border-bottom: 1px solid #1e2538;">
            <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">Analyse</h3>
            <p class="mt-1 text-xs text-subtle leading-relaxed">Soumettre l'état à l'engine pour recevoir la recommandation Monte Carlo.</p>
          </div>
          <div class="px-5 py-4 space-y-3">
            <button
              type="button"
              class="btn-gold w-full rounded-xl px-4 py-3 text-sm"
              :disabled="!canSubmit"
              @click="submitForm"
            >
              <span v-if="isSubmitting" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Simulation en cours…
              </span>
              <span v-else>Obtenir la recommandation →</span>
            </button>
            <button
              type="button"
              class="w-full rounded-xl border border-border px-4 py-2.5 text-xs font-medium text-subtle transition hover:border-rim hover:bg-card hover:text-text"
              @click="setupStore.resetAll"
            >
              Réinitialiser
            </button>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
