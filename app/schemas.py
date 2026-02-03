"""
Schemas Pydantic para requisições e respostas.
Define contratos de API com validação automática.
"""

from datetime import datetime
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class QueryRequest(BaseModel):
    """Request para consultar IP ou domínio."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Endereço IP (IPv4/IPv6) ou domínio a consultar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "8.8.8.8"
            }
        }


class IPInfoResponse(BaseModel):
    """Response com informações de IP de uma única fonte."""

    ip: str
    hostname: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[str] = None
    isp: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    timezone: Optional[str] = None
    source: str = Field(..., description="Fonte dos dados (ipinfo, ipapi, abuseipdb)")

    class Config:
        json_schema_extra = {
            "example": {
                "ip": "8.8.8.8",
                "country": "United States",
                "city": "Mountain View",
                "asn": "AS15169",
                "isp": "Google LLC",
                "source": "ipinfo"
            }
        }


class AbuseScoreResponse(BaseModel):
    """Response com score de abuso de IP."""

    ip: str
    abuse_score: int = Field(..., ge=0, le=100, description="Score de abuso (0-100)")
    is_whitelisted: bool = False
    total_reports: int = 0
    country_code: Optional[str] = None
    last_reported_at: Optional[datetime] = None
    source: str = Field(default="abuseipdb", description="Fonte dos dados")

    class Config:
        json_schema_extra = {
            "example": {
                "ip": "8.8.8.8",
                "abuse_score": 0,
                "is_whitelisted": False,
                "total_reports": 0,
                "source": "abuseipdb"
            }
        }


class AggregatedQueryResponse(BaseModel):
    """Response agregada com dados de múltiplas fontes."""

    query: str = Field(..., description="Query original (IP ou domínio)")
    query_type: Literal["ip", "domain"] = Field(..., description="Tipo de query")
    ip_address: Optional[str] = Field(None, description="Endereço IP resolvido")
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[str] = None
    isp: Optional[str] = None
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    abuse_score: Optional[int] = Field(None, ge=0, le=100)
    timezone: Optional[str] = None
    risk_level: Literal["low", "medium", "high"] = Field(
        ...,
        description="Nível de risco baseado em múltiplos fatores"
    )
    sources: Dict[str, IPInfoResponse] = Field(
        default_factory=dict,
        description="Dados brutos de cada fonte"
    )
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "8.8.8.8",
                "query_type": "ip",
                "ip_address": "8.8.8.8",
                "country": "United States",
                "city": "Mountain View",
                "asn": "AS15169",
                "isp": "Google LLC",
                "is_proxy": False,
                "is_vpn": False,
                "is_tor": False,
                "abuse_score": 0,
                "risk_level": "low",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class QueryHistoryResponse(BaseModel):
    """Response com histórico de consultas."""

    id: int
    query: str
    query_type: Literal["ip", "domain"]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
    abuse_score: Optional[int]
    risk_level: Literal["low", "medium", "high"]
    status: Literal["success", "error", "pending"]
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Response padrão para erros."""

    detail: str = Field(..., description="Descrição do erro")
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "IP inválido",
                "error_code": "INVALID_IP",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Response para health check."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: Literal["connected", "disconnected"]
    external_apis: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status de cada API externa"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
                "external_apis": {
                    "ipinfo": True,
                    "ipapi": True,
                    "abuseipdb": False
                }
            }
        }
