function escapeCsv(val) {
  if (val == null) return ''
  if (typeof val === 'object') return escapeCsv(JSON.stringify(val))
  const s = String(val)
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

/** União de chaves; `secao` primeiro quando existir. */
function colunasCsv(rows) {
  const keys = new Set()
  rows.forEach((row) => Object.keys(row).forEach((k) => keys.add(k)))
  const ordered = [...keys]
  if (ordered.includes('secao')) {
    return ['secao', ...ordered.filter((k) => k !== 'secao')]
  }
  return ordered
}

export function linhasParaCsv(rows) {
  if (!rows?.length) return null
  const cols = colunasCsv(rows)
  const lines = [cols.join(',')]
  for (const row of rows) {
    lines.push(cols.map((c) => escapeCsv(row[c])).join(','))
  }
  return `\uFEFF${lines.join('\n')}`
}

export function downloadCsvFromRows(rows, filename) {
  const csv = linhasParaCsv(rows)
  if (!csv) {
    throw new Error('Nada para exportar no filtro atual.')
  }
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export function flattenParaCsv(obj) {
  const out = {}
  for (const [k, v] of Object.entries(obj || {})) {
    if (k === 'lotes') continue
    if (Array.isArray(v) || (v && typeof v === 'object' && !(v instanceof Date))) continue
    out[k] = v
  }
  return out
}
