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
  <div class="rounded-3xl border border-border bg-slate-950/40 p-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="text-lg font-medium text-white">{{ title }}</h3>
        <p class="mt-2 text-sm text-slate-400">{{ subtitle }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-slate-900/50 px-4 py-2 text-sm text-slate-300">
        {{ rows.length }} / 5 cards
      </div>
    </div>

    <div v-if="rows.length === 0" class="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-500">
      {{ emptyMessage }}
    </div>

    <div v-else class="mt-6 overflow-hidden rounded-3xl border border-border">
      <table class="min-w-full divide-y divide-border text-sm">
        <thead class="bg-slate-900/80 text-left text-slate-400">
          <tr>
            <th class="px-4 py-3 font-medium">Order</th>
            <th class="px-4 py-3 font-medium">Seat</th>
            <th class="px-4 py-3 font-medium">Card</th>
            <th class="px-4 py-3 font-medium">Markers</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border bg-slate-950/40 text-slate-100">
          <tr v-for="(row, index) in rows" :key="`${title}-${index}-${row.seat}-${row.card}`">
            <td class="px-4 py-4">#{{ index + 1 }}</td>
            <td class="px-4 py-4">Player {{ row.seat }}</td>
            <td class="px-4 py-4"><CardTokenPill :token="row.card" compact /></td>
            <td class="px-4 py-4">
              <div class="flex flex-wrap gap-2">
                <span v-if="row.lead" class="rounded-full border border-sky-400/20 bg-sky-500/10 px-2.5 py-1 text-xs text-sky-100">Lead</span>
                <span v-if="row.winner" class="rounded-full border border-emerald-400/20 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-100">Winner</span>
                <span v-if="!row.lead && !row.winner" class="text-xs text-slate-500">—</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
