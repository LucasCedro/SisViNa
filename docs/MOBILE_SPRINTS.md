# SisViNa — Sprints Mobile (Fase 1 e Fase 2)

> Plano completo para PWA operacional + app Capacitor.  
> Módulos mobile: **Home, Coleta, Produção, Fitossanidade, Fertilização**.  
> Web only: NF-e, Financeiro, Contabilidade, Vendas (gestão), etc.

**Como usar:** copie cada bloco `Sprint N` para o seu organizador.  
**Ritmo sugerido:** 1 sprint ≈ 1 semana (ajuste ao seu tempo).  
**Regra:** testar no celular real ao fim de **cada** sprint antes de avançar.

---

## Visão geral

| Fase | Objetivo | Duração estimada |
|------|----------|------------------|
| **Fase 1** | PWA responsiva + banner “Adicionar atalho” | 6–7 semanas |
| **Fase 2** | Capacitor (APK/app) + plugins + offline coleta | 5–6 semanas |

### Ordem de execução

```
Fase 1: Sprint 1 → 2 → 3 → 4 → 5 → 6
Fase 2: Sprint 7 → 8 → 9 → 10 → 11
```

### Decisões fixas

- API atual (JWT + RBAC) — sem reescrever backend.
- Mesmo código Vue; não criar app React Native/Flutter separado.
- iOS **não** permite instalar PWA com 1 clique — banner com passo a passo (Share → Adicionar à Tela de Início).
- Android Chrome: botão “Instalar app” via `beforeinstallprompt`.

---

# FASE 1 — PWA responsiva operacional

---

## Sprint 1 — Fundação mobile (shell + tokens)

**Duração:** ~1 semana  
**Meta:** App navegável no celular antes de refinar telas internas.

### Entregas

- [x] Documentar breakpoints em `sistema-viveiro-nativas/docs/DESIGN_SYSTEM.md`:
  - Mobile: `< 768px`
  - Tablet: `768px – 1024px`
  - Desktop: `> 1024px`
- [x] Criar `MobileNav.vue` — bottom bar fixa com: Home, Coleta, Produção, Fitossanidade, Fertilização.
- [x] Filtrar itens do bottom nav com `can(permission)` (mesma lógica do `Sidebar.vue` / `NAV_ITEMS` via `useNavItems.js`).
- [x] Em `< 768px`: esconder sidebar lateral; conteúdo principal com `padding-bottom` para não ficar atrás da bottom bar.
- [x] Touch targets mínimos 44×44px em botões e links globais (`main.css`).
- [x] `index.html`: `viewport` correto + `theme-color` `#596247` (verde Brotare).
- [x] Composable `useViewport.js` (`isMobile`, `isTablet`) + `initViewport()` em `main.js`.
- [x] Registrar `MobileNav` em `App.vue`.

### Critérios de aceite

- [x] iPhone/Android ~375px: navega entre as 5 rotas sem scroll horizontal na shell.
- [x] Usuário `demo.campo` vê só módulos permitidos no bottom nav (Home, Coleta, Produção, Fitoss., Fertil. — sem Financeiro/Vendas).
- [x] Desktop permanece igual ao atual (sidebar 230px).
- [x] `.\scripts\smoke.ps1` continua passando.

### Arquivos principais

- `src/App.vue`
- `src/components/layout/Sidebar.vue`
- `src/components/layout/MobileNav.vue` (novo)
- `src/composables/useViewport.js` (novo)
- `src/assets/main.css`
- `index.html`

---

## Sprint 2 — Home + Login mobile

**Duração:** ~3–5 dias  
**Meta:** Primeira impressão boa; login confortável no campo.

### Entregas

- [ ] `LoginView.vue`: inputs grandes, botão full-width, layout uma coluna.
- [ ] Evitar zoom indesejado no iOS (`font-size` inputs ≥ 16px).
- [ ] `HomeView.vue`: grid 1 coluna no mobile; cards empilhados.
- [ ] Ações rápidas da home: no máximo 2 colunas no mobile.
- [ ] KPIs legíveis sem pinch-zoom; textos longos com truncamento.
- [ ] Header mobile: título curto; nome do usuário só ícone (refinar se necessário).

### Critérios de aceite

- [ ] Login + home OK em 390×844 (iPhone) sem pinch-zoom.
- [ ] Smoke API inalterado.

### Arquivos principais

- `src/views/LoginView.vue`
- `src/views/HomeView.vue`
- `src/components/layout/Header.vue`

---

## Sprint 3 — Coleta mobile (prioridade campo)

**Duração:** ~1 semana  
**Meta:** Cadastrar coleta e consultar matrizes no viveiro/campo.

### Entregas

- [ ] `ColetaView.vue`: abas com scroll horizontal OU `<select>` de aba no mobile.
- [ ] `MapaColeta.vue`: altura mínima ~50vh no mobile; controles de mapa acessíveis.
- [ ] Botão “Minha localização” visível e grande (`MapaSeletorCoordenadas` já usa geolocation).
- [ ] Tabelas → **cards** em `< 768px`:
  - `TabelaHistoricoColetas.vue`
  - `TabelaLotesColeta.vue`
- [ ] Modais coleta: variante full-screen no mobile (`modal-shell.css` → `app-modal-panel--mobile`).
- [ ] Formulários coleta: uma coluna; `inputmode` adequado (número, data).
- [ ] Toolbar coleta empilhada (completar media queries existentes).

### Critérios de aceite

- [ ] Fluxo completo no celular: listar → abrir form → salvar → ver na lista.
- [ ] Mapa com pan/zoom ok ao toque.
- [ ] Listagem principal sem scroll horizontal obrigatório.

### Arquivos principais

- `src/views/coleta/ColetaView.vue`
- `src/components/coleta/MapaColeta.vue`
- `src/components/coleta/TabelaHistoricoColetas.vue`
- `src/components/coleta/TabelaLotesColeta.vue`
- `src/components/coleta/Form*.vue`
- `src/assets/modal-shell.css`

---

## Sprint 4 — Produção mobile

**Duração:** ~1–1,5 semanas  
**Meta:** Operações de lote usáveis sem desktop (ex.: transferir 400 mudas).

### Entregas

- [ ] `ProducaoView.vue`: guias com scroll horizontal + indicador de aba ativa.
- [ ] Validar `ProducaoFluxoBar.vue` em coluna no mobile (pipeline).
- [ ] `ProducaoPainelLote.vue` + tabelas: cards ou tabela compacta (espécie / qtd / checkbox).
- [ ] Trocar `v-show` → `v-if` nas abas de produção (performance — ver `docs/PERFORMANCE.md`).
- [ ] Botão principal de ação na thumb zone (rodapé fixo da aba quando fizer sentido).
- [ ] Validar overlay `AppLoadingOverlay` com teclado virtual aberto.

### Critérios de aceite

- [ ] Transferência em lote usável no celular.
- [ ] Troca de aba sem travar 3s+.
- [ ] Sem overflow horizontal nas telas principais de produção.

### Arquivos principais

- `src/views/viveiro/ProducaoView.vue`
- `src/components/producao/ProducaoFluxoBar.vue`
- `src/components/producao/ProducaoPainelLote.vue`
- `src/components/producao/Producao*Panel.vue`
- `src/components/producao/producao-panel-shared.css`

---

## Sprint 5 — Fitossanidade + Fertilização mobile

**Duração:** ~1 semana  
**Meta:** Registrar pragas e fertilização no viveiro pelo celular.

### Entregas

- [ ] `Fitossanidade.vue`: gráficos com altura fixa no mobile; `maintainAspectRatio`.
- [ ] Filtros em accordion/colapsável no mobile.
- [ ] Tabelas de plantas/pragas → cards em `< 768px`.
- [ ] `Fertilizacao.vue`: formulário 1 coluna; histórico em cards.
- [ ] Padronizar `.module-header` empilhado no mobile (`module-panels.css`).

### Critérios de aceite

- [ ] Registrar 1 ocorrência de fitossanidade no celular.
- [ ] Registrar 1 aplicação de fertilização no celular.
- [ ] Gráficos não estouram a largura da tela.

### Arquivos principais

- `src/components/viveiro/Fitossanidade.vue`
- `src/components/viveiro/Fertilizacao.vue`
- `src/assets/module-panels.css`

---

## Sprint 6 — PWA + banner “Adicionar atalho” + polish Fase 1

**Duração:** ~1 semana  
**Meta:** Parecer app instalado; sugerir atalho na 1ª visita mobile.

### Entregas — PWA técnico

- [ ] `public/manifest.webmanifest`:
  - `name` / `short_name`: Brotare (ou SisViNa)
  - `display: standalone`
  - `start_url: /`
  - `theme_color` / `background_color`
- [ ] Ícones PWA: `public/icons/` (192×192, 512×512).
- [ ] Service worker mínimo (`vite-plugin-pwa` ou equivalente):
  - Cache do shell (HTML, JS, CSS).
  - Página fallback offline: “Sem conexão — reconecte para sincronizar”.
  - **Sem** sync de dados operacional nesta sprint.
- [ ] Registrar SW só em build de produção.

### Entregas — Banner instalação

- [ ] `composables/usePwaInstall.js`
- [ ] `components/shared/PwaInstallPrompt.vue`
- [ ] Exibir **somente quando**:
  - viewport mobile (`useViewport`);
  - **não** está em `display-mode: standalone`;
  - `localStorage` não tem `pwa_prompt=dismissed` nem `pwa_installed=1`.
- [ ] **Android (Chrome):** capturar `beforeinstallprompt`; botão “Instalar app” chama `deferredPrompt.prompt()`.
- [ ] **iOS (Safari):** modal com passos ilustrados:
  1. Toque em **Compartilhar** (↑)
  2. **Adicionar à Tela de Início**
  3. Confirmar
- [ ] Botões: “Entendi” / “Não mostrar de novo”.
- [ ] Snackbar opcional nas visitas 2–3 se dispensou: “Ver como fixar o atalho”.
- [ ] Não exibir banner no desktop nem dentro do app Capacitor (Fase 2).

### Entregas — Polish final

- [ ] Revisar modais e `ConfirmSaidaModal` no mobile.
- [ ] Criar `docs/MOBILE.md` (como testar no celular na mesma rede, limitações iOS/Android).
- [ ] Atualizar `RODAR.md` com link para mobile.
- [ ] Teste manual: celular na Wi‑Fi → `http://IP_DO_PC:5173`.

### Critérios de aceite

- [ ] Android: 1 toque no banner instala o atalho (quando elegível).
- [ ] iOS: banner educativo claro na 1ª visita.
- [ ] App aberto pelo atalho: sem barra do browser; bottom nav OK.
- [ ] Banner não reaparece após “Não mostrar de novo”.
- [ ] Smoke API continua passando.

### Arquivos principais

- `public/manifest.webmanifest`
- `public/icons/*`
- `vite.config.js` (plugin PWA)
- `src/composables/usePwaInstall.js`
- `src/components/shared/PwaInstallPrompt.vue`
- `docs/MOBILE.md`

---

# FASE 2 — Capacitor (app nativa leve)

---

## Sprint 7 — Capacitor bootstrap

**Duração:** ~1 semana  
**Meta:** Mesmo Vue vira projeto instalável (APK) sem depender só de PWA.

### Entregas

- [ ] Instalar `@capacitor/core`, `@capacitor/cli`, plataforma `@capacitor/android`.
- [ ] (`@capacitor/ios` se tiver Mac para build iOS.)
- [ ] `capacitor.config.ts`: `webDir: 'dist'`, `appId`, `appName`.
- [ ] Script `npm run build:mobile`: `vite build` + `npx cap sync`.
- [ ] Abrir projeto no Android Studio; rodar no emulador ou device.
- [ ] `VITE_API_URL` em dev apontando para IP da máquina (`http://192.168.x.x:8000`).
- [ ] CORS em `api_viveiro`: origens Capacitor (`capacitor://localhost`, etc.).
- [ ] Documentar em `docs/MOBILE.md`.

### Critérios de aceite

- [ ] APK debug instala e faz login.
- [ ] As 5 telas operacionais abrem no app Capacitor.

### Arquivos principais

- `sistema-viveiro-nativas/capacitor.config.ts`
- `sistema-viveiro-nativas/package.json`
- `android/` (gerado pelo Capacitor)
- `api_viveiro/.env` / `compose/api.yml` (CORS)
- `docs/MOBILE.md`

---

## Sprint 8 — Plugins nativos essenciais

**Duração:** ~1 semana  
**Meta:** Experiência nativa onde o browser é fraco.

### Entregas

- [ ] `@capacitor/splash-screen` — splash com logo Brotare.
- [ ] `@capacitor/status-bar` — cor alinhada à marca.
- [ ] `@capacitor/geolocation` — coleta usa plugin quando `Capacitor.isNativePlatform()`; fallback web no browser.
- [ ] `@capacitor/app` — botão voltar Android integrado ao `vue-router`; duplo back para sair.
- [ ] `@capacitor/keyboard` — ajuste de layout quando teclado abre.
- [ ] Esconder `PwaInstallPrompt` quando app nativo.
- [ ] Ícones e splash assets em resoluções Android (mipmap).

### Critérios de aceite

- [ ] GPS na coleta estável no Android nativo.
- [ ] Splash + status bar corretos.
- [ ] Botão voltar não fecha o app na primeira tela interna.

### Arquivos principais

- `src/composables/useGeolocation.js` (novo ou adaptar mapa coleta)
- `src/components/shared/PwaInstallPrompt.vue`
- `android/app/src/main/res/*`
- `capacitor.config.ts`

---

## Sprint 9 — Build release + distribuição interna

**Duração:** ~1 semana  
**Meta:** Equipe instala APK assinado sem Play Store (ainda).

### Entregas

- [ ] Keystore Android + config release em `build.gradle`.
- [ ] Versionamento: `versionCode` / `versionName` (semver).
- [ ] Documentar: gerar APK/AAB, distribuir por link/arquivo/WhatsApp.
- [ ] (Opcional Mac) TestFlight para iOS.
- [ ] Migrar token de `localStorage` para `@capacitor/preferences` (opcional, recomendado).
- [ ] Checklist smoke pós-build mobile (login + 3 GETs).

### Critérios de aceite

- [ ] APK release assinado instala em 2 celulares de teste.
- [ ] Login + coleta + produção funcionam em build **release** (não só debug).

### Arquivos principais

- `android/app/build.gradle`
- `docs/MOBILE.md`
- `src/store/auth.js` (se migrar Preferences)

---

## Sprint 10 — Offline leve (fila coleta)

**Duração:** ~1–2 semanas  
**Meta:** Não perder cadastro de coleta sem sinal.

### Entregas

- [ ] Fila local de POSTs pendentes (IndexedDB ou `@capacitor/preferences` / SQLite plugin se necessário).
- [ ] Escopo **somente coleta** na v1 offline (produção continua online).
- [ ] UI: badge “N pendências” + botão “Sincronizar agora”.
- [ ] Retry automático quando `navigator.onLine` / evento Capacitor Network.
- [ ] Estados: pendente / sincronizado / erro (com mensagem).
- [ ] Estratégia de conflito: última escrita vence + log simples.

### Critérios de aceite

- [ ] Modo avião: cadastra coleta → ao voltar rede, registro aparece no servidor.
- [ ] Usuário entende o status sem suporte técnico.

### Arquivos principais

- `src/services/offlineQueue.js` (novo)
- `src/store/offlineColeta.js` (novo)
- `src/components/coleta/*` (integração fila)
- `src/views/coleta/ColetaView.vue`

---

## Sprint 11 — QA campo + Play Store (opcional)

**Duração:** ~1 semana  
**Meta:** Pronto para uso real da equipe no viveiro.

### Entregas

- [ ] Roteiro de teste campo (checklist ~30 min no viveiro).
- [ ] Correção de bugs encontrados na Sprint 10.
- [ ] Play Console: listing mínimo, política de privacidade, screenshots phone.
- [ ] Decisão documentada: teste interno vs produção aberta.
- [ ] Treinamento rápido: 1 página “Como instalar o app” para equipe de campo.

### Critérios de aceite

- [ ] 1 dia de uso real com perfil `demo.campo` sem blocker crítico.
- [ ] (Opcional) App na faixa de teste interno da Play Store.

### Arquivos principais

- `docs/MOBILE.md`
- `docs/MOBILE_QA_CAMPO.md` (novo checklist)
- Assets Play Store

---

# Referência rápida

## Módulos por fase

| Módulo | Fase 1 PWA | Fase 2 Capacitor |
|--------|------------|------------------|
| Home | Sprint 2 | — |
| Coleta | Sprint 3 | Offline Sprint 10 |
| Produção | Sprint 4 | — |
| Fitossanidade | Sprint 5 | — |
| Fertilização | Sprint 5 | — |
| Shell / nav | Sprint 1 | Sprint 8 |
| Instalar atalho | Sprint 6 | Sprint 7+ (APK substitui PWA no Android) |

## Testar no celular (dev)

1. PC e celular na mesma Wi‑Fi.
2. Descobrir IP do PC: `ipconfig` → IPv4.
3. Subir stack: `.\scripts\dev.ps1 start-all`
4. No celular: `http://SEU_IP:5173`
5. Smoke na API: `.\scripts\smoke.ps1` (no PC).

## Comando para iniciar cada sprint com o assistente

```
Vamos Sprint N — Fase mobile (docs/MOBILE_SPRINTS.md)
```

---

*Última atualização: junho 2026*
