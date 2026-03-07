const BASE = '/api/1'

export class ClusterUnavailableError extends Error {
  constructor(detail) {
    super(detail || 'Kubernetes cluster unreachable')
    this.name = 'ClusterUnavailableError'
  }
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (res.status === 503) {
    const body = await res.json().catch(() => ({}))
    throw new ClusterUnavailableError(body.detail)
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  return res.json()
}

export const api = {
  getStatus: () => get('/status'),
  getCluster: () => get('/cluster'),
  getNodes: () => get('/nodes'),
  getNamespaces: () => get('/namespaces'),
  getPods: (namespace) => get(`/namespaces/${encodeURIComponent(namespace)}/pods`),
  getPodDetail: (namespace, pod) =>
    get(`/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(pod)}`),
}
