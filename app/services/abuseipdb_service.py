"""
Serviço de integração com AbuseIPDB API.
Fornece informações de reputação e detecção de abuso de IPs.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from app.config import settings
from app.schemas import AbuseScoreResponse

logger = logging.getLogger(__name__)


class AbuseIPDBService:
    """Serviço para consultar reputação de IP no AbuseIPDB."""

    BASE_URL = "https://api.abuseipdb.com/api/v2/check"
    TIMEOUT = 10

    def __init__(self):
        self.api_key = settings.abuseipdb_api_key
        self.client = httpx.AsyncClient(timeout=self.TIMEOUT)

    async def get_abuse_score(self, ip: str) -> Optional[AbuseScoreResponse]:
        """
        Obter score de abuso de IP do AbuseIPDB.

        Args:
            ip: Endereço IP a consultar

        Returns:
            AbuseScoreResponse com dados de abuso ou None se erro
        """
        if not self.api_key:
            logger.warning("AbuseIPDB API key not configured, skipping")
            return None

        try:
            headers = {
                "Key": self.api_key,
                "Accept": "application/json"
            }

            params = {
                "ipAddress": ip,
                "maxAgeInDays": 90,
                "verbose": ""
            }

            response = await self.client.get(
                self.BASE_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"AbuseIPDB response for {ip}: {data}")

            return self._parse_response(data)

        except httpx.HTTPError as e:
            logger.error(f"AbuseIPDB HTTP error for {ip}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"AbuseIPDB error for {ip}: {str(e)}")
            return None

    def _parse_response(self, data: Dict[str, Any]) -> AbuseScoreResponse:
        """Parse resposta do AbuseIPDB para nosso schema."""
        abuse_data = data.get("data", {})

        # Parse last reported date
        last_reported = None
        if abuse_data.get("lastReportedAt"):
            try:
                last_reported = datetime.fromisoformat(
                    abuse_data["lastReportedAt"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return AbuseScoreResponse(
            ip=abuse_data.get("ipAddress", ""),
            abuse_score=abuse_data.get("abuseConfidenceScore", 0),
            is_whitelisted=abuse_data.get("isWhitelisted", False),
            total_reports=abuse_data.get("totalReports", 0),
            country_code=abuse_data.get("countryCode"),
            last_reported_at=last_reported,
            source="abuseipdb"
        )

    async def close(self):
        """Fechar conexão HTTP."""
        await self.client.aclose()
