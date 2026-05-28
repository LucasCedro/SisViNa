<template>
  <div ref="root" class="lazy-wrap" :class="wrapClass">
    <img
      v-if="visivel && srcAtual"
      :src="srcAtual"
      :alt="alt"
      :class="imgClass"
      decoding="async"
      :fetchpriority="eager ? 'high' : 'low'"
      @error="onError"
    />
    <div v-else class="lazy-ph" :class="imgClass" aria-hidden="true" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";

const props = defineProps({
  src: { type: String, default: "" },
  alt: { type: String, default: "" },
  imgClass: { type: String, default: "" },
  wrapClass: { type: String, default: "" },
  rootMargin: { type: String, default: "200px 0px" },
  eager: { type: Boolean, default: false },
  candidatos: { type: Array, default: () => [] },
});

const root = ref(null);
const visivel = ref(false);
const srcAtual = ref("");
const tentadas = ref([]);

let observer = null;

function proximaCandidata() {
  const lista = [props.src, ...props.candidatos].filter(Boolean);
  return lista.find((u) => !tentadas.value.includes(u));
}

function atribuirSrc() {
  const prox = proximaCandidata();
  if (prox) {
    srcAtual.value = prox;
    if (!tentadas.value.includes(prox)) tentadas.value.push(prox);
  }
}

function onError() {
  const prox = proximaCandidata();
  if (prox) {
    srcAtual.value = prox;
    tentadas.value.push(prox);
    return;
  }
  srcAtual.value = "";
}

watch(
  () => props.src,
  () => {
    tentadas.value = [];
    if (visivel.value) atribuirSrc();
  }
);

onMounted(() => {
  if (props.eager) {
    visivel.value = true;
    atribuirSrc();
    return;
  }
  if (!root.value) return;
  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        visivel.value = true;
        atribuirSrc();
        observer?.disconnect();
        observer = null;
      }
    },
    { rootMargin: props.rootMargin }
  );
  observer.observe(root.value);
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>

<style scoped>
.lazy-wrap {
  width: 100%;
  height: 100%;
}

.lazy-ph {
  width: 100%;
  height: 100%;
  min-height: 80px;
  background: var(--color-surface-muted);
}
</style>
