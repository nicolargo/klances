<template>
  <div class="k-panel space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <div class="flex items-center gap-3 flex-wrap">
          <h2 class="text-base font-semibold text-heading truncate">{{ pod.name }}</h2>
          <StatusBadge :status="pod.status" />
        </div>
        <div class="mt-1 flex flex-wrap gap-4 text-xs text-faint">
          <span v-if="pod.ip">IP: <span class="text-body font-mono">{{ pod.ip }}</span></span>
          <span v-if="pod.node">Node: <span class="text-body">{{ pod.node }}</span></span>
          <span>CPU used: <span class="text-body">{{ formatCpu(pod.cpu.used) }}</span></span>
          <span>Mem used: <span class="text-body">{{ formatMem(pod.memory.used) }}</span></span>
        </div>
      </div>
      <button
        @click="$emit('close')"
        class="text-faint hover:text-heading transition-colors shrink-0"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Services & Ingresses -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Services -->
      <div>
        <h3 class="k-section-title">
          <svg class="w-3.5 h-3.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.143 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
          </svg>
          Services ({{ pod.services.length }})
        </h3>
        <div v-if="pod.services.length > 0" class="space-y-1.5">
          <div
            v-for="svc in pod.services"
            :key="svc.name"
            class="bg-card border border-line/40 rounded px-3 py-2"
          >
            <div class="flex items-center gap-2">
              <span class="text-heading text-sm font-medium">{{ svc.name }}</span>
              <span class="k-tag text-xs">{{ svc.type }}</span>
            </div>
            <div class="mt-1 text-xs text-faint">
              <span v-if="svc.cluster_ip" class="font-mono">{{ svc.cluster_ip }}</span>
              <span v-if="svc.ports.length" class="ml-2">{{ svc.ports.join(', ') }}</span>
            </div>
          </div>
        </div>
        <p v-else class="text-ghost text-xs">No services</p>
      </div>

      <!-- Ingresses -->
      <div>
        <h3 class="k-section-title">
          <svg class="w-3.5 h-3.5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          Ingresses ({{ pod.ingresses.length }})
        </h3>
        <div v-if="pod.ingresses.length > 0" class="space-y-1.5">
          <div
            v-for="ing in pod.ingresses"
            :key="ing.name"
            class="bg-card border border-line/40 rounded px-3 py-2"
          >
            <div class="text-heading text-sm font-medium">{{ ing.name }}</div>
            <div class="mt-1 space-y-0.5">
              <div v-for="path in ing.paths" :key="path" class="text-xs text-muted font-mono">{{ path }}</div>
            </div>
          </div>
        </div>
        <p v-else class="text-ghost text-xs">No ingresses</p>
      </div>
    </div>

    <!-- Events -->
    <div>
      <h3 class="k-section-title">
        <svg class="w-3.5 h-3.5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Events ({{ pod.events.length }})
      </h3>
      <div v-if="pod.events.length > 0" class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="text-left text-ghost border-b border-line/40">
              <th class="pb-1.5 pr-4 font-medium">Time</th>
              <th class="pb-1.5 pr-4 font-medium">Type</th>
              <th class="pb-1.5 pr-4 font-medium">Reason</th>
              <th class="pb-1.5 font-medium">Message</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(evt, i) in pod.events"
              :key="i"
              class="border-b border-line/20"
              :class="evt.type === 'Warning' ? 'k-warning' : 'text-muted'"
            >
              <td class="py-1.5 pr-4 font-mono whitespace-nowrap text-faint">{{ formatTs(evt.timestamp) }}</td>
              <td class="py-1.5 pr-4 whitespace-nowrap">{{ evt.type ?? '—' }}</td>
              <td class="py-1.5 pr-4 whitespace-nowrap font-medium">{{ evt.reason ?? '—' }}</td>
              <td class="py-1.5 text-muted break-all">{{ evt.message ?? '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-ghost text-xs">No events</p>
    </div>

    <!-- Logs -->
    <div>
      <h3 class="k-section-title">
        <svg class="w-3.5 h-3.5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Logs
      </h3>
      <pre
        class="bg-code-bg border border-line/40 rounded p-3 text-xs text-body font-mono overflow-auto max-h-80 whitespace-pre-wrap break-all"
      >{{ pod.logs || '(no logs available)' }}</pre>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'
import { formatCpu, formatMem } from '../utils/format.js'

defineProps({
  pod: { type: Object, required: true },
})

defineEmits(['close'])

function formatTs(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleString()
  } catch {
    return ts
  }
}
</script>
