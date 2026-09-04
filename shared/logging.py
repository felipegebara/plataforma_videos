"""
Logging padrão do Antigravity.
Todos os agentes usam get_logger(nome_do_agente) para logs consistentes.
"""
import logging
import sys

# Garante suporte a UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_logger(agent_name: str) -> logging.Logger:
    logger = logging.getLogger(agent_name)
    if logger.handlers:
        # evita duplicar handlers se get_logger for chamado mais de uma vez
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt=f"[%(asctime)s] [{agent_name}] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
