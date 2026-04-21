<script setup lang="ts">
import SectionHeader from '@/components/ui/SectionHeader.vue'
</script>

<template>
  <section>
    <SectionHeader
      eyebrow="Research"
      title="Analysis and probability workspace"
      description="This route is reserved for the future high-value research layer: card probabilities, heatmaps, hand percentile studies, and strategic scenario analysis. The page exists now so the frontend architecture already supports that expansion."
    />

    <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <div class="rounded-3xl border border-border bg-slate-950/40 p-6 text-sm text-slate-400">Posterior probability heatmaps</div>
      <div class="rounded-3xl border border-border bg-slate-950/40 p-6 text-sm text-slate-400">Hand strength percentile view</div>
      <div class="rounded-3xl border border-border bg-slate-950/40 p-6 text-sm text-slate-400">Card impact and synergy studies</div>
    </div>
  </section>
</template>
