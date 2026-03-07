<template>
  <span class="k-badge" :class="`k-badge-${level}`">
    <span class="k-badge-dot" />
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const GREEN_STATUSES = ['healthy', 'ready', 'running', 'active', 'true', 'bound']
const YELLOW_STATUSES = ['degraded', 'pending', 'terminating', 'containercreating']
const RED_STATUSES = ['error', 'failed', 'crashloopbackoff', 'notready', 'oomkilled', 'unknown']

const level = computed(() => {
  const s = (props.status || '').toLowerCase()
  if (GREEN_STATUSES.includes(s)) return 'green'
  if (YELLOW_STATUSES.includes(s)) return 'yellow'
  if (RED_STATUSES.includes(s)) return 'red'
  return 'green'
})
</script>
