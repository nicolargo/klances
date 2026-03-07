/**
 * Format CPU millicores to a human-readable string.
 * @param {number|null} m - millicores
 */
export function formatCpu(m) {
  if (m === null || m === undefined) return '—'
  if (m >= 1000) return `${(m / 1000).toFixed(2)}c`
  return `${m}m`
}

/**
 * Format memory bytes to a human-readable string.
 * @param {number|null} b - bytes
 */
export function formatMem(b) {
  if (b === null || b === undefined) return '—'
  const gib = b / (1024 ** 3)
  if (gib >= 1) return `${gib.toFixed(1)}G`
  const mib = b / (1024 ** 2)
  if (mib >= 1) return `${mib.toFixed(0)}M`
  const kib = b / 1024
  return `${kib.toFixed(0)}K`
}

/**
 * Compute usage percentage (0-100), capped at 100.
 * @param {number|null} used
 * @param {number|null} total
 */
export function usagePct(used, total) {
  if (!used || !total || total === 0) return null
  return Math.min(100, Math.round((used / total) * 100))
}

/**
 * Return a Tailwind color class based on a percentage.
 * @param {number|null} pct
 */
export function pctColor(pct) {
  if (pct === null || pct === undefined) return 'bg-slate-600'
  if (pct >= 90) return 'bg-red-500'
  if (pct >= 75) return 'bg-yellow-500'
  return 'bg-green-500'
}
