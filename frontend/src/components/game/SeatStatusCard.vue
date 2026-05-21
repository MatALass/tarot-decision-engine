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
  { highlighted: false, cards: () => [], meta: '' },
)
</script>

<template>
  <div
    class="rounded-xl border p-4 transition-all duration-200"
    :class="highlighted
      ? 'border-gold/35 bg-gold/6 shadow-glow-gold'
      : 'border-border bg-panel'"
  >
    <div class="flex items-start justify-between gap-2">
      <div>
        <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-1">
          Siège {{ seat }}
        </div>
        <div
          class="font-display text-sm font-semibold"
          :class="highlighted ? 'text-gold-light' : 'text-text'"
        >{{ role }}</div>
        <div class="text-xs text-subtle mt-0.5 leading-snug">{{ status }}</div>
      </div>
      <div
        v-if="meta"
        class="shrink-0 rounded-lg border px-2.5 py-1.5 text-[10px] font-medium"
        :class="highlighted ? 'border-gold/30 bg-gold/10 text-gold' : 'border-border bg-deep text-subtle'"
      >{{ meta }}</div>
    </div>

    <div v-if="cards.length > 0" class="mt-3 flex flex-wrap gap-1.5">
      <CardTokenPill v-for="card in cards" :key="`${seat}-${card}`" :token="card" compact :active="highlighted" />
    </div>
    <div v-else class="mt-3 h-6 flex items-center">
      <div class="h-px w-full border-t border-dashed border-border"></div>
    </div>
  </div>
</template>
