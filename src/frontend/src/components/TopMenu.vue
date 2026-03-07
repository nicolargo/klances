<template>
  <header class="sticky top-0 z-50 border-b border-line bg-header-bg backdrop-blur-sm">
    <div class="px-4 py-3 flex items-center justify-between gap-4">

      <!-- Left: branding + cluster info -->
      <div class="flex items-center gap-4 min-w-0">
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-blue-400 font-bold text-lg tracking-tight">Klances</span>
          <span class="text-ghost text-sm">|</span>
        </div>

        <template v-if="clusterReachable === false">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <span class="text-red-400 text-sm">Cluster unreachable</span>
          </div>
        </template>
        <template v-else-if="cluster">
          <div class="flex items-center gap-3 min-w-0">
            <span class="text-heading font-medium truncate">{{ cluster.name }}</span>
            <StatusBadge :status="cluster.status" />
            <span class="text-faint text-xs hidden sm:inline">
              v{{ cluster.version }} &bull; {{ cluster.node_count }} node{{ cluster.node_count !== 1 ? 's' : '' }}
            </span>
          </div>
        </template>
        <template v-else>
          <span class="text-faint text-sm animate-pulse">Connecting...</span>
        </template>
      </div>

      <!-- Right: controls -->
      <div class="flex items-center gap-3 shrink-0">
        <span v-if="loading" class="text-faint text-xs animate-pulse">refreshing...</span>

        <!-- Theme toggle -->
        <button
          @click="$emit('toggle-theme')"
          class="p-1.5 rounded bg-input hover:bg-hover border border-line text-muted hover:text-heading transition-colors"
          :title="dark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <!-- Sun icon (shown in dark mode → click for light) -->
          <svg v-if="dark" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
          </svg>
          <!-- Moon icon (shown in light mode → click for dark) -->
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
          </svg>
        </button>

        <select
          v-model="intervalModel"
          class="bg-input border border-line text-body text-xs rounded px-2 py-1 focus:outline-none focus:border-blue-500"
        >
          <option :value="0">manual</option>
          <option :value="5">5s</option>
          <option :value="10">10s</option>
          <option :value="30">30s</option>
          <option :value="60">60s</option>
        </select>

        <button
          @click="$emit('refresh')"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-input hover:bg-hover border border-line text-body text-xs rounded transition-colors"
        >
          <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import StatusBadge from './StatusBadge.vue'

const props = defineProps({
  cluster: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
  interval: { type: Number, default: 5 },
  clusterReachable: { type: Boolean, default: null },
  dark: { type: Boolean, default: true },
})

const emit = defineEmits(['refresh', 'update:interval', 'toggle-theme'])

const intervalModel = computed({
  get: () => props.interval,
  set: (v) => emit('update:interval', Number(v)),
})
</script>
