<template>
  <PageLayout>
    <section class="toolbar card">
      <div class="toolbar-left">
        <input
          v-model="termoBusca"
          type="text"
          class="search-input"
          placeholder="Buscar por nome científico, popular ou família..."
        />
        <p class="status-msg" v-if="carregando">Carregando espécies da biblioteca...</p>
        <p class="status-msg erro" v-else-if="erro">{{ erro }}</p>
      </div>
      <div class="toolbar-right">
        <span class="tag">{{ especiesFiltradas.length }} espécies</span>
      </div>
    </section>

    <section v-if="especiesFiltradas.length" class="especies-grid">
      <article
        v-for="especie in especiesFiltradas"
        :key="especie.id"
        class="card especie-card"
        @click="abrirEspecie(especie)"
      >
        <div class="especie-img">
          <img
            v-if="capaCard(especie)"
            :src="urlThumbnail(capaCard(especie))"
            :alt="`Foto de ${especie.nome_popular || especie.nome_cientifico}`"
            class="especie-img-el"
            loading="lazy"
            decoding="async"
            @error="onCardImgError($event, especie)"
          />
          <div v-else class="placeholder-img" />
        </div>
        <div class="especie-content">
          <h3 class="especie-nome">{{ especie.nome_popular || "Sem nome popular" }}</h3>
          <p class="especie-nome-cientifico">{{ especie.nome_cientifico }}</p>
          <div class="especie-tags">
            <span v-if="especie.familia" class="especie-tag">{{ especie.familia }}</span>
            <span v-if="especie.ficha_tecnica?.substrato_tipo" class="especie-tag">
              Substrato {{ especie.ficha_tecnica.substrato_tipo }}
            </span>
            <span v-if="especie.total_fotos > 0" class="especie-tag especie-tag-fotos">
              {{ especie.total_fotos }} foto{{ especie.total_fotos === 1 ? "" : "s" }}
            </span>
          </div>
          <p class="especie-descricao">
            {{ especie.descricao || especie.resumo_manejo || "Sem descrição cadastrada." }}
          </p>
          <p class="meta" v-if="especie.tempo_germinacao">Germinação: ~{{ especie.tempo_germinacao }} dias</p>
        </div>
      </article>
    </section>

    <div v-else-if="!carregando && !erro" class="vazio">Nenhuma espécie encontrada.</div>

    <div v-if="selecionada" class="modal-overlay" @click.self="fecharModal">
      <div class="modal-card">
        <header class="modal-header">
          <h3>{{ selecionada.nome_popular || selecionada.nome_cientifico }}</h3>
          <button type="button" class="btn-fechar" @click="fecharModal">×</button>
        </header>
        <div class="modal-body">
          <p class="cientifico">{{ selecionada.nome_cientifico }}</p>
          <ul v-if="selecionada.ficha_tecnica" class="ficha-grid">
            <li><span>Coleta</span>{{ formatMesesColeta(selecionada.ficha_tecnica) }}</li>
            <li><span>Germinação</span>{{ formatGerminacao(selecionada) }}</li>
            <li><span>Substrato</span>{{ formatSubstrato(selecionada.ficha_tecnica) }}</li>
            <li><span>Viveiro</span>{{ formatPermanencia(selecionada.ficha_tecnica) }}</li>
            <li><span>Semeadura</span>{{ formatProfundidade(selecionada.ficha_tecnica) }}</li>
            <li><span>Armazenamento</span>{{ selecionada.ficha_tecnica.armazenamento_tipo || "—" }}</li>
          </ul>
          <p class="resumo">{{ selecionada.resumo_manejo || selecionada.descricao || "Sem resumo técnico." }}</p>
          <p v-if="selecionada.familia" class="familia-line"><strong>Família:</strong> {{ selecionada.familia }}</p>

          <section class="fotos-especie">
            <h4 class="fotos-titulo">
              Fotos da espécie
              <span v-if="fotosModalUrls.length" class="fotos-contagem">({{ fotosModalUrls.length }})</span>
            </h4>
            <p v-if="carregandoFotosModal" class="fotos-carregando">Carregando fotos…</p>
            <div v-else-if="fotosVisiveis.length" class="fotos-grid">
              <figure
                v-for="(url, i) in fotosVisiveis"
                :key="`${url}-${i}`"
                class="foto-item"
                @click="abrirZoom(i)"
              >
                <img
                  :src="urlThumbnail(url)"
                  :alt="`Foto ${i + 1}`"
                  class="foto-thumb"
                  loading="lazy"
                  decoding="async"
                  @error="onGaleriaImageError"
                />
                <span class="foto-zoom-hint" aria-hidden="true">Ampliar</span>
              </figure>
            </div>
            <p v-else class="sem-fotos">Nenhuma foto disponível para esta espécie.</p>
            <button
              v-if="temMaisFotos"
              type="button"
              class="btn-mais-fotos"
              @click="carregarMaisFotos"
            >
              Carregar mais fotos ({{ fotosModalUrls.length - fotosVisiveis.length }} restantes)
            </button>
          </section>
        </div>
      </div>
    </div>

    <BibliotecaLightbox
      ref="lightboxRef"
      :urls="fotosModalUrls"
      :alt="`Fotos — ${selecionada?.nome_popular || selecionada?.nome_cientifico || ''}`"
    />
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import PageLayout from "@/components/layout/PageLayout.vue";
import BibliotecaLightbox from "@/components/biblioteca/BibliotecaLightbox.vue";
import { listEspeciesBiblioteca, getImagensExternasEspecie } from "@/services/especies";
import {
  capaDaEspecie,
  urlThumbnail,
  urlPareceImagem,
  fotosDaEspecie,
} from "@/utils/bibliotecaImagens";

const FOTOS_LOTE = 8;

const especies = ref([]);
const selecionada = ref(null);
const termoBusca = ref("");
const carregando = ref(true);
const erro = ref(null);
const fotosModalUrls = ref([]);
const fotosVisiveis = ref([]);
const carregandoFotosModal = ref(false);
const lightboxRef = ref(null);

const especiesFiltradas = computed(() => {
  const q = termoBusca.value.trim().toLowerCase();
  if (!q) return especies.value;
  return especies.value.filter((e) => {
    const c = (e.nome_cientifico || "").toLowerCase();
    const p = (e.nome_popular || "").toLowerCase();
    const f = (e.familia || "").toLowerCase();
    return c.includes(q) || p.includes(q) || f.includes(q);
  });
});

const temMaisFotos = computed(
  () => fotosVisiveis.value.length < fotosModalUrls.value.length
);

const MESES = [
  "",
  "jan",
  "fev",
  "mar",
  "abr",
  "mai",
  "jun",
  "jul",
  "ago",
  "set",
  "out",
  "nov",
  "dez",
];

function formatMesesColeta(ficha) {
  if (!ficha?.mes_coleta_inicio) return "—";
  const a = MESES[ficha.mes_coleta_inicio] || ficha.mes_coleta_inicio;
  const b = ficha.mes_coleta_fim ? MESES[ficha.mes_coleta_fim] || ficha.mes_coleta_fim : a;
  return a === b ? a : `${a} – ${b}`;
}

function formatGerminacao(especie) {
  const f = especie.ficha_tecnica;
  const partes = [];
  if (f?.dias_inicio_germinacao) partes.push(`~${f.dias_inicio_germinacao} dias`);
  else if (especie.tempo_germinacao) partes.push(`~${especie.tempo_germinacao} dias`);
  if (f?.pct_germinacao_tipico != null) partes.push(`${f.pct_germinacao_tipico}%`);
  return partes.length ? partes.join(" · ") : "—";
}

function formatSubstrato(ficha) {
  return ficha?.substrato_tipo ? `Tipo ${ficha.substrato_tipo}` : "—";
}

function formatPermanencia(ficha) {
  if (!ficha?.meses_permanencia_viveiro) return "—";
  const min = ficha.meses_permanencia_viveiro;
  const max = ficha.meses_permanencia_viveiro_max;
  return max && max !== min ? `${min}–${max} meses` : `${min} meses`;
}

function formatProfundidade(ficha) {
  const min = ficha?.profundidade_semeadura_cm_min;
  const max = ficha?.profundidade_semeadura_cm_max;
  if (min == null) return "—";
  return max && max !== min ? `${min}–${max} cm` : `${min} cm`;
}

function filtrarUrlsFotos(urls) {
  return (urls || []).filter((u) => urlPareceImagem(u));
}

function capaCard(especie) {
  return capaDaEspecie(especie);
}

function onCardImgError(event, especie) {
  const img = event.target;
  const tentadas = (img.dataset.tentadas || "").split("|").filter(Boolean);
  if (img.src && !tentadas.includes(img.src)) tentadas.push(img.src);
  const proxima = fotosDaEspecie(especie).find(
    (u) => urlPareceImagem(u) && !tentadas.includes(u)
  );
  if (proxima) {
    img.dataset.tentadas = [...tentadas, proxima].join("|");
    img.src = urlThumbnail(proxima);
    return;
  }
  img.style.display = "none";
}

function aplicarLoteFotos(urls, reset = false) {
  const validas = filtrarUrlsFotos(urls);
  fotosModalUrls.value = validas;
  if (reset) {
    fotosVisiveis.value = validas.slice(0, FOTOS_LOTE);
  }
}

function carregarMaisFotos() {
  const start = fotosVisiveis.value.length;
  fotosVisiveis.value.push(...fotosModalUrls.value.slice(start, start + FOTOS_LOTE));
}

async function carregarFotosModal(especie) {
  carregandoFotosModal.value = true;
  fotosModalUrls.value = [];
  fotosVisiveis.value = [];
  try {
    const { urls } = await getImagensExternasEspecie(especie.id);
    aplicarLoteFotos(urls || [], true);
  } catch (e) {
    console.error(e);
    aplicarLoteFotos([], true);
  } finally {
    carregandoFotosModal.value = false;
  }
}

function abrirEspecie(especie) {
  selecionada.value = especie;
  carregarFotosModal(especie);
}

function fecharModal() {
  selecionada.value = null;
  fotosModalUrls.value = [];
  fotosVisiveis.value = [];
  lightboxRef.value?.fechar();
}

function abrirZoom(indice) {
  const url = fotosVisiveis.value[indice];
  const indiceGlobal = fotosModalUrls.value.indexOf(url);
  lightboxRef.value?.abrir(indiceGlobal >= 0 ? indiceGlobal : indice);
}

onMounted(async () => {
  try {
    especies.value = await listEspeciesBiblioteca({ limit: 1000 });
  } catch (e) {
    erro.value = "Não foi possível carregar espécies. Verifique se a API está no ar.";
    console.error(e);
  } finally {
    carregando.value = false;
  }
});
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}

.toolbar-left {
  flex: 1;
}

.tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  font-weight: 600;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
}

.status-msg {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.status-msg.erro {
  color: var(--color-error);
}

.especies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.especie-card {
  overflow: hidden;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.especie-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.especie-img {
  height: 148px;
  background: var(--color-surface-muted);
}

.especie-img-wrap,
:deep(.especie-img-el) {
  width: 100%;
  height: 148px;
  object-fit: cover;
  display: block;
}

.placeholder-img {
  height: 100%;
  background: linear-gradient(135deg, var(--color-info-bg), var(--color-success-bg));
}

.especie-content {
  padding: var(--spacing-lg);
}

.especie-nome {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.especie-nome-cientifico {
  font-style: italic;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.75rem;
}

.especie-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.especie-tag {
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.especie-tag-fotos {
  background: var(--color-surface-muted);
  color: var(--color-text-secondary);
}

.especie-descricao {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
  margin-top: 0.75rem;
}

.meta {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.5rem;
}

.vazio {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 2rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 2000;
}

.modal-card {
  width: min(980px, 100%);
  max-height: 88vh;
  overflow: auto;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.modal-body {
  padding: 1.2rem;
}

.cientifico {
  margin: 0;
  font-style: italic;
  color: var(--color-text-secondary);
}

.ficha-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem 1rem;
  list-style: none;
  margin: 0.75rem 0;
  padding: 0.75rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.ficha-grid li span {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

.resumo {
  margin: 0.8rem 0;
  white-space: pre-line;
}

.familia-line {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.fotos-especie {
  margin-top: 1rem;
}

.fotos-titulo {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
}

.fotos-contagem {
  font-weight: 500;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

.fotos-carregando {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0 0 1rem;
}

.fotos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.65rem;
}

.foto-item {
  margin: 0;
  position: relative;
  cursor: zoom-in;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.foto-item .foto-thumb {
  display: block;
  width: 100%;
  height: 140px;
  object-fit: cover;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
}

.foto-item:hover .foto-zoom-hint {
  opacity: 1;
}

.foto-zoom-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.35rem;
  font-size: 0.7rem;
  text-align: center;
  color: #fff;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.65));
  opacity: 0;
  transition: opacity 0.15s;
  pointer-events: none;
}

.btn-mais-fotos {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
  color: var(--color-primary);
}

.btn-mais-fotos:hover {
  background: var(--color-primary-subtle);
}

.sem-fotos {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-align: center;
  padding: 1.25rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
}
</style>
