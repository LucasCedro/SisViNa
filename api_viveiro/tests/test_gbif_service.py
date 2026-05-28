from app.services.gbif_service import _urls_de_ocorrencia


def test_urls_de_ocorrencia_ignora_identifier_numerico():
    record = {
        "media": [
            {"identifier": "334138944"},
            {
                "identifier": "https://example.org/foto.jpg",
                "license": "http://creativecommons.org/licenses/by/4.0/",
            },
        ]
    }
    assert _urls_de_ocorrencia(record) == ["https://example.org/foto.jpg"]
