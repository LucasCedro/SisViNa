import { ref, onMounted } from 'vue'

/** Alinhado a DESIGN_SYSTEM.md e tokens em main.css */
export const BREAKPOINTS = {
  mobileMax: 767,
  tabletMin: 768,
  tabletMax: 1024,
  desktopMin: 1025,
}

const MQ_MOBILE = `(max-width: ${BREAKPOINTS.mobileMax}px)`
const MQ_TABLET = `(min-width: ${BREAKPOINTS.tabletMin}px) and (max-width: ${BREAKPOINTS.tabletMax}px)`

function readViewport() {
  if (typeof window === 'undefined') {
    return { mobile: false, tablet: false, desktop: true }
  }
  const mobile = window.matchMedia(MQ_MOBILE).matches
  const tablet = window.matchMedia(MQ_TABLET).matches
  return {
    mobile,
    tablet,
    desktop: !mobile && !tablet,
  }
}

function syncHtmlClasses(mobile, tablet) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.classList.toggle('viewport-mobile', mobile)
  root.classList.toggle('viewport-tablet', tablet)
  root.classList.toggle('viewport-desktop', !mobile && !tablet)
}

const initial = readViewport()
export const isMobile = ref(initial.mobile)
export const isTablet = ref(initial.tablet)
export const isDesktop = ref(initial.desktop)

let listenersReady = false

function applyViewport() {
  const v = readViewport()
  isMobile.value = v.mobile
  isTablet.value = v.tablet
  isDesktop.value = v.desktop
  syncHtmlClasses(v.mobile, v.tablet)
}

/** Chamar cedo (main.js) evita flash da sidebar no mobile. */
export function initViewport() {
  if (typeof window === 'undefined' || listenersReady) return
  listenersReady = true
  applyViewport()
  window.matchMedia(MQ_MOBILE).addEventListener('change', applyViewport)
  window.matchMedia(MQ_TABLET).addEventListener('change', applyViewport)
}

/**
 * Viewport reativo compartilhado — todos os consumidores veem o mesmo estado.
 */
export function useViewport() {
  onMounted(() => {
    initViewport()
    applyViewport()
  })

  return { isMobile, isTablet, isDesktop, BREAKPOINTS }
}
