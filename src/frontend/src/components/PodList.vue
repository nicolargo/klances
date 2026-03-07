<template>
  <div class="k-panel">
    <div class="flex items-center justify-between mb-3">
      <h2 class="k-panel-title !mb-0">
        <svg class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        Pods
        <span class="text-faint font-normal text-xs">in</span>
        <span class="text-cyan-300">{{ namespace }}</span>
        <span class="text-ghost font-normal text-xs ml-1">({{ pods.length }})</span>
      </h2>

      <button
        @click="$emit('close')"
        class="text-faint hover:text-heading text-xs flex items-center gap-1 transition-colors"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
        close
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-faint text-xs border-b border-line/60">
            <th class="pb-2 pr-4 font-medium">Name</th>
            <th class="pb-2 pr-4 font-medium">Status</th>
            <th class="pb-2 pr-4 font-medium">CPU</th>
            <th class="pb-2 pr-4 font-medium">Memory</th>
            <th class="pb-2 pr-4 font-medium">IP</th>
            <th class="pb-2 font-medium">Node</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pod in pods"
            :key="pod.name"
            @click="$emit('select', pod.name)"
            class="border-b border-line/30 cursor-pointer transition-colors"
            :class="selected === pod.name ? 'k-sel-pod' : 'hover:bg-hover/40'"
          >
            <td class="py-2 pr-4 text-heading font-medium max-w-[200px] truncate">
              <span :class="selected === pod.name ? 'k-sel-pod-text' : ''">{{ pod.name }}</span>
            </td>
            <td class="py-2 pr-4">
              <StatusBadge :status="pod.status" />
            </td>
            <td class="py-2 pr-4 min-w-[180px]">
              <ResourceBar
                :used="pod.cpu.used"
                :total="pod.cpu.limit ?? pod.cpu.requested"
                :secondary="pod.cpu.requested"
                type="cpu"
              />
              <div class="text-xs text-ghost mt-0.5">
                req {{ formatCpu(pod.cpu.requested) }} / lim {{ formatCpu(pod.cpu.limit) }}
              </div>
            </td>
            <td class="py-2 pr-4 min-w-[180px]">
              <ResourceBar
                :used="pod.memory.used"
                :total="pod.memory.limit ?? pod.memory.requested"
                :secondary="pod.memory.requested"
                type="mem"
              />
              <div class="text-xs text-ghost mt-0.5">
                req {{ formatMem(pod.memory.requested) }} / lim {{ formatMem(pod.memory.limit) }}
              </div>
            </td>
            <td class="py-2 pr-4 text-muted text-xs font-mono">{{ pod.ip ?? '—' }}</td>
            <td class="py-2 text-faint text-xs truncate max-w-[120px]">{{ pod.node ?? '—' }}</td>
          </tr>
        </tbody>
      </table>

      <p v-if="pods.length === 0" class="text-ghost text-sm py-4 text-center">No pods in this namespace</p>
    </div>

    <p v-if="selected" class="mt-2 text-xs text-faint">
      Click a pod to view details &nbsp;&bull;&nbsp;
      <button @click="$emit('select', null)" class="text-muted hover:text-heading underline">clear selection</button>
    </p>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'
import ResourceBar from './ResourceBar.vue'
import { formatCpu, formatMem } from '../utils/format.js'

defineProps({
  namespace: { type: String, required: true },
  pods: { type: Array, default: () => [] },
  selected: { type: String, default: null },
})

defineEmits(['select', 'close'])
</script>
