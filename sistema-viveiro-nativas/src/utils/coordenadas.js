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

/** Zona UTM (1–60) a partir da longitude WGS84 */
export function zonaUtmFromLng(lng) {
  return Math.min(60, Math.max(1, Math.floor((Number(lng) + 180) / 6) + 1))
}

/** Lat/lng WGS84 → UTM (hemisfério sul por padrão — Cerrado/Brasil) */
export function latLngParaUtm(lat, lng, zona = null, hemisferioSul = true) {
  const zone = zona != null ? Number(zona) : zonaUtmFromLng(lng)
  const latRad = (Number(lat) * Math.PI) / 180
  const lonRad = (Number(lng) * Math.PI) / 180
  const lonOrigin = (((zone - 1) * 6 - 180 + 3) * Math.PI) / 180

  const n = A / Math.sqrt(1 - E2 * Math.sin(latRad) ** 2)
  const t = Math.tan(latRad) ** 2
  const c = E_PRIME2 * Math.cos(latRad) ** 2
  const a = Math.cos(latRad) * (lonRad - lonOrigin)

  const m =
    A *
    ((1 - E2 / 4 - (3 * E2 ** 2) / 64 - (5 * E2 ** 3) / 256) * latRad -
      ((3 * E2) / 8 + (3 * E2 ** 2) / 32 + (45 * E2 ** 3) / 1024) * Math.sin(2 * latRad) +
      ((15 * E2 ** 2) / 256 + (45 * E2 ** 3) / 1024) * Math.sin(4 * latRad) -
      ((35 * E2 ** 3) / 3072) * Math.sin(6 * latRad))

  let easting =
    K0 *
      n *
      (a +
        ((1 - t + c) * a ** 3) / 6 +
        ((5 - 18 * t + t ** 2 + 72 * c - 58 * E_PRIME2) * a ** 5) / 120) +
    500000

  let northing =
    K0 *
    (m +
      n *
        Math.tan(latRad) *
        (a ** 2 / 2 +
          ((5 - t + 9 * c + 4 * c ** 2) * a ** 4) / 24 +
          ((61 - 58 * t + t ** 2 + 600 * c - 330 * E_PRIME2) * a ** 6) / 720))

  if (hemisferioSul) northing += 10000000

  return {
    zona: zone,
    easting: +easting.toFixed(2),
    northing: +northing.toFixed(2),
  }
}
