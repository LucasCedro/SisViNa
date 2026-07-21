# app/config.py
import os
from pydantic import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Brotare Viveiros API"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SPECIESLINK_API_KEY: str = ""
    SPECIESLINK_API_BASE_URL: str = "https://specieslink.net/ws/1.0"
    SPECIESLINK_REQUEST_TIMEOUT: float = 25.0
    SPECIESLINK_VERIFY_SSL: bool = True
    SPECIESLINK_MAX_IMAGENS_POR_ESPECIE: int = 12
    SPECIESLINK_SEARCH_LIMIT: int = 40
    SPECIESLINK_SCOPE: str = "p"
    SPECIESLINK_CACHE_DIAS: int = 30
    # Exsiccatae (reflora*.cria.org.br) está fora do ar — deixe vazio; use fallback iNaturalist.
    SPECIESLINK_EXSICCATAE_IMAGE_URL_TEMPLATE: str = ""
    SPECIESLINK_VALIDAR_URL_IMAGEM: bool = False
    GBIF_FALLBACK_ENABLED: bool = True
    GBIF_API_BASE_URL: str = "https://api.gbif.org/v1"
    GBIF_COUNTRY_FILTER: str = "BR"
    GBIF_SEARCH_LIMIT: int = 20
    GBIF_MAX_IMAGENS_POR_ESPECIE: int = 12
    INATURALIST_FALLBACK_ENABLED: bool = True
    INATURALIST_API_BASE_URL: str = "https://api.inaturalist.org/v1"
    INATURALIST_MAX_IMAGENS_POR_ESPECIE: int = 3
    IMAGENS_FALLBACK_GENERO_ENABLED: bool = True
    # Pasta public/ do front (para validar JPG local). No Docker: /biblioteca_public
    BIBLIOTECA_PUBLIC_ROOT: str = ""

    FOCUS_NFE_TOKEN: str = ""
    FOCUS_NFE_URL_HOMOLOGACAO: str = "https://homologacao.focusnfe.com.br"
    FOCUS_NFE_URL_PRODUCAO: str = "https://api.focusnfe.com.br"
    FOCUS_NFE_TIMEOUT: float = 60.0
    # Nunca true em dev/demo — só homologação Focus até liberação consciente
    NFE_ALLOW_PRODUCAO: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
