"""
Serviço de integração com IPinfo.io API.
Fornece informações de geolocalização e detecção de VPN/Proxy.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from app.config import settings
from app.schemas import IPInfoResponse

logger = logging.getLogger(__name__)


class IPInfoService:
    """Serviço para consultar dados de IP no IPinfo.io."""

    BASE_URL = "https://ipinfo.io"
    TIMEOUT = 10

    def __init__(self):
        self.api_key = settings.ipinfo_api_key
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT)

    async def get_ip_info(self, ip: str) -> Optional[IPInfoResponse]:
        """
        Obter informações de IP do IPinfo.io.

        Args:
            ip: Endereço IP a consultar

        Returns:
            IPInfoResponse com dados do IP ou None se erro
        """
        try:
            url = f"{self.BASE_URL}/{ip}"
            params = {}

            if self.api_key:
                params["token"] = self.api_key

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.info(f"IPinfo.io response for {ip}: {data}")

            return self._parse_response(data)

        except httpx.HTTPError as e:
            logger.error(f"IPinfo.io HTTP error for {ip}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"IPinfo.io error for {ip}: {str(e)}")
            return None

    def _parse_response(self, data: Dict[str, Any]) -> IPInfoResponse:
        """Parse resposta do IPinfo.io para nosso schema."""
        # Extrair coordenadas se disponível
        latitude, longitude = None, None
        if "loc" in data:
            try:
                lat_str, lon_str = data["loc"].split(",")
                latitude = float(lat_str)
                longitude = float(lon_str)
            except (ValueError, AttributeError):
                pass

        # Determinar se é VPN/Proxy baseado em informações disponíveis
        is_vpn = data.get("vpn", {}).get("signal", False) if isinstance(data.get("vpn"), dict) else False
        is_proxy = data.get("privacy", {}).get("proxy", False) if isinstance(data.get("privacy"), dict) else False

        return IPInfoResponse(
            ip=data.get("ip", ""),
            hostname=data.get("hostname"),
            city=data.get("city"),
            region=data.get("region"),
            country=data.get("country"),
            country_code=data.get("country"),  # IPinfo retorna code em 'country'
            latitude=latitude,
            longitude=longitude,
            asn=data.get("org"),  # IPinfo retorna ASN em 'org'
            isp=data.get("org"),
            is_vpn=is_vpn,
            is_proxy=is_proxy,
            is_tor=False,  # IPinfo não fornece detecção de Tor
            timezone=data.get("timezone"),
            source="ipinfo"
        )

    async def close(self):
        """Fechar conexão HTTP."""
        await self.client.aclose()
