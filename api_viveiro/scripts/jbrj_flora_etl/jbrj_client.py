"""Cliente HTTP para Flora e Funga do Brasil — servicos.jbrj.gov.br/v2/flora."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from fenologia import extract_fenologia
from normalizacao import api_search_variants, normalize_key, sanitize_input_name, url_encode_taxon

FLORA_TAXON_URL = "https://servicos.jbrj.gov.br/v2/flora/taxon/{nome}"
REQUEST_TIMEOUT = 45
USER_AGENT = "SisViNa-ETL/1.0 (+https://github.com/sisvina; contato dev local)"


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, requests.HTTPError):
        return exc.response is not None and exc.response.status_code in (429, 502, 503, 504)
    return isinstance(exc, (requests.ConnectionError, requests.Timeout))


class JbrjFloraClient:
    def __init__(self, delay_ok: float = 2.0) -> None:
        self.delay_ok = delay_ok
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "User-Agent": USER_AGENT})

    @retry(
        retry=retry_if_exception(_retryable),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True,
    )
    def _get_json(self, url: str) -> Any:
        resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code in (429, 502, 503, 504):
            resp.raise_for_status()
        resp.raise_for_status()
        return resp.json()

    def fetch_taxon(self, nome_cientifico: str) -> List[Dict[str, Any]]:
        limpo = sanitize_input_name(nome_cientifico)
        if not limpo:
            raise ValueError("Nome científico vazio após sanitização")

        tentativas = api_search_variants(limpo)
        visto: set[str] = set()
        ultimo_erro: Exception | None = None

        for candidato in tentativas:
            if candidato in visto:
                continue
            visto.add(candidato)
            url = FLORA_TAXON_URL.format(nome=url_encode_taxon(candidato))
            try:
                data = self._get_json(url)
                if isinstance(data, list) and data:
                    return data
            except requests.HTTPError as exc:
                ultimo_erro = exc
                if exc.response is not None and exc.response.status_code == 404:
                    continue
                raise

        if ultimo_erro:
            raise ultimo_erro
        raise ValueError(f"Nenhum registro retornado para {nome_cientifico!r}")

    def transform_record(self, records: List[Dict[str, Any]], input_name: str) -> Dict[str, Any]:
        """Normaliza resposta JBRJ → payload para species_master."""
        if not records:
            raise ValueError(f"Nenhum registro retornado para {input_name!r}")

        # Preferir nome aceito (NOME_ACEITO)
        rec = records[0]
        for candidate in records:
            taxon = candidate.get("taxon") or {}
            if taxon.get("taxonomicstatus") == "NOME_ACEITO":
                rec = candidate
                break

        taxon = rec.get("taxon") or {}
        distrib = rec.get("distribuition") or rec.get("distribution") or []
        profile = rec.get("specie_profile") or {}
        vernacular = rec.get("vernacular_name") or []

        estados: List[str] = []
        biomas: List[str] = []
        endemismo: Optional[str] = None

        for row in distrib:
            loc = row.get("locationid") or ""
            if loc.startswith("BR-"):
                uf = loc.split("-", 1)[1]
                if uf and uf not in estados:
                    estados.append(uf)
            remarks = row.get("occurrenceremarks") or {}
            if isinstance(remarks, dict):
                if not endemismo and remarks.get("endemism"):
                    endemismo = str(remarks.get("endemism"))
                domains = remarks.get("phytogeographicDomain") or []
                if isinstance(domains, list):
                    for b in domains:
                        b = str(b).strip()
                        if b and b not in biomas:
                            biomas.append(b)

        nomes_pop: List[str] = []
        for v in vernacular:
            if isinstance(v, dict):
                nome = v.get("vernacularname") or v.get("name")
                lang = (v.get("language") or v.get("languagecode") or "pt").lower()
                if nome and lang.startswith("pt") and nome not in nomes_pop:
                    nomes_pop.append(str(nome).strip())
            elif isinstance(v, str) and v.strip():
                nomes_pop.append(v.strip())

        life_form = [str(x) for x in (profile.get("lifeForm") or []) if x]
        habitat = [str(x) for x in (profile.get("habitat") or []) if x]
        vegetation = [str(x) for x in (profile.get("vegetationType") or []) if x]

        notes_parts: List[str] = []
        if endemismo:
            notes_parts.append(f"Endemismo: {endemismo}")
        if vegetation:
            notes_parts.append(f"Vegetação: {', '.join(vegetation)}")
        # Campo notes explícito (DwC simplificado / futuras extensões da API)
        if rec.get("notes"):
            notes_parts.append(str(rec["notes"]))
        notes_text = ". ".join(notes_parts) if notes_parts else None

        meses_flor, meses_frut = extract_fenologia(notes_text)

        status = rec.get("threatStatus") or rec.get("threat_status")
        if not status and isinstance(rec.get("conservation"), dict):
            status = rec["conservation"].get("status")

        scientific = (
            taxon.get("scientificname")
            or f"{taxon.get('genus', '')} {taxon.get('specificepithet', '')}".strip()
            or input_name
        )

        return {
            "taxon_id_jbrj": taxon.get("taxonid"),
            "nome_cientifico": scientific,
            "nome_cientifico_chave": normalize_key(scientific or input_name),
            "familia": taxon.get("family"),
            "nomes_populares": nomes_pop,
            "biomas": sorted(biomas),
            "estados_ocorrencia": sorted(estados),
            "status_ameaca": status,
            "meses_floracao": meses_flor,
            "meses_frutificacao": meses_frut,
            "forma_vida": life_form,
            "habitat": habitat,
            "notas_origem": notes_text,
        }

    def fetch_and_transform(self, nome_cientifico: str) -> Dict[str, Any]:
        limpo = sanitize_input_name(nome_cientifico)
        records = self.fetch_taxon(limpo)
        payload = self.transform_record(records, limpo)
        time.sleep(self.delay_ok)
        return payload
