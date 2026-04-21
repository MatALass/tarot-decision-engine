<script setup lang="ts">
import { computed } from 'vue'

import { formatCardLabel } from '@/lib/cards'

const props = defineProps<{
  token: string
  active?: boolean
  compact?: boolean
}>()

const baseClasses = computed(() => [
  'rounded-2xl border transition',
  props.compact ? 'px-3 py-2 text-xs' : 'px-3 py-3 text-sm',
  props.active
    ? 'border-accent/50 bg-accent/15 text-white shadow-[0_0_0_1px_rgba(129,140,248,0.2)]'
    : 'border-border bg-slate-950/50 text-slate-300 hover:border-slate-500 hover:bg-slate-900/70',
])
</script>

<template>
  <div :class="baseClasses">
    <div class="font-medium">{{ token }}</div>
    <div v-if="!compact" class="mt-1 text-xs text-slate-400">{{ formatCardLabel(token) }}</div>
  </div>
</template>
