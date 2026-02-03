"""
Configuração de testes usando pytest.
"""

import pytest
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente para testes
load_dotenv(".env.test")


@pytest.fixture(scope="session")
def test_settings():
    """Fixture para configurações de teste."""
    os.environ["DEBUG"] = "True"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
    os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def mock_ipinfo_response():
    """Fixture para resposta mockada do IPinfo."""
    return {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "United States",
        "loc": "37.3861,-122.0839",
        "org": "AS15169 Google LLC",
        "timezone": "America/Los_Angeles",
        "privacy": {
            "vpn": False,
            "proxy": False,
            "tor": False,
            "relay": False
        }
    }


@pytest.fixture
def mock_ipapi_response():
    """Fixture para resposta mockada do IP-API."""
    return {
        "status": "success",
        "query": "8.8.8.8",
        "country": "United States",
        "countryCode": "US",
        "city": "Mountain View",
        "lat": 37.3861,
        "lon": -122.0839,
        "isp": "Google LLC",
        "org": "Google",
        "as": "AS15169 Google LLC",
        "proxy": False,
        "hosting": False
    }


@pytest.fixture
def mock_abuseipdb_response():
    """Fixture para resposta mockada do AbuseIPDB."""
    return {
        "data": {
            "ipAddress": "8.8.8.8",
            "isWhitelisted": False,
            "abuseConfidenceScore": 0,
            "countryCode": "US",
            "usageType": "Content Delivery Network",
            "isp": "Google LLC",
            "domain": "google.com",
            "totalReports": 0,
            "numDistinctUsers": 0,
            "lastReportedAt": None
        }
    }
