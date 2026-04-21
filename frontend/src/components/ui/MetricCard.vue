<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint?: string
  accent?: 'gold' | 'emerald' | 'ruby' | 'sapphire' | 'default'
  large?: boolean
}>()
</script>

<template>
  <div class="rounded-xl border panel-base p-4" :class="accent === 'gold' ? 'border-gold/25 shadow-glow-gold' : 'border-border'">
    <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-2">{{ label }}</div>
    <div
      class="font-display font-semibold leading-tight"
      :class="[
        large ? 'text-3xl' : 'text-2xl',
        accent === 'gold' ? 'metric-gold' :
        accent === 'emerald' ? 'text-emerald' :
        accent === 'ruby' ? 'text-ruby' :
        accent === 'sapphire' ? 'text-sapphire' :
        'text-text'
      ]"
    >{{ value }}</div>
    <div v-if="hint" class="mt-1.5 text-xs text-muted leading-snug">{{ hint }}</div>
  </div>
</template>
