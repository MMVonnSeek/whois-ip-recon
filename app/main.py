"""
Aplicação FastAPI para Whois & IP Info Aggregator.
Implementa endpoints seguros e documentados com Swagger/OpenAPI.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.logging_config import setup_logging
from app.validators import validate_query_input
from app.schemas import QueryRequest, AggregatedQueryResponse, ErrorResponse, HealthResponse
from app.services.aggregator_service import AggregatorService

# Configurar logging
logger = setup_logging()
logger = logging.getLogger(__name__)

# Inicializar serviços globais
aggregator_service: AggregatorService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciar ciclo de vida da aplicação.
    Inicializa recursos ao iniciar e limpa ao desligar.
    """
    global aggregator_service
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Startup
    aggregator_service = AggregatorService()

    yield

    # Shutdown
    logger.info("Shutting down services")
    if aggregator_service:
        await aggregator_service.close()


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API profissional para agregação de informações de IP e Whois",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Configurar Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    """Handler para limite de taxa excedido."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Limite de requisições excedido. Tente novamente mais tarde.",
            "error_code": "RATE_LIMIT_EXCEEDED"
        }
    )


# ==================== Endpoints ====================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verificar saúde da aplicação.

    Returns:
        HealthResponse com status da aplicação
    """
    logger.info("Health check requested")

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database="connected",
        external_apis={
            "ipinfo": True,
            "ipapi": True,
            "abuseipdb": bool(settings.abuseipdb_api_key)
        }
    )


@app.post(
    "/api/v1/query",
    response_model=AggregatedQueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Query inválida"},
        429: {"model": ErrorResponse, "description": "Limite de taxa excedido"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["Queries"]
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def query_ip_or_domain(http_request: Request, request: QueryRequest):
    """
    Consultar informações de IP ou domínio.

    Agrega dados de múltiplas fontes:
    - IPinfo.io: Geolocalização e detecção de VPN/Proxy
    - IP-API.com: Geolocalização alternativa
    - AbuseIPDB: Reputação e detecção de abuso

    Args:
        request: QueryRequest com o IP ou domínio a consultar

    Returns:
        AggregatedQueryResponse com dados agregados

    Raises:
        HTTPException: Se a query for inválida
    """
    logger.info(f"Query requested for: {request.query}")

    # Validar input
    validation_result = validate_query_input(request.query)
    if not validation_result:
        logger.warning(f"Invalid query: {request.query}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{request.query}' não é um IP ou domínio válido",
            headers={"X-Error-Code": "INVALID_QUERY"}
        )

    normalized_query, query_type = validation_result

    try:
        # Agregar dados
        result = await aggregator_service.aggregate_query(normalized_query)

        logger.info(
            f"Query completed for {normalized_query}",
            extra={
                "extra_fields": {
                    "query_type": query_type,
                    "risk_level": result.risk_level
                }
            }
        )

        return result

    except Exception as e:
        logger.error(f"Error processing query {request.query}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a consulta. Tente novamente mais tarde.",
            headers={"X-Error-Code": "QUERY_FAILED"}
        )


@app.get("/api/v1/status", response_model=HealthResponse, tags=["Status"])
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_status(request: Request):

    """
    Obter status detalhado da aplicação.

    Returns:
        HealthResponse com informações de saúde
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database="connected",
        external_apis={
            "ipinfo": True,
            "ipapi": True,
            "abuseipdb": bool(settings.abuseipdb_api_key)
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# ==================== Error Handlers ====================


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler genérico para exceções não tratadas."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
