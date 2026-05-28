from app.services.specieslink_service import (
    extrair_urls_imagem,
    filtrar_urls_imagem,
    montar_url_busca,
    normalizar_nome_cientifico_para_busca,
    url_imagem_bloqueada,
    url_parece_imagem,
)
from app.config import settings


def test_normalizar_nome_remove_autoria():
    assert (
        normalizar_nome_cientifico_para_busca(
            "Acrocomia aculeata (Jacq.) Lodd. ex Mart."
        )
        == "Acrocomia aculeata"
    )


def test_normalizar_corrige_genero_stryphnodendron():
    assert (
        normalizar_nome_cientifico_para_busca(
            "Stryphondendron adstringens (Mart.) Coville"
        )
        == "Stryphnodendron adstringens"
    )


def test_montar_url_search(monkeypatch):
    monkeypatch.setattr(settings, "SPECIESLINK_API_KEY", "chave-teste")
    url = montar_url_busca("Dipteryx alata")
    assert "specieslink.net/ws/1.0/search" in url
    assert "apikey=chave-teste" in url
    assert "scientificname=Dipteryx+alata" in url
    assert "images=yes" in url


def test_url_imagem_bloqueada_reflora():
    assert url_imagem_bloqueada(
        "https://reflora-cdc.cria.org.br/inct/exsiccatae/image/imagecode/X/size/large/"
    )
    assert not url_imagem_bloqueada("https://inaturalist-open-data.s3.amazonaws.com/x.jpg")


def test_url_parece_imagem_rejeita_pagina_herbario():
    assert not url_parece_imagem("https://coicatalogue.uc.pt/specimen/COI00081737")
    assert url_parece_imagem(
        "https://inaturalist-open-data.s3.amazonaws.com/photos/1/medium.jpg"
    )


def test_filtrar_urls_remove_reflora():
    urls = filtrar_urls_imagem(
        [
            "https://reflora.cria.org.br/x.jpg",
            "https://inaturalist-open-data.s3.amazonaws.com/ok.jpg",
        ]
    )
    assert urls == ["https://inaturalist-open-data.s3.amazonaws.com/ok.jpg"]


def test_extrair_urls_geojson_e_exsiccatae(monkeypatch):
    monkeypatch.setattr(
        settings,
        "SPECIESLINK_EXSICCATAE_IMAGE_URL_TEMPLATE",
        "https://img.test/{imagecode}/large/",
    )
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "barcode": "FLOR0037759",
                    "occurrenceremarks": '<a href="https://exemplo.org/foto.jpg">link</a>',
                },
            }
        ],
    }
    urls = extrair_urls_imagem(payload, max_imagens=5)
    assert "https://exemplo.org/foto.jpg" in urls
    assert "https://img.test/FLOR0037759/large/" in urls
