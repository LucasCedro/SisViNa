const HOST_IMAGEM_MORTO = /reflora(-cdc)?\.cria\.org\.br/i;
const EXT_IMAGEM = /\.(jpe?g|png|gif|webp|bmp)(\?|#|$)/i;
const PATHS_NAO_IMAGEM = /\/(specimen|record|occurrence)\//i;
/** Paths da migração sem arquivo em public/ — não tentar carregar. */
const LOCAL_TEMPLATE_VAZIO = /^\/assets\/biblioteca\/especies\/(arvores|sementes|folhas)\/\d+\.jpg$/i;

export function urlLocalBibliotecaUtilizavel(url) {
  if (!url || typeof url !== "string") return false;
  const u = url.trim();
  if (LOCAL_TEMPLATE_VAZIO.test(u)) return false;
  if (u.startsWith("/") && EXT_IMAGEM.test(u)) return true;
  return false;
}

/** Página de herbário (ex.: coicatalogue.uc.pt/specimen/…) não é imagem. */
export function urlPareceImagem(url) {
  if (!url || typeof url !== "string") return false;
  const u = url.trim();
  const lower = u.toLowerCase();
  if (HOST_IMAGEM_MORTO.test(lower)) return false;
  if (lower.startsWith("/")) return EXT_IMAGEM.test(lower);
  if (!lower.startsWith("http")) return false;
  if (EXT_IMAGEM.test(lower)) return true;
  if (lower.includes("inaturalist-open-data.s3.amazonaws.com/photos/")) return true;
  if (lower.includes("static.inaturalist.org/photos/")) return true;
  if (PATHS_NAO_IMAGEM.test(lower)) return false;
  return false;
}

/** URLs menores para grade/cards; só transforma iNaturalist. */
export function urlThumbnail(url) {
  if (!url || typeof url !== "string") return url;
  if (!/inaturalist/i.test(url)) return url;
  return url
    .replace(/\/original\.(jpe?g|png|webp)(\?|$)/i, "/medium.$1$2")
    .replace(/\/large\.(jpe?g|png|webp)(\?|$)/i, "/medium.$1$2")
    .replace(/\/square\.(jpe?g|png|webp)(\?|$)/i, "/small.$1$2");
}

export function urlFullSize(url) {
  if (!url || typeof url !== "string") return url;
  return url
    .replace(/\/medium\.(jpe?g|png|webp)(\?|$)/i, "/large.$1$2")
    .replace(/\/small\.(jpe?g|png|webp)(\?|$)/i, "/large.$1$2");
}

export function urlsExternasValidas(especie) {
  return (especie?.imagens_externas || []).filter(
    (u) => typeof u === "string" && urlPareceImagem(u)
  );
}

export function fotosDaEspecie(especie) {
  if (!especie) return [];
  const externas = urlsExternasValidas(especie);
  const locais = [especie.imagem_arvore, especie.imagem_semente, especie.imagem_folha].filter(
    urlLocalBibliotecaUtilizavel
  );
  const vistos = new Set();
  const out = [];
  for (const url of [...externas, ...locais]) {
    if (!urlPareceImagem(url) || vistos.has(url)) continue;
    vistos.add(url);
    out.push(url);
  }
  return out;
}

export function capaDaEspecie(especie) {
  if (!especie) return null;
  if (especie.imagem_capa && urlPareceImagem(especie.imagem_capa)) {
    return especie.imagem_capa;
  }
  const fotos = fotosDaEspecie(especie);
  return fotos.find((u) => urlPareceImagem(u)) || null;
}
