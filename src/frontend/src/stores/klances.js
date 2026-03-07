import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, ClusterUnavailableError } from '../api/index.js'

export const useKlancesStore = defineStore('klances', () => {
  const cluster = ref(null)
  const nodes = ref([])
  const namespaces = ref([])
  const pods = ref([])
  const podDetail = ref(null)

  const selectedNamespace = ref(null)
  const selectedPod = ref(null)

  const loading = ref(false)
  const error = ref(null)
  const clusterReachable = ref(null)   // null = unknown, true/false = known

  async function refreshClusterData() {
    try {
      error.value = null
      // Check cluster connectivity first via /status
      const status = await api.getStatus()
      if (!status.cluster_reachable) {
        clusterReachable.value = false
        error.value = status.cluster_error || 'Kubernetes cluster unreachable'
        return
      }
      clusterReachable.value = true

      const [clusterData, nodesData, namespacesData] = await Promise.all([
        api.getCluster(),
        api.getNodes(),
        api.getNamespaces(),
      ])
      cluster.value = clusterData
      nodes.value = nodesData
      namespaces.value = namespacesData
    } catch (e) {
      if (e instanceof ClusterUnavailableError) {
        clusterReachable.value = false
      }
      error.value = e.message
    }
  }

  async function selectNamespace(namespace) {
    selectedNamespace.value = namespace
    selectedPod.value = null
    podDetail.value = null
    pods.value = []
    if (!namespace) return
    try {
      pods.value = await api.getPods(namespace)
    } catch (e) {
      error.value = e.message
    }
  }

  async function selectPod(pod) {
    selectedPod.value = pod
    podDetail.value = null
    if (!pod || !selectedNamespace.value) return
    try {
      podDetail.value = await api.getPodDetail(selectedNamespace.value, pod)
    } catch (e) {
      error.value = e.message
    }
  }

  async function refreshPods() {
    if (!selectedNamespace.value) return
    try {
      pods.value = await api.getPods(selectedNamespace.value)
    } catch (e) {
      error.value = e.message
    }
  }

  async function refreshPodDetail() {
    if (!selectedNamespace.value || !selectedPod.value) return
    try {
      podDetail.value = await api.getPodDetail(selectedNamespace.value, selectedPod.value)
    } catch (e) {
      error.value = e.message
    }
  }

  async function refreshAll() {
    loading.value = true
    await refreshClusterData()
    await refreshPods()
    await refreshPodDetail()
    loading.value = false
  }

  return {
    cluster, nodes, namespaces, pods, podDetail,
    selectedNamespace, selectedPod,
    loading, error, clusterReachable,
    refreshClusterData, refreshAll,
    selectNamespace, selectPod,
  }
})
