/** UTM WGS84 (hemisfério sul) → lat/lng — preview no formulário */
const K0 = 0.9996
const A = 6378137.0
const E2 = 0.00669438
const E_PRIME2 = 0.006739497

export function utmParaLatLng(easting, northing, zona, hemisferioSul = true) {
  let x = Number(easting) - 500000
  let y = Number(northing)
  if (hemisferioSul) y -= 10000000

  const lonOrigin = (Number(zona) - 1) * 6 - 180 + 3
  const m = y / K0
  const mu = m / (A * (1 - E2 / 4 - (3 * E2 ** 2) / 64 - (5 * E2 ** 3) / 256))

  const e1 = (1 - Math.sqrt(1 - E2)) / (1 + Math.sqrt(1 - E2))
  const phi1 =
    mu +
    ((3 * e1) / 2 - (27 * e1 ** 3) / 32) * Math.sin(2 * mu) +
    ((21 * e1 ** 2) / 16 - (55 * e1 ** 4) / 32) * Math.sin(4 * mu) +
    ((151 * e1 ** 3) / 96) * Math.sin(6 * mu) +
    ((1097 * e1 ** 4) / 512) * Math.sin(8 * mu)

  const n1 = A / Math.sqrt(1 - E2 * Math.sin(phi1) ** 2)
  const t1 = Math.tan(phi1) ** 2
  const c1 = E_PRIME2 * Math.cos(phi1) ** 2
  const r1 = (A * (1 - E2)) / (1 - E2 * Math.sin(phi1) ** 2) ** 1.5
  const d = x / (n1 * K0)

  const lat =
    phi1 -
    ((n1 * Math.tan(phi1)) / r1) *
      (d ** 2 / 2 -
        ((5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * E_PRIME2) * d ** 4) / 24 +
        ((61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * E_PRIME2 - 3 * c1 ** 2) * d ** 6) / 720)

  const lon =
    (d -
      ((1 + 2 * t1 + c1) * d ** 3) / 6 +
      ((5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * E_PRIME2 + 24 * t1 ** 2) * d ** 5) / 120) /
    Math.cos(phi1)

  return {
    latitude: +(lat * (180 / Math.PI)).toFixed(7),
    longitude: +(lonOrigin + lon * (180 / Math.PI)).toFixed(7)
  }
}
