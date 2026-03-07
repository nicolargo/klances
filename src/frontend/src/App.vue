<template>
  <div class="min-h-screen flex flex-col">

    <TopMenu
      :cluster="store.cluster"
      :loading="store.loading"
      :error="store.error"
      :cluster-reachable="store.clusterReachable"
      :dark="isDark"
      v-model:interval="refreshInterval"
      @refresh="doRefresh"
      @toggle-theme="toggleTheme"
    />

    <main class="flex-1 p-4 space-y-4 max-w-screen-2xl mx-auto w-full">

      <!-- Cluster unreachable banner -->
      <Transition name="panel">
        <div
          v-if="store.clusterReachable === false"
          class="k-alert p-6 flex flex-col items-center gap-3 text-center"
        >
          <svg class="w-10 h-10 text-red-500/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <div>
            <p class="text-red-400 font-semibold text-base">Kubernetes cluster unreachable</p>
            <p class="text-muted text-sm mt-1">
              Klances cannot connect to the cluster. Check that your cluster is running and
              <code class="text-body bg-input px-1 rounded text-xs">~/.kube/config</code> is valid.
            </p>
          </div>
          <p class="text-ghost text-xs animate-pulse">Retrying automatically every {{ refreshInterval }}s...</p>
        </div>
      </Transition>

      <!-- Main panels (only when cluster is reachable or status unknown) -->
      <template v-if="store.clusterReachable !== false">
        <!-- Panel 1: Nodes + Namespaces (always visible) -->
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <NodeList :nodes="store.nodes" />
          <NamespaceList
            :namespaces="store.namespaces"
            :selected="store.selectedNamespace"
            @select="onSelectNamespace"
          />
        </div>

        <!-- Panel 2: Pod list (when a namespace is selected) -->
        <Transition name="panel">
          <PodList
            v-if="store.selectedNamespace"
            :namespace="store.selectedNamespace"
            :pods="store.pods"
            :selected="store.selectedPod"
            @select="onSelectPod"
            @close="onSelectNamespace(null)"
          />
        </Transition>

        <!-- Panel 3: Pod detail (when a pod is selected) -->
        <Transition name="panel">
          <PodDetail
            v-if="store.selectedPod && store.podDetail"
            :pod="store.podDetail"
            @close="onSelectPod(null)"
          />
        </Transition>

        <!-- Loading skeleton for pod detail -->
        <div
          v-if="store.selectedPod && !store.podDetail"
          class="animate-pulse h-40 rounded-lg bg-hover/40 border border-line/30"
        />
      </template>

    </main>

    <BottomMenu />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useKlancesStore } from './stores/klances.js'
import TopMenu from './components/TopMenu.vue'
import BottomMenu from './components/BottomMenu.vue'
import NodeList from './components/NodeList.vue'
import NamespaceList from './components/NamespaceList.vue'
import PodList from './components/PodList.vue'
import PodDetail from './components/PodDetail.vue'

const store = useKlancesStore()
const refreshInterval = ref(5)
const isDark = ref(true)
let timer = null

// ── Theme ──────────────────────────────────────
function applyTheme() {
  document.documentElement.classList.toggle('light', !isDark.value)
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('klances-theme', isDark.value ? 'dark' : 'light')
  applyTheme()
}

// ── Data refresh ───────────────────────────────
async function doRefresh() {
  await store.refreshAll()
}

function startTimer() {
  stopTimer()
  if (refreshInterval.value > 0) {
    timer = setInterval(doRefresh, refreshInterval.value * 1000)
  }
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(refreshInterval, () => {
  startTimer()
})

onMounted(async () => {
  const saved = localStorage.getItem('klances-theme')
  isDark.value = saved !== 'light'
  applyTheme()

  await doRefresh()
  startTimer()
})

onUnmounted(() => {
  stopTimer()
})

async function onSelectNamespace(ns) {
  await store.selectNamespace(ns)
}

async function onSelectPod(pod) {
  await store.selectPod(pod)
}
</script>

<style>
.panel-enter-active,
.panel-leave-active {
  transition: all 0.25s ease;
}
.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
