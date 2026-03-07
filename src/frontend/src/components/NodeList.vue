<template>
  <div class="k-panel">
    <h2 class="k-panel-title">
      <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
      </svg>
      Nodes
      <span class="text-ghost font-normal text-xs ml-1">({{ nodes.length }})</span>
    </h2>

    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-faint text-xs border-b border-line/60">
            <th class="pb-2 pr-4 font-medium">Name</th>
            <th class="pb-2 pr-4 font-medium">Roles</th>
            <th class="pb-2 pr-4 font-medium">Version</th>
            <th class="pb-2 pr-4 font-medium">Status</th>
            <th class="pb-2 pr-4 font-medium">CPU</th>
            <th class="pb-2 font-medium">Memory</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="node in nodes"
            :key="node.name"
            class="border-b border-line/30 hover:bg-hover/40 transition-colors"
          >
            <td class="py-2 pr-4 text-heading font-medium">{{ node.name }}</td>
            <td class="py-2 pr-4">
              <div class="flex flex-wrap gap-1">
                <span v-for="role in node.roles" :key="role" class="k-tag">{{ role }}</span>
              </div>
            </td>
            <td class="py-2 pr-4 text-muted text-xs">{{ node.version }}</td>
            <td class="py-2 pr-4">
              <StatusBadge :status="node.status" />
            </td>
            <td class="py-2 pr-4 min-w-[160px]">
              <ResourceBar
                :used="node.cpu.used"
                :total="node.cpu.allocatable ?? node.cpu.capacity"
                type="cpu"
              />
            </td>
            <td class="py-2 min-w-[160px]">
              <ResourceBar
                :used="node.memory.used"
                :total="node.memory.allocatable ?? node.memory.capacity"
                type="mem"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="nodes.length === 0" class="text-ghost text-sm py-4 text-center">No nodes found</p>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'
import ResourceBar from './ResourceBar.vue'

defineProps({
  nodes: { type: Array, default: () => [] },
})
</script>
