"""
Testes para endpoints da API FastAPI.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.schemas import AggregatedQueryResponse


@pytest.fixture
def client():
    """Fixture para cliente de teste."""
    return TestClient(app)


class TestHealthEndpoints:
    """Testes para endpoints de health check."""

    def test_health_check(self, client):
        """Testar endpoint de health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data

    def test_status_endpoint(self, client):
        """Testar endpoint de status."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Testar endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestQueryEndpoint:
    """Testes para endpoint de query."""

    @pytest.mark.asyncio
    async def test_valid_ip_query(self, client):
        """Testar query com IP válido."""
        with patch("app.services.aggregator_service.AggregatorService.aggregate_query") as mock:
            mock_response = AggregatedQueryResponse(
                query="8.8.8.8",
                query_type="ip",
                ip_address="8.8.8.8",
                country="United States",
                city="Mountain View",
                asn="AS15169",
                isp="Google LLC",
                risk_level="low"
            )
            mock.return_value = mock_response

            response = client.post("/api/v1/query", json={"query": "8.8.8.8"})
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "8.8.8.8"
            assert data["query_type"] == "ip"
            assert data["risk_level"] == "low"

    def test_invalid_query(self, client):
        """Testar query com input inválido."""
        response = client.post("/api/v1/query", json={"query": "invalid..com"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_empty_query(self, client):
        """Testar query vazia."""
        response = client.post("/api/v1/query", json={"query": ""})
        assert response.status_code == 422  # Validation error

    def test_query_too_long(self, client):
        """Testar query muito longa."""
        long_query = "a" * 300
        response = client.post("/api/v1/query", json={"query": long_query})
        assert response.status_code == 422  # Validation error

    def test_query_with_dangerous_chars(self, client):
        """Testar query com caracteres perigosos."""
        response = client.post(
            "/api/v1/query",
            json={"query": "8.8.8.8'; DROP TABLE--"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_domain_query(self, client):
        """Testar query com domínio válido."""
        with patch("app.services.aggregator_service.AggregatorService.aggregate_query") as mock:
            mock_response = AggregatedQueryResponse(
                query="google.com",
                query_type="domain",
                ip_address="142.250.185.46",
                country="United States",
                city="Mountain View",
                asn="AS15169",
                isp="Google LLC",
                risk_level="low"
            )
            mock.return_value = mock_response

            response = client.post("/api/v1/query", json={"query": "google.com"})
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "google.com"
            assert data["query_type"] == "domain"


class TestErrorHandling:
    """Testes para tratamento de erros."""

    def test_method_not_allowed(self, client):
        """Testar método HTTP não permitido."""
        response = client.get("/api/v1/query")
        assert response.status_code == 405

    def test_not_found(self, client):
        """Testar endpoint não encontrado."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Testar JSON inválido."""
        response = client.post(
            "/api/v1/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


class TestCORS:
    """Testes para CORS."""

    def test_cors_headers(self, client):
        """Testar headers CORS."""
        response = client.options("/api/v1/query")
        # FastAPI pode não retornar 200 para OPTIONS sem configuração específica
        # Apenas verificamos que não é 500
        assert response.status_code != 500


class TestDocumentation:
    """Testes para documentação da API."""

    def test_swagger_docs(self, client):
        """Testar acesso a documentação Swagger."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_redoc_docs(self, client):
        """Testar acesso a documentação ReDoc."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Testar schema OpenAPI."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/api/v1/query" in data["paths"]
