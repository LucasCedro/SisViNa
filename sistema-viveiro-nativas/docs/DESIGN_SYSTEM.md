# Brotare Viveiros — Design System

> Paleta e tokens visuais oficiais. Versão 0.2 · 2026

---

## Princípios de UI/UX aplicados

### Regra 60-30-10

| Proporção | Papel | Tokens |
|-----------|-------|--------|
| **60%** | Fundo dominante, áreas de respiro | `--color-background`, `--color-surface`, `--color-border-subtle` |
| **30%** | Estrutura, navegação, hierarquia | Escala Primary (`#596247` e tons), sidebar, cards, bordas |
| **10%** | Acento e feedback | `--color-attention`, semânticas (sucesso/erro/info) em CTAs, badges e alertas |

### Outras práticas

- **Contraste**: texto principal `#2C2D2A` sobre fundo `#F5F4F2` — WCAG AA. Neutro médio `#8E9089` apenas para placeholders, ícones secundários e bordas — **nunca** como texto de corpo.
- **Cohesão cromática**: verdes oliva + terrosos; sem azuis genéricos de UI kit.
- **Hierarquia tipográfica**: títulos em `--color-text-primary`, metadados em `--color-text-secondary`, hints em `--color-text-muted`.
- **Feedback semântico**: sucesso/erro/info/atencao sempre com par fundo + texto (`--color-*-bg` + `--color-*`).
- **Consistência**: componentes consomem **CSS variables** de `src/assets/main.css` — evitar hex solto nos `.vue`.

### Mobile e breakpoints

Layout responsivo e app operacional em campo (PWA / Capacitor). Ver também `docs/MOBILE_SPRINTS.md`.

| Faixa | Largura | Token CSS | Uso |
|-------|---------|-----------|-----|
| **Mobile** | `< 768px` | `--breakpoint-mobile-max: 767px` | Bottom nav (`MobileNav`), sidebar oculta, touch 44px |
| **Tablet** | `768px – 1024px` | `--breakpoint-tablet-max: 1024px` | Sidebar compacta opcional; grids 2 colunas |
| **Desktop** | `> 1024px` | — | Layout atual (sidebar 230px) |

**Media queries oficiais** (usar estes valores em todo o projeto):

```css
/* Mobile */
@media (max-width: 767px) { … }

/* Tablet */
@media (min-width: 768px) and (max-width: 1024px) { … }

/* Desktop */
@media (min-width: 1025px) { … }
```

**JavaScript:** `composables/useViewport.js` — `isMobile`, `isTablet`, `isDesktop` via `matchMedia`, sincroniza classes `viewport-mobile` / `viewport-tablet` no `<html>`.

**Navegação mobile (operacional):** bottom bar com Home, Coleta, Produção, Fitossanidade, Fertilização — mesmas permissões RBAC e pipeline da unidade (`viveiroContext`).

No modo **florestal**, itens nativos (Coleta, Produção nativa) ficam ocultos via `modulos_nav_desabilitados`.

### Crítica construtiva à paleta

| Ponto | Avaliação | Recomendação |
|-------|-----------|--------------|
| Primary `#596247` | Excelente para viveiro/nativas — sóbrio, orgânico | Usar como marca e CTAs primários |
| Sucesso `#3E6247` = Análogo 1 | Coeso, mas **muito próximo** do primary | Diferenciar em badges com `--color-success-bg` |
| Atenção `#C8A84B` | Dourado natural, ótimo acento 10% | Reservar para highlights, active nav, warnings |
| Complementar `#624E47` | Terroso elegante | Sidebar ou elementos de profundidade |
| Neutro médio `#8E9089` | Risco de contraste baixo em texto | Apenas decorativo / disabled |
| Info `#47607B` | Azul-acinzentado harmoniza sem quebrar paleta | Substituir blues genéricos (#2196F3) |

---

## Paleta completa

### Primary — escala de tom

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-primary-50` | `#EEF0EA` | Fundos sutis, hover leve |
| `--color-primary-100` | `#CBD3C3` | Bordas suaves, divisores |
| `--color-primary-200` | `#A4B39A` | Ícones secundários, gráficos |
| `--color-primary-500` | `#596247` | **Primary base** — botões, links, marca |
| `--color-primary-600` | `#47503A` | Hover primary, texto secundário |
| `--color-primary-700` | `#353D2B` | Texto em fundos claros alternativo |
| `--color-primary-900` | `#222A1C` | Sidebar, superfícies escuras |

Atalhos: `--color-primary` = 500 · `--color-primary-dark` = 600 · `--color-primary-light` = 100 · `--color-primary-subtle` = 50

### Paleta harmônica

| Nome | Token | Hex | Uso sugerido |
|------|-------|-----|--------------|
| Complementar escuro | `--color-complement-dark` | `#624E47` | Acentos terrosos, gráficos |
| Complementar claro | `--color-complement-light` | `#F0EAE9` | Fundos quentes alternativos |
| Análogo 1 | `--color-analog-1` | `#3E6247` | Sucesso, vegetação |
| Análogo 2 | `--color-analog-2` | `#625947` | Variação em charts |

### Neutros

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-background` | `#F5F4F2` | Fundo geral da app (60%) |
| `--color-surface` | `#FFFFFF` | Cards, modais, header |
| `--color-surface-muted` | `#EEF0EA` | Zebrado, inputs disabled |
| `--color-border` | `#CBD3C3` | Bordas padrão |
| `--color-border-subtle` | `#EEF0EA` | Divisores internos |
| `--color-neutral-medium` | `#8E9089` | Placeholder, ícones inativos |
| `--color-text-primary` | `#2C2D2A` | Títulos e corpo |
| `--color-text-secondary` | `#47503A` | Subtítulos, labels |
| `--color-text-muted` | `#8E9089` | Hints, timestamps |
| `--color-text-inverse` | `#FFFFFF` | Texto sobre primary/sidebar |

### Semânticas

| Token | Hex | Par de fundo |
|-------|-----|--------------|
| `--color-attention` | `#C8A84B` | `--color-attention-bg` `#FBF6E8` |
| `--color-success` | `#3E6247` | `--color-success-bg` `#EEF0EA` |
| `--color-error` | `#8E3B2B` | `--color-error-bg` `#F5EDEB` |
| `--color-info` | `#47607B` | `--color-info-bg` `#EDF1F5` |

Hover semânticos: `--color-info-dark` `#3A5066` · `--color-error-dark` `#723023`

### Sidebar

| Token | Valor |
|-------|-------|
| `--color-sidebar-bg` | `#222A1C` (primary-900) |
| `--color-sidebar-active-accent` | `#C8A84B` (atenção — regra 10%) |

### Gráficos (Chart.js / SVG)

Paleta categórica base — `src/constants/chartColors.js`:

```js
['#596247', '#3E6247', '#625947', '#624E47', '#47607B',
 '#A4B39A', '#C8A84B', '#47503A', '#8E9089', '#353D2B']
```

Presets por módulo (mesmos hex que `main.css`):

| Export | Uso |
|--------|-----|
| `CHART_DFC` | Barras evolução caixa (entrada / saída / saldo) |
| `CHART_DRE` | Faturamento × CMV |
| `CHART_ESTOQUE_ETAPA` | Timeline Compras e Estoques |

---

## Mapa do viveiro (planta baixa)

O editor (`ViveiroDesigner`, `ViveiroLayoutEditor`, `PlantaBaixa`) segue a **mesma sistemática** do restante da app — sem exceção.

### Duas camadas

| Camada | Onde | Como |
|--------|------|------|
| **Chrome UI** | header, toolbar, painéis, erros | `var(--color-*)` de `main.css` + classes `.viveiro-toolbar` em `viveiro-map-shell.css` |
| **SVG / atributos dinâmicos** | `fill`, `stroke`, `setAttribute`, legenda | Hex de `src/constants/viveiroMapColors.js` |

Atributos SVG **não resolvem** CSS variables — por isso o hex fica centralizado em JS, espelhado em CSS:

```css
/* viveiro-map-shell.css — manter sincronizado com viveiroMapColors.js */
--viveiro-tipo-canteiro: #596247;
--viveiro-tipo-sementeira: #C8A84B;
/* … */
```

### Fontes por tipo de área

| Tipo | Token design | Hex mapa |
|------|--------------|----------|
| Canteiro | `--color-primary` | `#596247` |
| Sementeira | `--color-attention` | `#C8A84B` |
| Rustificação / trabalho | `--color-primary-200` | `#A4B39A` |
| Sede / água | `--color-info` / `--color-info-dark` | `#47607B` / `#3A5066` |
| Garagem / estoque | `--color-neutral-medium` | `#8E9089` |

`viveiroComponentes.js` (`corPadrao`) e `viveiroLayout.js` importam `corPadraoTipo()` — **não** duplicar hex nesses arquivos.

Paletas do seletor de cor no editor: `VIVEIRO_PALETTES` (5 tons harmônicos por categoria).

---

## Tipografia

- **Família**: Inter (Google Fonts) com fallback system-ui
- **Base**: 16px / line-height 1.5
- **Títulos de página**: 1.5–1.75rem, weight 600–700
- **Seções**: 1.25rem, weight 600

---

## Espaçamento, raios e sombras

Definidos em `:root` em `main.css`:

- Spacing: `--spacing-xs` … `--spacing-2xl`
- Radius: `--radius-sm` … `--radius-full`
- Shadow: `--shadow-sm`, `--shadow`, `--shadow-md`, `--shadow-lg`

---

## Componentes globais

Classes utilitárias em `main.css` (não scoped):

| Classe | Uso |
|--------|-----|
| `.card`, `.card-title` | Containers padrão |
| `.btn`, `.btn-primary`, `.btn-outline`, `.btn-secondary`, `.btn-danger` | Botões |
| `.alert`, `.alert-error`, `.alert-success`, `.alert-warning`, `.alert-info` | Mensagens |
| `.badge`, `.badge-success`, `.badge-error`, `.badge-warning`, `.badge-info` | Status |
| `.form-input`, `.form-label` | Formulários |
| `.content-wrapper`, `.secao`, `.secao-header`, `.secao-titulo` | Layout de páginas |
| `.guia`, `.guia.ativa` | Abas / tabs |

---

## Implementação

1. **Fonte da verdade (UI)**: `src/assets/main.css` — todas as CSS variables
2. **Gráficos / SVG dinâmico**: `src/constants/chartColors.js` e `src/constants/viveiroMapColors.js` — hex literal espelhando os tokens
3. **Shell do mapa**: `src/assets/viveiro-map-shell.css` — toolbar, fundo do canvas, `--viveiro-*` para fills em scoped CSS
4. **Tailwind**: `tailwind.config.js` espelha tokens para stubs legados
5. **Painéis de módulo**: `src/assets/module-panels.css` — banners e utilitários `.sem-fill-*` / `.sem-border-*`

---

## Checklist para novos componentes

- [ ] Usar `var(--color-*)` em vez de hex no CSS do componente
- [ ] Botão primário: `--color-primary` + hover `--color-primary-dark`
- [ ] Erro/sucesso: par bg + texto semântico
- [ ] Respeitar 60-30-10 — no máximo 1 acento forte por viewport
- [ ] Testar contraste de texto muted em fundo branco
- [ ] **Mapa viveiro**: chrome com tokens; cores de área via `viveiroMapColors.js` + `--viveiro-tipo-*` no CSS scoped
- [ ] **Chart.js / canvas**: importar de `chartColors.js`, não inventar hex
- [ ] **Mobile**: testar em `< 768px`; alvos de toque ≥ 44px; evitar scroll horizontal na shell
