"""
Configuração de logging estruturado.
Implementa logging profissional com JSON para produção.
"""

import logging
import logging.config
import json
from datetime import datetime
from app.config import settings


class JSONFormatter(logging.Formatter):
    """Formatter que retorna logs em formato JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Formatar log como JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adicionar exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Adicionar campos extras
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging():
    """Configurar logging da aplicação."""

    log_format = settings.log_format
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Obter logger para um módulo específico."""
    return logging.getLogger(name)
