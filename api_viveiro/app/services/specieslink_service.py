"""Integração com a API speciesLink (specieslink.net/ws/1.0)."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Hosts do serviço Exsiccatae/Reflora — DNS morto; não usar no front nem gravar no cache.
_HOSTS_IMAGEM_BLOQUEADOS = (
    "reflora-cdc.cria.org.br",
    "reflora.cria.org.br",
)

_HREF_RE = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.I)
_URL_RE = re.compile(r"https?://[^\s\"'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s\"'<>]*)?", re.I)

CAMPOS_URL_IMAGEM = (
    "image_url",
    "imageurl",
    "associatedmedia",
    "media",
)


def url_imagem_bloqueada(url: str) -> bool:
    lower = (url or "").lower()
    return any(host in lower for host in _HOSTS_IMAGEM_BLOQUEADOS)


_EXT_IMAGEM_RE = re.compile(r"\.(jpe?g|png|gif|webp|bmp)(\?|#|$)", re.I)
_PATHS_NAO_IMAGEM = ("/specimen/", "/record/", "/occurrence/", "/catalogue/")


def url_parece_imagem(url: str) -> bool:
    """Aceita só URLs que provavelmente são arquivo de imagem (não página HTML de herbário)."""
    u = (url or "").strip()
    if not u or url_imagem_bloqueada(u):
        return False
    lower = u.lower()
    if lower.startswith("/"):
        return bool(_EXT_IMAGEM_RE.search(lower))
    if not lower.startswith("http"):
        return False
    if _EXT_IMAGEM_RE.search(lower):
        return True
    if "inaturalist-open-data.s3.amazonaws.com/photos/" in lower:
        return True
    if "static.inaturalist.org/photos/" in lower:
        return True
    if any(p in lower for p in _PATHS_NAO_IMAGEM):
        return False
    return False


def filtrar_urls_imagem(urls: List[str]) -> List[str]:
    """Remove hosts mortos, páginas de catálogo e duplicatas."""
    out: List[str] = []
    for url in urls:
        if not url_parece_imagem(url):
            continue
        if url not in out:
            out.append(url)
    return out


# Grafias incorretas no cadastro que impedem match em APIs externas
_CORRECOES_GENERO: Dict[str, str] = {
    "stryphondendron": "stryphnodendron",
}

_BINOMIO_RE = re.compile(
    r"^([A-Z][A-Za-z\-\.]+)\s+([a-z][a-z\-\.]+)",
    re.UNICODE,
)


def normalizar_nome_cientifico_para_busca(nome_cientifico: str) -> str:
    """Binômio puro (gênero + espécie), sem autores; corrige typos conhecidos."""
    nome = re.sub(r"\s+", " ", (nome_cientifico or "").strip())
    if "(" in nome:
        nome = nome.split("(")[0].strip()
    nome = nome.rstrip(".,;")
    match = _BINOMIO_RE.match(nome)
    if not match:
        partes = nome.split()
        return f"{partes[0]} {partes[1]}" if len(partes) >= 2 else nome

    genero, especie = match.group(1), match.group(2)
    genero_lower = genero.lower()
    if genero_lower in _CORRECOES_GENERO:
        fix = _CORRECOES_GENERO[genero_lower]
        genero = fix[0].upper() + fix[1:] if fix else genero
    return f"{genero} {especie}"


def _api_key() -> Optional[str]:
    key = (settings.SPECIESLINK_API_KEY or "").strip()
    return key or None


def montar_url_busca(
    nome_cientifico: str,
    *,
    limit: Optional[int] = None,
    scope: Optional[str] = None,
) -> str:
    """Monta URL do endpoint /search (parâmetros via query string)."""
    if not _api_key():
        raise ValueError("SPECIESLINK_API_KEY não configurada no servidor.")

    params: Dict[str, str] = {
        "apikey": _api_key(),
        "scientificname": normalizar_nome_cientifico_para_busca(nome_cientifico),
        "images": "yes",
        "limit": str(limit or settings.SPECIESLINK_SEARCH_LIMIT),
        "scope": scope or settings.SPECIESLINK_SCOPE,
    }
    base = settings.SPECIESLINK_API_BASE_URL.rstrip("/")
    return f"{base}/search?{urlencode(params)}"


def _extrair_features(payload: Any) -> List[dict]:
    if not isinstance(payload, dict):
        return []
    features = payload.get("features")
    if isinstance(features, list):
        return [f for f in features if isinstance(f, dict)]
    return []


def _urls_em_texto(texto: str) -> List[str]:
    urls: List[str] = []
    for m in _HREF_RE.finditer(texto):
        urls.append(m.group(1).strip())
    for m in _URL_RE.finditer(texto):
        urls.append(m.group(0).strip())
    return urls


def _urls_de_propriedades(props: dict) -> List[str]:
    urls: List[str] = []
    for chave, valor in props.items():
        if chave.lower() in CAMPOS_URL_IMAGEM and isinstance(valor, str):
            urls.extend(_urls_em_texto(valor))
        elif isinstance(valor, str):
            urls.extend(_urls_em_texto(valor))
    return urls


def _url_exsiccatae(imagecode: str) -> Optional[str]:
    code = (imagecode or "").strip()
    if not code:
        return None
    template = settings.SPECIESLINK_EXSICCATAE_IMAGE_URL_TEMPLATE
    if not template or "{imagecode}" not in template:
        return None
    return template.format(imagecode=code)


async def _validar_url_imagem(url: str, client: httpx.AsyncClient) -> bool:
    if not settings.SPECIESLINK_VALIDAR_URL_IMAGEM:
        return True
    try:
        response = await client.head(url, follow_redirects=True)
        if response.status_code >= 400:
            response = await client.get(url, follow_redirects=True)
        ctype = (response.headers.get("content-type") or "").lower()
        return response.status_code < 400 and (
            "image" in ctype or len(response.content) > 500
        )
    except httpx.HTTPError:
        return False


def extrair_urls_imagem(
    payload: Any,
    *,
    max_imagens: Optional[int] = None,
    urls_validadas: Optional[List[str]] = None,
) -> List[str]:
    """Extrai URLs a partir do GeoJSON da busca /search."""
    limite = max_imagens or settings.SPECIESLINK_MAX_IMAGENS_POR_ESPECIE
    urls: List[str] = []
    vistos: set[str] = set()

    def add(url: Optional[str]) -> None:
        if not url or url in vistos:
            return
        if urls_validadas is not None and url not in urls_validadas:
            return
        vistos.add(url)
        urls.append(url)

    for feature in _extrair_features(payload):
        props = feature.get("properties") or {}
        if not isinstance(props, dict):
            continue
        for url in _urls_de_propriedades(props):
            add(url)
        barcode = props.get("barcode")
        if isinstance(barcode, str):
            add(_url_exsiccatae(barcode))

    return filtrar_urls_imagem(urls[:limite])


async def buscar_imagens_inaturalist(
    nome_cientifico: str,
    *,
    timeout: Optional[float] = None,
    max_imagens: Optional[int] = None,
) -> List[str]:
    """Fotos taxonômicas via API pública do iNaturalist (fallback quando Exsiccatae está fora)."""
    if not settings.INATURALIST_FALLBACK_ENABLED:
        return []

    nome = normalizar_nome_cientifico_para_busca(nome_cientifico)
    if not nome:
        return []

    limite = max_imagens or settings.INATURALIST_MAX_IMAGENS_POR_ESPECIE
    base = settings.INATURALIST_API_BASE_URL.rstrip("/")
    url = f"{base}/taxa?q={quote(nome)}&per_page={limite}&is_active=true"
    timeout_val = timeout if timeout is not None else settings.SPECIESLINK_REQUEST_TIMEOUT

    payload = await _get_json(url, timeout=timeout_val, verify_ssl=True)
    if not isinstance(payload, dict):
        return []

    urls: List[str] = []
    for taxon in payload.get("results") or []:
        if not isinstance(taxon, dict):
            continue
        photo = taxon.get("default_photo")
        if not isinstance(photo, dict):
            continue
        for key in ("medium_url", "large_url", "original_url", "square_url"):
            candidate = photo.get(key)
            if isinstance(candidate, str) and candidate.startswith("http"):
                urls.append(candidate)
                break
        if len(urls) >= limite:
            break

    return filtrar_urls_imagem(urls)[:limite]


async def _get_json(url: str, *, timeout: float, verify_ssl: bool) -> Optional[Any]:
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers={"Accept": "application/json", "User-Agent": "SisViNa/1.0"},
            )
        if response.status_code != 200:
            logger.info("speciesLink HTTP %s — %s", response.status_code, url[:120])
            return None
        return response.json()
    except httpx.TimeoutException:
        logger.warning("speciesLink timeout: %s", url[:120])
    except httpx.HTTPError as exc:
        logger.warning("speciesLink erro HTTP: %s", exc)
    except ValueError as exc:
        logger.warning("speciesLink JSON inválido: %s", exc)
    return None


async def buscar_imagens_por_nome_cientifico(
    nome_cientifico: str,
    *,
    timeout: Optional[float] = None,
    verify_ssl: Optional[bool] = None,
    max_imagens: Optional[int] = None,
) -> List[str]:
    """Alias legado — use imagens_externas_service.buscar_imagens_para_especie."""
    from app.services.imagens_externas_service import buscar_imagens_para_especie

    return await buscar_imagens_para_especie(
        nome_cientifico,
        timeout=timeout,
        verify_ssl=verify_ssl,
        max_imagens=max_imagens,
    )
