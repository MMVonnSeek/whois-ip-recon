.PHONY: help install dev test lint format security clean docs

help:
	@echo "Whois & IP Info Aggregator - Comandos disponíveis"
	@echo ""
	@echo "Instalação e Setup:"
	@echo "  make install          - Instalar dependências"
	@echo "  make install-dev      - Instalar dependências de desenvolvimento"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make dev              - Iniciar servidor de desenvolvimento"
	@echo "  make test             - Executar testes"
	@echo "  make test-cov         - Executar testes com cobertura"
	@echo ""
	@echo "Qualidade de Código:"
	@echo "  make lint             - Verificar linting (flake8, pylint)"
	@echo "  make format           - Formatar código (black, isort)"
	@echo "  make type-check       - Verificar tipos (mypy)"
	@echo "  make security         - Verificar segurança (bandit, safety)"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean            - Remover arquivos temporários"
	@echo "  make clean-all        - Remover tudo incluindo venv"
	@echo ""
	@echo "Documentação:"
	@echo "  make docs             - Gerar documentação"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app tests --max-line-length=100 --exclude=__pycache__,.venv
	pylint app tests --disable=C0111,R0903

format:
	black app tests --line-length=100
	isort app tests --profile=black --line-length=100

type-check:
	mypy app --ignore-missing-imports

security:
	bandit -r app -ll
	safety check

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean
	rm -rf .venv venv ENV env

docs:
	@echo "Documentação disponível em:"
	@echo "  - Swagger UI: http://localhost:8000/docs"
	@echo "  - ReDoc: http://localhost:8000/redoc"
	@echo "  - OpenAPI JSON: http://localhost:8000/openapi.json"

.DEFAULT_GOAL := help
