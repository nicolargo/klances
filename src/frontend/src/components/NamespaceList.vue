<template>
  <div class="k-panel">
    <h2 class="k-panel-title">
      <svg class="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      Namespaces
      <span class="text-ghost font-normal text-xs ml-1">({{ namespaces.length }})</span>
    </h2>

    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-faint text-xs border-b border-line/60">
            <th class="pb-2 pr-4 font-medium">Name</th>
            <th class="pb-2 pr-4 font-medium">Status</th>
            <th class="pb-2 pr-4 font-medium">Pods</th>
            <th class="pb-2 pr-4 font-medium">CPU</th>
            <th class="pb-2 font-medium">Memory</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="ns in namespaces"
            :key="ns.name"
            @click="$emit('select', ns.name)"
            class="border-b border-line/30 cursor-pointer transition-colors"
            :class="selected === ns.name ? 'k-sel-ns' : 'hover:bg-hover/40'"
          >
            <td class="py-2 pr-4 text-heading font-medium">
              <span :class="selected === ns.name ? 'k-sel-ns-text' : ''">{{ ns.name }}</span>
            </td>
            <td class="py-2 pr-4">
              <StatusBadge :status="ns.status" />
            </td>
            <td class="py-2 pr-4 text-muted text-center">{{ ns.pod_count }}</td>
            <td class="py-2 pr-4 min-w-[160px]">
              <ResourceBar
                :used="ns.cpu.used"
                :total="ns.cpu.limit || ns.cpu.requested"
                :secondary="ns.cpu.requested"
                type="cpu"
              />
            </td>
            <td class="py-2 min-w-[160px]">
              <ResourceBar
                :used="ns.memory.used"
                :total="ns.memory.limit || ns.memory.requested"
                :secondary="ns.memory.requested"
                type="mem"
              />
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="namespaces.length === 0" class="text-ghost text-sm py-4 text-center">No namespaces found</p>
    </div>

    <p v-if="selected" class="mt-2 text-xs text-faint">
      Click a namespace to view its pods &nbsp;&bull;&nbsp;
      <button @click="$emit('select', null)" class="text-muted hover:text-heading underline">clear selection</button>
    </p>
  </div>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'
import ResourceBar from './ResourceBar.vue'

defineProps({
  namespaces: { type: Array, default: () => [] },
  selected: { type: String, default: null },
})

defineEmits(['select'])
</script>
