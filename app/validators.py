"""
Validadores robustos para IPs, domínios e inputs.
Implementa as melhores práticas de validação de entrada para cibersegurança.
"""

import re
from ipaddress import ip_address, AddressValueError
from typing import Literal, Optional, Tuple
from pydantic import BaseModel, Field, validator


class IPValidator(BaseModel):
    """Validador para endereços IP (IPv4 e IPv6)."""

    ip: str = Field(..., min_length=7, max_length=45)

    @validator("ip")
    def validate_ip(cls, v: str) -> str:
        """Validar se é um endereço IP válido."""
        try:
            ip_address(v)
            return v
        except AddressValueError:
            raise ValueError(f"'{v}' não é um endereço IP válido (IPv4 ou IPv6)")


class DomainValidator(BaseModel):
    """Validador para domínios."""

    domain: str = Field(..., min_length=3, max_length=255)

    @validator("domain")
    def validate_domain(cls, v: str) -> str:
        """Validar se é um domínio válido."""
        # RFC 1123 compliant domain regex
        domain_regex = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"

        if not re.match(domain_regex, v.lower()):
            raise ValueError(f"'{v}' não é um domínio válido")

        return v.lower()


class QueryValidator(BaseModel):
    """Validador para queries genéricas (IP ou domínio)."""

    query: str = Field(..., min_length=3, max_length=255)
    query_type: Optional[Literal["ip", "domain"]] = None

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Sanitizar e validar query."""
        # Remover espaços em branco
        v = v.strip()

        # Rejeitar caracteres perigosos
        dangerous_chars = r"[<>\"'%;()&+]"
        if re.search(dangerous_chars, v):
            raise ValueError("Query contém caracteres inválidos")

        return v

    @validator("query_type", pre=True, always=True)
    def determine_query_type(cls, v: str, values: dict) -> str:
        """Determinar automaticamente o tipo de query se não especificado."""
        if v is not None:
            return v

        query = values.get("query", "")
        if is_valid_ip(query):
            return "ip"
        elif is_valid_domain(query):
            return "domain"
        else:
            raise ValueError("Não foi possível determinar o tipo de query")


def is_valid_ip(value: str) -> bool:
    """Verificar se é um IP válido."""
    try:
        ip_address(value)
        return True
    except (AddressValueError, ValueError):
        return False


def is_valid_domain(value: str) -> bool:
    """Verificar se é um domínio válido."""
    domain_regex = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
    return bool(re.match(domain_regex, value.lower()))


def get_query_type(query: str) -> Literal["ip", "domain"]:
    """Determinar o tipo de query (IP ou domínio)."""
    if is_valid_ip(query):
        return "ip"
    return "domain"


def sanitize_input(value: str, max_length: int = 255) -> str:
    """
    Sanitizar input removendo caracteres perigosos.
    Implementa proteção contra injeção de código.
    """
    # Limitar comprimento
    value = value[:max_length]

    # Remover espaços em branco extras
    value = value.strip()

    # Remover caracteres de controle
    value = "".join(char for char in value if ord(char) >= 32)

    return value


def validate_and_normalize_ip(ip: str) -> Optional[str]:
    """Validar e normalizar endereço IP."""
    try:
        validator = IPValidator(ip=ip)
        return validator.ip
    except ValueError:
        return None


def validate_and_normalize_domain(domain: str) -> Optional[str]:
    """Validar e normalizar domínio."""
    try:
        validator = DomainValidator(domain=domain)
        return validator.domain
    except ValueError:
        return None


def validate_query_input(query: str) -> Optional[Tuple[str, Literal["ip", "domain"]]]:
    """
    Validar input de query genérica.
    Retorna tuple (query_normalizada, tipo) ou None se inválido.
    """
    try:
        validator = QueryValidator(query=query)
        return (validator.query, validator.query_type)
    except ValueError:
        return None
