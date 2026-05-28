<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      class="lightbox-overlay"
      role="dialog"
      aria-modal="true"
      :aria-label="`Foto ${indice + 1} de ${urls.length}`"
      @click.self="fechar"
    >
      <button type="button" class="lightbox-btn lightbox-fechar" aria-label="Fechar" @click="fechar">
        ×
      </button>
      <button
        v-if="urls.length > 1"
        type="button"
        class="lightbox-btn lightbox-nav lightbox-prev"
        aria-label="Foto anterior"
        @click.stop="anterior"
      >
        ‹
      </button>
      <figure class="lightbox-figure" @click.stop>
        <img
          v-if="urlAtual"
          :src="urlFullSize(urlAtual)"
          :alt="alt"
          class="lightbox-img"
          @load="carregando = false"
          @error="onErro"
        />
        <p v-if="carregando" class="lightbox-status">Carregando…</p>
        <p v-else-if="erro" class="lightbox-status">Não foi possível carregar esta foto.</p>
        <figcaption v-if="urls.length > 1" class="lightbox-legenda">
          {{ indice + 1 }} / {{ urls.length }}
        </figcaption>
      </figure>
      <button
        v-if="urls.length > 1"
        type="button"
        class="lightbox-btn lightbox-nav lightbox-next"
        aria-label="Próxima foto"
        @click.stop="proxima"
      >
        ›
      </button>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { urlFullSize } from "@/utils/bibliotecaImagens";

const props = defineProps({
  urls: { type: Array, default: () => [] },
  indiceInicial: { type: Number, default: 0 },
  alt: { type: String, default: "Foto ampliada" },
});

const emit = defineEmits(["close"]);

const aberto = ref(false);
const indice = ref(0);
const carregando = ref(true);
const erro = ref(false);

const urlAtual = computed(() => props.urls[indice.value] || "");

function fechar() {
  aberto.value = false;
  emit("close");
}

function anterior() {
  if (!props.urls.length) return;
  carregando.value = true;
  erro.value = false;
  indice.value = (indice.value - 1 + props.urls.length) % props.urls.length;
}

function proxima() {
  if (!props.urls.length) return;
  carregando.value = true;
  erro.value = false;
  indice.value = (indice.value + 1) % props.urls.length;
}

function onErro() {
  carregando.value = false;
  erro.value = true;
}

function onKeydown(e) {
  if (!aberto.value) return;
  if (e.key === "Escape") fechar();
  if (e.key === "ArrowLeft") anterior();
  if (e.key === "ArrowRight") proxima();
}

function abrir(startIndex = 0) {
  indice.value = Math.max(0, Math.min(startIndex, Math.max(0, props.urls.length - 1)));
  carregando.value = true;
  erro.value = false;
  aberto.value = true;
}

watch(urlAtual, () => {
  if (aberto.value) {
    carregando.value = true;
    erro.value = false;
  }
});

watch(
  () => props.indiceInicial,
  (v) => {
    if (aberto.value) indice.value = v;
  }
);

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));

defineExpose({ abrir, fechar });
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 4rem;
}

.lightbox-figure {
  margin: 0;
  max-width: min(96vw, 1200px);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lightbox-img {
  max-width: 100%;
  max-height: calc(90vh - 2rem);
  object-fit: contain;
  border-radius: var(--radius-md);
  user-select: none;
}

.lightbox-legenda {
  margin-top: 0.75rem;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9rem;
}

.lightbox-status {
  color: rgba(255, 255, 255, 0.9);
  margin: 1rem;
}

.lightbox-btn {
  position: absolute;
  border: none;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  cursor: pointer;
  border-radius: var(--radius-full);
  line-height: 1;
  transition: background 0.15s;
}

.lightbox-btn:hover {
  background: rgba(255, 255, 255, 0.22);
}

.lightbox-fechar {
  top: 1rem;
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.6rem;
}

.lightbox-nav {
  top: 50%;
  transform: translateY(-50%);
  width: 2.75rem;
  height: 2.75rem;
  font-size: 2rem;
}

.lightbox-prev {
  left: 1rem;
}

.lightbox-next {
  right: 1rem;
}
</style>
