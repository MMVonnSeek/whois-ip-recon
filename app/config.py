"""
Configuração centralizada da aplicação.
Segue as melhores práticas de segurança e gerenciamento de secrets.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic."""

    # Aplicação
    app_name: str = Field(default="Whois & IP Info Aggregator", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Banco de Dados
    database_url: str = Field(
        default="sqlite:///./whois_aggregator.db", env="DATABASE_URL"
    )

    # Segurança
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # APIs Externas
    ipinfo_api_key: Optional[str] = Field(default=None, env="IPINFO_API_KEY")
    abuseipdb_api_key: Optional[str] = Field(default=None, env="ABUSEIPDB_API_KEY")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # CORS
    allowed_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validar que a chave secreta é suficientemente longa em produção."""
        if len(v) < 32:
            import warnings
            warnings.warn(
                "SECRET_KEY é muito curta. Use uma chave com pelo menos 32 caracteres em produção.",
                UserWarning
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna a instância de configurações (cached).
    Usa LRU cache para evitar recarregar configurações múltiplas vezes.
    """
    return Settings()


# Exportar instância global
settings = get_settings()
