"""
Serviço agregador que combina dados de múltiplas APIs.
Implementa lógica de orquestração e análise de risco.
"""

import logging
from typing import Optional, Literal, Dict
import asyncio
from app.validators import is_valid_ip, get_query_type
from app.schemas import AggregatedQueryResponse, IPInfoResponse
from app.services.ipinfo_service import IPInfoService
from app.services.ipapi_service import IPAPIService
from app.services.abuseipdb_service import AbuseIPDBService

logger = logging.getLogger(__name__)


class AggregatorService:
    """Serviço que agrega dados de múltiplas fontes."""

    def __init__(self):
        self.ipinfo_service = IPInfoService()
        self.ipapi_service = IPAPIService()
        self.abuseipdb_service = AbuseIPDBService()

    async def aggregate_query(self, query: str) -> AggregatedQueryResponse:
        """
        Agregar informações de IP/domínio de múltiplas fontes.

        Args:
            query: IP ou domínio a consultar

        Returns:
            AggregatedQueryResponse com dados agregados
        """
        query_type = get_query_type(query)
        ip_address = query if is_valid_ip(query) else None

        try:
            # Se for domínio, precisamos resolver o IP primeiro
            if query_type == "domain" and not ip_address:
                ip_address = await self._resolve_domain(query)
                if not ip_address:
                    return AggregatedQueryResponse(
                        query=query,
                        query_type=query_type,
                        risk_level="low",
                        error=f"Não foi possível resolver o domínio {query}"
                    )

            # Executar consultas em paralelo
            results = await asyncio.gather(
                self.ipinfo_service.get_ip_info(ip_address),
                self.ipapi_service.get_ip_info(ip_address),
                self.abuseipdb_service.get_abuse_score(ip_address),
                return_exceptions=True
            )

            ipinfo_result = results[0] if not isinstance(results[0], Exception) else None
            ipapi_result = results[1] if not isinstance(results[1], Exception) else None
            abuse_result = results[2] if not isinstance(results[2], Exception) else None

            # Agregar dados
            aggregated = self._aggregate_results(
                query, query_type, ip_address,
                ipinfo_result, ipapi_result, abuse_result
            )

            return aggregated

        except Exception as e:
            logger.error(f"Error aggregating query {query}: {str(e)}")
            return AggregatedQueryResponse(
                query=query,
                query_type=query_type,
                risk_level="low",
                error=str(e)
            )

    async def _resolve_domain(self, domain: str) -> Optional[str]:
        """
        Resolver domínio para IP.
        Implementação simplificada - em produção usar DNS resolver apropriado.
        """
        try:
            import socket
            ip = socket.gethostbyname(domain)
            logger.info(f"Resolved domain {domain} to {ip}")
            return ip
        except socket.gaierror as e:
            logger.error(f"Failed to resolve domain {domain}: {str(e)}")
            return None

    def _aggregate_results(
        self,
        query: str,
        query_type: Literal["ip", "domain"],
        ip_address: Optional[str],
        ipinfo_result: Optional[IPInfoResponse],
        ipapi_result: Optional[IPInfoResponse],
        abuse_result: Optional[Dict]
    ) -> AggregatedQueryResponse:
        """Agregar resultados de múltiplas fontes."""

        # Usar dados do IPinfo como primário (mais confiável)
        primary = ipinfo_result or ipapi_result

        sources = {}
        if ipinfo_result:
            sources["ipinfo"] = ipinfo_result
        if ipapi_result:
            sources["ipapi"] = ipapi_result

        # Determinar nível de risco
        risk_level = self._calculate_risk_level(
            ipinfo_result, ipapi_result, abuse_result
        )

        abuse_score = None
        if abuse_result:
            abuse_score = abuse_result.get("abuse_score", 0)

        return AggregatedQueryResponse(
            query=query,
            query_type=query_type,
            ip_address=ip_address,
            country=primary.country if primary else None,
            city=primary.city if primary else None,
            latitude=primary.latitude if primary else None,
            longitude=primary.longitude if primary else None,
            asn=primary.asn if primary else None,
            isp=primary.isp if primary else None,
            is_proxy=primary.is_proxy if primary else False,
            is_vpn=primary.is_vpn if primary else False,
            is_tor=primary.is_tor if primary else False,
            abuse_score=abuse_score,
            timezone=primary.timezone if primary else None,
            risk_level=risk_level,
            sources=sources
        )

    def _calculate_risk_level(
        self,
        ipinfo_result: Optional[IPInfoResponse],
        ipapi_result: Optional[IPInfoResponse],
        abuse_result: Optional[Dict]
    ) -> Literal["low", "medium", "high"]:
        """
        Calcular nível de risco baseado em múltiplos fatores.
        """
        risk_score = 0

        # Verificar VPN/Proxy
        is_vpn_or_proxy = False
        if ipinfo_result and (ipinfo_result.is_vpn or ipinfo_result.is_proxy):
            is_vpn_or_proxy = True
            risk_score += 20
        if ipapi_result and (ipapi_result.is_vpn or ipapi_result.is_proxy):
            is_vpn_or_proxy = True
            risk_score += 20

        # Verificar Tor
        if ipinfo_result and ipinfo_result.is_tor:
            risk_score += 30
        if ipapi_result and ipapi_result.is_tor:
            risk_score += 30

        # Verificar score de abuso
        if abuse_result:
            abuse_score = abuse_result.get("abuse_score", 0)
            if abuse_score > 75:
                risk_score += 40
            elif abuse_score > 50:
                risk_score += 25
            elif abuse_score > 25:
                risk_score += 10

        # Determinar nível
        if risk_score >= 50:
            return "high"
        elif risk_score >= 25:
            return "medium"
        else:
            return "low"

    async def close(self):
        """Fechar todas as conexões."""
        await asyncio.gather(
            self.ipinfo_service.close(),
            self.ipapi_service.close(),
            self.abuseipdb_service.close(),
            return_exceptions=True
        )
