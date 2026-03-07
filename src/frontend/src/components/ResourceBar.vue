<template>
  <div class="flex items-center gap-2 min-w-0">
    <div class="flex-1 bg-bar-track rounded-full h-1.5 min-w-[60px] relative overflow-hidden">
      <!-- secondary bar (requested) -->
      <div
        v-if="secondaryPct !== null"
        class="absolute inset-y-0 left-0 bg-bar-secondary rounded-full"
        :style="{ width: secondaryPct + '%' }"
      />
      <!-- primary bar (used or limit) -->
      <div
        v-if="primaryPct !== null"
        class="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
        :class="barColor"
        :style="{ width: primaryPct + '%' }"
      />
    </div>
    <span class="text-xs text-muted whitespace-nowrap w-20 text-right">
      {{ label }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usagePct, pctColor, formatCpu, formatMem } from '../utils/format.js'

const props = defineProps({
  used: { type: Number, default: null },
  total: { type: Number, default: null },
  secondary: { type: Number, default: null },  // e.g. requested
  type: { type: String, default: 'cpu' },       // 'cpu' | 'mem'
})

const fmt = computed(() => props.type === 'cpu' ? formatCpu : formatMem)

const primaryPct = computed(() => usagePct(props.used, props.total))
const secondaryPct = computed(() => usagePct(props.secondary, props.total))
const barColor = computed(() => pctColor(primaryPct.value))

const label = computed(() => {
  if (props.used !== null && props.used !== undefined) {
    return `${fmt.value(props.used)} / ${fmt.value(props.total)}`
  }
  if (props.secondary !== null && props.secondary !== undefined) {
    return `${fmt.value(props.secondary)} req`
  }
  return fmt.value(props.total)
})
</script>
