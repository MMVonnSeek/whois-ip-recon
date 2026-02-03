"""
Serviço de integração com IP-API.com.
Fornece informações de geolocalização e detecção de hosting.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from app.schemas import IPInfoResponse

logger = logging.getLogger(__name__)


class IPAPIService:
    """Serviço para consultar dados de IP no IP-API.com."""

    BASE_URL = "http://ip-api.com/json"
    TIMEOUT = 10

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT)

    async def get_ip_info(self, ip: str) -> Optional[IPInfoResponse]:
        """
        Obter informações de IP do IP-API.com.

        Args:
            ip: Endereço IP a consultar

        Returns:
            IPInfoResponse com dados do IP ou None se erro
        """
        try:
            params = {
                "query": ip,
                "fields": "status,query,country,countryCode,city,lat,lon,isp,org,as,proxy,hosting"
            }

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # Verificar se a query foi bem-sucedida
            if data.get("status") != "success":
                logger.warning(f"IP-API.com failed for {ip}: {data.get('message')}")
                return None

            logger.info(f"IP-API.com response for {ip}: {data}")
            return self._parse_response(data)

        except httpx.HTTPError as e:
            logger.error(f"IP-API.com HTTP error for {ip}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"IP-API.com error for {ip}: {str(e)}")
            return None

    def _parse_response(self, data: Dict[str, Any]) -> IPInfoResponse:
        """Parse resposta do IP-API.com para nosso schema."""
        return IPInfoResponse(
            ip=data.get("query", ""),
            hostname=None,  # IP-API não fornece hostname
            city=data.get("city"),
            region=None,  # IP-API não fornece region separado
            country=data.get("country"),
            country_code=data.get("countryCode"),
            latitude=data.get("lat"),
            longitude=data.get("lon"),
            asn=data.get("as"),
            isp=data.get("isp"),
            is_vpn=data.get("proxy", False),
            is_proxy=data.get("proxy", False),
            is_tor=False,  # IP-API não fornece detecção de Tor
            timezone=None,  # IP-API não fornece timezone neste endpoint
            source="ipapi"
        )

    async def close(self):
        """Fechar conexão HTTP."""
        await self.client.aclose()
