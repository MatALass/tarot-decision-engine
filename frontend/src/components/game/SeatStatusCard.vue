<script setup lang="ts">
import CardTokenPill from '@/components/setup/CardTokenPill.vue'

withDefaults(
  defineProps<{
    seat: number
    role: string
    status: string
    highlighted?: boolean
    cards?: string[]
    meta?: string
  }>(),
  {
    highlighted: false,
    cards: () => [],
    meta: '',
  },
)
</script>

<template>
  <div
    :class="[
      'rounded-3xl border p-5 transition',
      highlighted
        ? 'border-accent/40 bg-accent/10 shadow-[0_0_0_1px_rgba(129,140,248,0.15)]'
        : 'border-border bg-slate-950/40',
    ]"
  >
    <div class="flex items-start justify-between gap-3">
      <div>
        <div class="text-xs uppercase tracking-[0.22em] text-slate-500">Seat {{ seat }}</div>
        <div class="mt-2 text-lg font-semibold text-white">{{ role }}</div>
        <div class="mt-1 text-sm text-slate-400">{{ status }}</div>
      </div>
      <div v-if="meta" class="rounded-2xl border border-border bg-slate-900/50 px-3 py-2 text-xs text-slate-300">
        {{ meta }}
      </div>
    </div>

    <div v-if="cards.length > 0" class="mt-4 grid gap-2 sm:grid-cols-2">
      <CardTokenPill v-for="card in cards" :key="`${seat}-${card}`" :token="card" compact />
    </div>
  </div>
</template>
