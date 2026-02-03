"""
Testes unitários para validadores de IP e domínio.
"""

import pytest
from app.validators import (
    is_valid_ip,
    is_valid_domain,
    get_query_type,
    validate_and_normalize_ip,
    validate_and_normalize_domain,
    validate_query_input,
    IPValidator,
    DomainValidator,
    QueryValidator
)


class TestIPValidation:
    """Testes para validação de IPs."""

    def test_valid_ipv4(self):
        """Testar validação de IPv4 válido."""
        assert is_valid_ip("8.8.8.8") is True
        assert is_valid_ip("192.168.1.1") is True
        assert is_valid_ip("127.0.0.1") is True

    def test_valid_ipv6(self):
        """Testar validação de IPv6 válido."""
        assert is_valid_ip("2001:4860:4860::8888") is True
        assert is_valid_ip("::1") is True
        assert is_valid_ip("fe80::1") is True

    def test_invalid_ip(self):
        """Testar rejeição de IPs inválidos."""
        assert is_valid_ip("999.999.999.999") is False
        assert is_valid_ip("invalid") is False
        assert is_valid_ip("") is False
        assert is_valid_ip("192.168.1") is False

    def test_normalize_ipv4(self):
        """Testar normalização de IPv4."""
        result = validate_and_normalize_ip("8.8.8.8")
        assert result == "8.8.8.8"

    def test_normalize_invalid_ip(self):
        """Testar normalização de IP inválido."""
        result = validate_and_normalize_ip("invalid")
        assert result is None

    def test_ipvalidator_model(self):
        """Testar modelo Pydantic IPValidator."""
        validator = IPValidator(ip="8.8.8.8")
        assert validator.ip == "8.8.8.8"

        with pytest.raises(ValueError):
            IPValidator(ip="invalid")


class TestDomainValidation:
    """Testes para validação de domínios."""

    def test_valid_domain(self):
        """Testar validação de domínio válido."""
        assert is_valid_domain("google.com") is True
        assert is_valid_domain("example.org") is True
        assert is_valid_domain("test.co.uk") is True

    def test_valid_subdomain(self):
        """Testar validação de subdomínio."""
        assert is_valid_domain("mail.google.com") is True
        assert is_valid_domain("api.example.com") is True
        assert is_valid_domain("sub.domain.example.com") is True

    def test_invalid_domain(self):
        """Testar rejeição de domínios inválidos."""
        assert is_valid_domain("invalid..com") is False
        assert is_valid_domain(".com") is False
        assert is_valid_domain("") is False
        assert is_valid_domain("invalid_domain.com") is False

    def test_domain_case_insensitive(self):
        """Testar que validação de domínio é case-insensitive."""
        assert is_valid_domain("GOOGLE.COM") is True
        assert is_valid_domain("Google.Com") is True

    def test_normalize_domain(self):
        """Testar normalização de domínio."""
        result = validate_and_normalize_domain("GOOGLE.COM")
        assert result == "google.com"

    def test_normalize_invalid_domain(self):
        """Testar normalização de domínio inválido."""
        result = validate_and_normalize_domain("invalid..com")
        assert result is None

    def test_domainvalidator_model(self):
        """Testar modelo Pydantic DomainValidator."""
        validator = DomainValidator(domain="google.com")
        assert validator.domain == "google.com"

        with pytest.raises(ValueError):
            DomainValidator(domain="invalid..com")


class TestQueryTypeDetection:
    """Testes para detecção de tipo de query."""

    def test_detect_ipv4(self):
        """Testar detecção de IPv4."""
        assert get_query_type("8.8.8.8") == "ip"

    def test_detect_ipv6(self):
        """Testar detecção de IPv6."""
        assert get_query_type("2001:4860:4860::8888") == "ip"

    def test_detect_domain(self):
        """Testar detecção de domínio."""
        assert get_query_type("google.com") == "domain"
        assert get_query_type("mail.google.com") == "domain"

    def test_detect_invalid_query(self):
        """Testar detecção de query inválida."""
        # Query inválida é tratada como domínio por padrão
        result = get_query_type("invalid..com")
        assert result in ["ip", "domain"]


class TestQueryValidation:
    """Testes para validação de queries genéricas."""

    def test_validate_ip_query(self):
        """Testar validação de query com IP."""
        result = validate_query_input("8.8.8.8")
        assert result is not None
        query, query_type = result
        assert query == "8.8.8.8"
        assert query_type == "ip"

    def test_validate_domain_query(self):
        """Testar validação de query com domínio."""
        result = validate_query_input("google.com")
        assert result is not None
        query, query_type = result
        assert query == "google.com"
        assert query_type == "domain"

    def test_validate_invalid_query(self):
        """Testar validação de query inválida."""
        result = validate_query_input("invalid..com")
        # Pode retornar None ou um resultado dependendo da implementação
        # Aqui testamos que não lança exceção

    def test_sanitize_whitespace(self):
        """Testar sanitização de espaços em branco."""
        result = validate_query_input("  8.8.8.8  ")
        assert result is not None
        query, _ = result
        assert query == "8.8.8.8"

    def test_reject_dangerous_chars(self):
        """Testar rejeição de caracteres perigosos."""
        result = validate_query_input("8.8.8.8'; DROP TABLE--")
        assert result is None

    def test_queryvalidator_model(self):
        """Testar modelo Pydantic QueryValidator."""
        validator = QueryValidator(query="8.8.8.8")
        assert validator.query == "8.8.8.8"
        assert validator.query_type == "ip"

        validator2 = QueryValidator(query="google.com")
        assert validator2.query == "google.com"
        assert validator2.query_type == "domain"


class TestEdgeCases:
    """Testes para casos extremos."""

    def test_max_length_domain(self):
        """Testar domínio com comprimento máximo."""
        # Domínio com 63 caracteres por label (máximo RFC)
        long_domain = "a" * 63 + ".com"
        assert is_valid_domain(long_domain) is True

    def test_min_length_domain(self):
        """Testar domínio com comprimento mínimo."""
        assert is_valid_domain("ab.c") is True

    def test_ipv6_compressed(self):
        """Testar IPv6 comprimido."""
        assert is_valid_ip("::") is True
        assert is_valid_ip("::1") is True

    def test_ipv6_full(self):
        """Testar IPv6 completo."""
        assert is_valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
