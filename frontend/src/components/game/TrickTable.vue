<script setup lang="ts">
import CardTokenPill from '@/components/setup/CardTokenPill.vue'

export interface TrickRow {
  seat: number
  card: string
  winner?: boolean
  lead?: boolean
}

defineProps<{
  title: string
  subtitle: string
  rows: TrickRow[]
  emptyMessage: string
}>()
</script>

<template>
  <div class="rounded-2xl panel-base overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid #1e2538;">
      <div>
        <h3 class="font-display text-sm font-semibold tracking-wider text-gold-light">{{ title }}</h3>
        <p class="text-xs text-subtle mt-0.5">{{ subtitle }}</p>
      </div>
      <div class="rounded-lg border border-border bg-deep px-3 py-1.5 text-xs font-mono text-subtle">
        {{ rows.length }}/5
      </div>
    </div>

    <div
      v-if="rows.length === 0"
      class="flex items-center justify-center gap-2 px-5 py-10 text-xs text-subtle"
    >
      <span class="opacity-30">◈</span>
      {{ emptyMessage }}
    </div>

    <div v-else class="divide-y divide-border">
      <div
        v-for="(row, index) in rows"
        :key="`${title}-${index}-${row.seat}-${row.card}`"
        class="flex items-center gap-4 px-5 py-3.5"
        :class="row.lead ? 'bg-sapphire/4' : row.winner ? 'bg-emerald/4' : ''"
      >
        <div
          class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold"
          :class="row.lead ? 'bg-sapphire/20 text-sapphire' : 'bg-border text-muted'"
        >#{{ index + 1 }}</div>
        <div class="w-16 text-xs text-subtle">J{{ row.seat }}</div>
        <CardTokenPill :token="row.card" compact />
        <div class="ml-auto flex items-center gap-1.5">
          <span
            v-if="row.lead"
            class="rounded-full border border-sapphire/25 bg-sapphire/10 px-2 py-0.5 text-[10px] text-sapphire"
          >Entame</span>
          <span
            v-if="row.winner"
            class="rounded-full border border-emerald/25 bg-emerald/10 px-2 py-0.5 text-[10px] text-emerald"
          >Gagnant</span>
        </div>
      </div>
    </div>
  </div>
</template>
