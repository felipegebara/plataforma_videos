"""
core/config.py
==============
Sistema de configuracao via arquivo .env para o Rota Calculada AI Video Studio PRO.
Parsing manual do .env sem dependencia de python-dotenv.
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger("core.config")
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ENV_FILE = _PROJECT_ROOT / ".env"


def load_env(env_path=None):
    """
    Carrega o arquivo .env e injeta as variaveis em os.environ.

    Suporta:
    - Linhas KEY=VALUE (com ou sem aspas)
    - Linhas comecando com # sao comentarios e ignoradas
    - Linhas em branco sao ignoradas

    Retorna um dict com as chaves/valores carregados nesta chamada.
    """
    if env_path is None:
        env_path = _ENV_FILE
    loaded = {}
    if not Path(env_path).exists():
        logger.debug("Arquivo .env nao encontrado em %s.", env_path)
        return loaded
    try:
        with open(env_path, "r", encoding="utf-8") as fh:
            for line_num, raw_line in enumerate(fh, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    logger.debug(".env linha %d: formato invalido ignorado.", line_num)
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                if not key:
                    continue
                if key not in os.environ:
                    os.environ[key] = value
                loaded[key] = value
        logger.debug(".env carregado: %d variaveis de %s", len(loaded), env_path)
    except OSError as exc:
        logger.warning("Nao foi possivel ler o arquivo .env: %s", exc)
    return loaded


def get(key, default=None):
    """
    Retorna o valor de uma variavel de ambiente.

    Args:
        key: Nome da variavel.
        default: Valor padrao caso a variavel nao esteja definida.

    Returns:
        Valor da variavel ou default.
    """
    return os.environ.get(key, default)


class Config:
    """
    Acesso estruturado as configuracoes de API do projeto.

    Todas as propriedades leem diretamente de os.environ, que ja foi
    populado por load_env() na importacao deste modulo.
    """

    @staticmethod
    def GEMINI_API_KEY():
        """Chave da API Google Gemini (gemini.google.com/app)."""
        return os.environ.get("GEMINI_API_KEY")

    @staticmethod
    def OPENAI_API_KEY():
        """Chave da API OpenAI (alternativa ao Gemini)."""
        return os.environ.get("OPENAI_API_KEY")

    @staticmethod
    def PEXELS_API_KEY():
        """Chave da API Pexels para busca de imagens/videos gratuitos."""
        return os.environ.get("PEXELS_API_KEY")

    @staticmethod
    def PIXABAY_API_KEY():
        """Chave da API Pixabay para busca de imagens/videos gratuitos."""
        return os.environ.get("PIXABAY_API_KEY")

    @staticmethod
    def YOUTUBE_CLIENT_SECRET_PATH():
        """Caminho para o arquivo client_secret.json do YouTube Data API."""
        return os.environ.get("YOUTUBE_CLIENT_SECRET_PATH", "client_secret.json")

    @staticmethod
    def MINIMAX_API_KEY():
        """Chave da API MiniMax (platform.minimaxi.com)."""
        return os.environ.get("MINIMAX_API_KEY")

    @staticmethod
    def MINIMAX_GROUP_ID():
        """Group ID MiniMax necessario para geracao de videos I2V."""
        return os.environ.get("MINIMAX_GROUP_ID")

    @classmethod
    def status(cls):
        """
        Retorna um dict indicando quais chaves estao configuradas.
        Util para debug e para o endpoint /api/settings/status.
        """
        yt_path = cls.YOUTUBE_CLIENT_SECRET_PATH()
        return {
            "gemini": bool(cls.GEMINI_API_KEY()),
            "openai": bool(cls.OPENAI_API_KEY()),
            "pexels": bool(cls.PEXELS_API_KEY()),
            "pixabay": bool(cls.PIXABAY_API_KEY()),
            "youtube": bool(yt_path and Path(yt_path).exists()),
            "minimax": bool(cls.MINIMAX_API_KEY()),
        }


# Executa o carregamento na importacao do modulo
_loaded_vars = load_env()
