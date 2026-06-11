import { orientacaoFaixa } from '@/constants/viveiroDimensoes'

/** Estimativa de largura de texto em px (SVG / UI). */
export function estimarLarguraTexto(texto, fontSize, fator = 0.55) {
  if (!texto) return 0
  return String(texto).length * fontSize * fator
}

export function truncarTexto(texto, maxPx, fontSize, fator = 0.55) {
  const s = String(texto ?? '')
  if (!s || maxPx <= 0) return ''
  const charW = fontSize * fator
  let max = Math.floor(maxPx / charW)
  if (max < 1) max = 1
  if (s.length <= max) return s
  if (max < 2) return s.slice(0, max)
  return `${s.slice(0, max - 1)}…`
}

const PAD = 6
const GAP_LINHA = 3

function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v))
}

/** Tamanhos de fonte SVG conforme dimensões do retângulo (px no layout). */
export function tamanhosFonteArea(largura, altura) {
  const w = largura || 100
  const h = altura || 80
  const short = Math.min(w, h)
  const long = Math.max(w, h)
  return {
    tipo: clamp(Math.round(short * 0.11 + 2), 9, 15),
    nome: clamp(Math.round(short * 0.15 + long * 0.02), 11, 20),
    badge: clamp(Math.round(short * 0.12 + 2), 10, 17),
  }
}

/**
 * Rótulos do mapa HTML (PlantaBaixa): tamanhos proporcionais ao retângulo,
 * sem compensação de scale (evita fontes gigantes e caixas estourando).
 */
export function rotulosMapaElemento({ largura, altura, nome, temBadge = false, metros = null }) {
  const w = largura || 100
  const h = altura || 80
  const pad = clamp(Math.round(Math.min(w, h) * 0.05), 3, 7)
  const iw = Math.max(12, w - pad * 2)
  const ih = Math.max(12, h - pad * 2)
  const short = Math.min(w, h)
  const nomeStr = String(nome || '')
  const faixa = orientacaoFaixa(w, h)

  let layout = 'padrao'
  if (faixa === 'vertical' && ih >= 48) layout = 'faixa-v'
  else if (faixa === 'horizontal' && iw >= 48) layout = 'faixa-h'
  else if (short < 34 || iw < 26) layout = 'minimal'
  else if (w < 88 || (temBadge && w < 120) || h < 48) layout = 'stacked'

  const fsBadge = clamp(Math.round(short * 0.095 + 7), 8, 11)
  const fsTipo = clamp(Math.round(short * 0.085 + 6), 7, 10)

  const linhasTipo = layout === 'minimal' ? 0 : 1
  const linhasBadge = temBadge && layout === 'stacked' ? 1 : 0
  const alturaNome = ih - linhasTipo * (fsTipo + 2) - linhasBadge * (fsBadge + 2) - 4

  const fsNome = clamp(
    Math.floor(
      Math.min(
        iw / Math.max(nomeStr.length * 0.52, 2.5),
        Math.max(alturaNome * 0.85, 8),
        13
      )
    ),
    8,
    13
  )

  let fsNomeFinal = fsNome
  if (layout === 'faixa-v') {
    fsNomeFinal = clamp(Math.round(short * 0.22 + 6), 9, 14)
  } else if (layout === 'faixa-h') {
    fsNomeFinal = clamp(Math.round(short * 0.2 + 7), 9, 13)
  }

  const nomeExib =
    layout === 'faixa-v'
      ? truncarTexto(nomeStr, Math.max(ih - 24, 20), fsNomeFinal, 0.48)
      : truncarTexto(nomeStr, iw, fsNomeFinal, 0.52)
  const showTipo = layout !== 'minimal' && layout !== 'faixa-v' && ih >= fsTipo + fsNome + 6
  const metrosExib =
    metros?.largura > 0 && metros?.altura > 0 ? `${metros.largura}×${metros.altura} m` : null

  return {
    layout,
    fsTipo: showTipo || layout === 'faixa-v' || layout === 'faixa-h' ? fsTipo : 0,
    fsNome: fsNomeFinal,
    fsBadge,
    pad,
    nomeExib,
    showTipo: showTipo || layout === 'faixa-v' || layout === 'faixa-h',
    metrosExib,
  }
}

/** @deprecated use rotulosMapaElemento */
export function fontesMapaElemento(largura, altura) {
  const r = rotulosMapaElemento({ largura, altura, nome: 'Area', temBadge: false })
  return { fsTipo: r.fsTipo, fsNome: r.fsNome, fsBadge: r.fsBadge, pad: r.pad }
}

/**
 * Rótulos SVG dentro de um retângulo de área do viveiro.
 * Empilha ou encurta conforme largura/altura disponível.
 */
export function layoutRotulosArea({
  x,
  y,
  largura: w,
  altura: h,
  rotuloTipo,
  nome,
  badge = null,
  metros = null,
}) {
  const { tipo: FS_TIPO, nome: FS_NOME, badge: FS_BADGE } = tamanhosFonteArea(w, h)
  const lines = []
  const iw = Math.max(0, w - PAD * 2)
  const ih = Math.max(0, h - PAD * 2)

  const tipoRaw = rotuloTipo || ''
  const tipoTxt = tipoRaw.toUpperCase()
  const nomeTxt = truncarTexto(nome || '', iw, FS_NOME, 0.5)
  const badgeStr = badge ? String(badge) : null
  const metrosTxt =
    metros?.largura > 0 && metros?.altura > 0 ? `${metros.largura}×${metros.altura} m` : null
  const faixa = orientacaoFaixa(w, h)

  const push = (line) => lines.push(line)

  if (faixa === 'vertical' && ih >= 40) {
    const cx = x + w / 2
    const fsTipoF = clamp(Math.round(Math.min(w, h) * 0.14 + 5), 8, 11)
    const fsNomeF = clamp(Math.round(Math.min(w, h) * 0.18 + 6), 10, 14)
    const fsMetros = clamp(fsTipoF - 1, 7, 10)
    push({
      text: truncarTexto(tipoTxt, iw, fsTipoF, 0.55),
      x: cx,
      y: y + PAD + fsTipoF,
      class: 'lbl-tipo',
      anchor: 'middle',
      fontSize: fsTipoF,
    })
    if (metrosTxt && ih > 80) {
      push({
        text: metrosTxt,
        x: cx,
        y: y + PAD + fsTipoF + fsMetros + 4,
        class: 'lbl-metros',
        anchor: 'middle',
        fontSize: fsMetros,
      })
    }
    push({
      text: truncarTexto(nome || '', Math.max(ih - 40, 24), fsNomeF, 0.45),
      x: cx,
      y: y + h / 2,
      class: 'lbl-nome',
      anchor: 'middle',
      fontSize: fsNomeF,
      transform: `rotate(-90, ${cx}, ${y + h / 2})`,
    })
    if (badgeStr) {
      push({
        text: badgeStr,
        x: cx,
        y: y + h - PAD,
        class: 'lbl-badge',
        anchor: 'middle',
        fontSize: FS_BADGE,
      })
    }
    return { lines, mode: 'faixa-v' }
  }

  if (faixa === 'horizontal' && iw >= 56) {
    const cy = y + h / 2
    const fsNomeF = clamp(Math.round(Math.min(w, h) * 0.2 + 6), 9, 13)
    push({
      text: truncarTexto(tipoTxt, iw * 0.25, FS_TIPO, 0.55),
      x: x + PAD,
      y: cy + FS_TIPO * 0.35,
      class: 'lbl-tipo',
      fontSize: FS_TIPO,
    })
    push({
      text: truncarTexto(nome || '', iw * 0.5, fsNomeF, 0.48),
      x: x + w / 2,
      y: cy + fsNomeF * 0.35,
      class: 'lbl-nome',
      anchor: 'middle',
      fontSize: fsNomeF,
    })
    if (badgeStr) {
      push({
        text: badgeStr,
        x: x + w - PAD,
        y: cy + FS_BADGE * 0.35,
        class: 'lbl-badge',
        anchor: 'end',
        fontSize: FS_BADGE,
      })
    }
    if (metrosTxt) {
      push({
        text: metrosTxt,
        x: x + w / 2,
        y: y + h - PAD,
        class: 'lbl-metros',
        anchor: 'middle',
        fontSize: clamp(FS_TIPO - 1, 7, 10),
      })
    }
    return { lines, mode: 'faixa-h' }
  }

  const linha = (text, ly, cls, opts = {}) => {
    if (!text) return ly
    push({
      text,
      x: opts.x ?? x + PAD,
      y: ly,
      class: cls,
      anchor: opts.anchor ?? 'start',
      fontSize: opts.fontSize,
    })
    return ly + (opts.fontSize ?? (cls === 'lbl-tipo' ? FS_TIPO : cls === 'lbl-badge' ? FS_BADGE : FS_NOME)) + GAP_LINHA
  }

  const fsMin = clamp(Math.round(Math.min(w, h) * 0.14), 9, 14)

  if (iw < 32 || ih < 18) {
    const principal = badgeStr || nomeTxt || truncarTexto(tipoTxt, iw, fsMin, 0.6)
    push({
      text: truncarTexto(principal, iw, fsMin, 0.55),
      x: x + w / 2,
      y: y + h / 2 + fsMin * 0.35,
      class: 'lbl-nome',
      anchor: 'middle',
      fontSize: fsMin,
    })
    return { lines, mode: 'minimal' }
  }

  const tipoW = estimarLarguraTexto(tipoTxt, FS_TIPO, 0.6)
  const badgeW = badgeStr ? estimarLarguraTexto(badgeStr, FS_BADGE, 0.55) : 0
  const cabeMesmaLinha = badgeStr && tipoW + badgeW + 10 <= iw
  const alturaMinEmpilhada = PAD + FS_TIPO + GAP_LINHA + (badgeStr ? FS_BADGE + GAP_LINHA : 0) + FS_NOME + PAD

  let by = y + PAD + FS_TIPO

  if (cabeMesmaLinha && ih >= FS_TIPO + FS_NOME + PAD * 2) {
    push({
      text: truncarTexto(tipoTxt, iw - badgeW - 8, FS_TIPO, 0.6),
      x: x + PAD,
      y: by,
      class: 'lbl-tipo',
      fontSize: FS_TIPO,
    })
    push({
      text: badgeStr,
      x: x + w - PAD,
      y: by,
      class: 'lbl-badge',
      anchor: 'end',
      fontSize: FS_BADGE,
    })
    by += FS_TIPO + 5
    if (by + FS_NOME <= y + h - PAD) {
      linha(nomeTxt, by, 'lbl-nome', { fontSize: FS_NOME })
    }
    return { lines, mode: 'inline' }
  }

  const mostrarTipo = ih >= FS_TIPO + 12 && !(ih < alturaMinEmpilhada && badgeStr)
  if (mostrarTipo) {
    by = linha(truncarTexto(tipoTxt, iw, FS_TIPO, 0.6), by, 'lbl-tipo', { fontSize: FS_TIPO })
  } else {
    by = y + PAD + (badgeStr ? FS_BADGE : FS_NOME)
  }

  if (badgeStr && by + FS_BADGE <= y + h - PAD) {
    by = linha(badgeStr, by, 'lbl-badge', { fontSize: FS_BADGE })
  }

  if (nomeTxt && by + FS_NOME <= y + h - PAD) {
    const fsNome = ih < alturaMinEmpilhada ? Math.min(FS_NOME, fsMin + 2) : FS_NOME
    linha(truncarTexto(nome, iw, fsNome, 0.5), by, 'lbl-nome', { fontSize: fsNome })
  } else if (!badgeStr && !mostrarTipo && nomeTxt) {
    push({
      text: nomeTxt,
      x: x + PAD,
      y: y + h / 2 + FS_NOME * 0.35,
      class: 'lbl-nome',
      fontSize: FS_NOME,
    })
  }

  return { lines, mode: 'stacked' }
}

/** Classes CSS para PlantaBaixa (HTML). */
export function classeLayoutElemento(largura, altura, temBadge = false) {
  if (largura < 36 || altura < 22) return 'elemento--rotulo-minimal'
  if (largura < 72 || (temBadge && largura < 108) || altura < 40) return 'elemento--rotulo-stacked'
  return ''
}
