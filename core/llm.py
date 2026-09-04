# -*- coding: utf-8 -*-
"""
core/llm.py
===========
LLM integration for Rota Calculada AI Video Studio PRO.

Supports Google Gemini 1.5-Flash (primary) and OpenAI GPT-4o-mini (fallback)
for generating viral Brazilian-Portuguese narration scripts and YouTube titles.

API keys are read from environment variables or from a .env file at the
project root. Returns None gracefully on any failure so callers can fall
back to template-based generation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("core.llm")

# -----------------------------------------------------------------------
# Project root & .env loader
# -----------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    """Manually parse .env file at project root and export to os.environ."""
    env_file = _PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception as exc:
        logger.warning(f"[LLM] Erro ao ler .env: {exc}")


_load_dotenv()


def _get_gemini_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY") or None


def _get_openai_key() -> Optional[str]:
    return os.environ.get("OPENAI_API_KEY") or None


# -----------------------------------------------------------------------
# Optional httpx import
# -----------------------------------------------------------------------
try:
    import httpx as _httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _httpx = None  # type: ignore
    _HTTPX_AVAILABLE = False
    logger.warning("[LLM] httpx nao instalado. Execute: pip install httpx")


# -----------------------------------------------------------------------
# Internal API callers
# -----------------------------------------------------------------------

def _call_gemini(prompt: str, key: str) -> Optional[str]:
    """Call Gemini 1.5-Flash API and return generated text."""
    if not _HTTPX_AVAILABLE:
        logger.error("[LLM] httpx nao disponivel para chamar Gemini.")
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 300},
    }
    try:
        resp = _httpx.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        logger.warning(f"[LLM] Gemini retornou resposta vazia: {data}")
        return None
    except Exception as exc:
        logger.error(f"[LLM] Erro na chamada Gemini: {exc}")
        return None


def _call_openai(prompt: str, key: str) -> Optional[str]:
    """Call OpenAI Chat Completions API and return generated text."""
    if not _HTTPX_AVAILABLE:
        logger.error("[LLM] httpx nao disponivel para chamar OpenAI.")
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 300,
    }
    try:
        resp = _httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "").strip()
        logger.warning(f"[LLM] OpenAI retornou resposta vazia: {data}")
        return None
    except Exception as exc:
        logger.error(f"[LLM] Erro na chamada OpenAI: {exc}")
        return None


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def generate_script(
    topic: str,
    category: str,
    format_type: str,
    duration_seconds: int = 15,
) -> Optional[str]:
    """
    Generate a viral Brazilian-Portuguese narration script via LLM.

    Tries Gemini first, then OpenAI. Returns None if neither key is
    configured or if all calls fail, allowing the caller to use template
    fallback.

    Parameters
    ----------
    topic            : Video topic / subject
    category         : Content category (e.g. 'MISTERY_HISTORY')
    format_type      : 'short' or 'long'
    duration_seconds : Target duration in seconds (default 15)

    Returns
    -------
    str  - generated narration text
    None - no LLM available or call failed
    """
    prompt = (
        f"Crie uma narração VIRAL em português brasileiro para um Short do YouTube "
        f"de {duration_seconds} segundos sobre o tema: {topic}. "
        f"Categoria: {category}. "
        f"Use linguagem de impacto, curiosidade e mistério. "
        f"Máximo 80 palavras. "
        f"Apenas o texto da narração, sem títulos ou introduções."
    )

    gemini_key = _get_gemini_key()
    if gemini_key:
        logger.info(f"[LLM] Gerando roteiro via Gemini para '{topic}'...")
        result = _call_gemini(prompt, gemini_key)
        if result:
            logger.info(f"[LLM] Roteiro Gemini gerado ({len(result.split())} palavras).")
            return result

    openai_key = _get_openai_key()
    if openai_key:
        logger.info(f"[LLM] Gerando roteiro via OpenAI para '{topic}'...")
        result = _call_openai(prompt, openai_key)
        if result:
            logger.info(f"[LLM] Roteiro OpenAI gerado ({len(result.split())} palavras).")
            return result

    if not gemini_key and not openai_key:
        logger.info(
            "[LLM] Nenhuma chave de API encontrada (GEMINI_API_KEY / OPENAI_API_KEY). "
            "Usando fallback de template."
        )
    return None


def generate_viral_titles(topic: str, script: str) -> dict:
    """
    Generate three viral YouTube title options using the LLM.

    Parameters
    ----------
    topic  : Video topic
    script : Generated narration script

    Returns
    -------
    dict with keys:
        viral_curiosity : Curiosity-gap / clickbait title (with emoji)
        high_stakes     : High-drama title (partial CAPS)
        seo_optimized   : SEO keyword-rich title
    """
    default_titles = {
        "viral_curiosity": f"Isso Sobre {topic} Vai Te Chocar! 😱",
        "high_stakes": f"O SEGREDO PROIBIDO DE {topic.upper()} REVELADO!",
        "seo_optimized": f"{topic} - Mistério, História e Lendas | Rota Calculada",
    }

    prompt = (
        f"Crie 3 títulos virais em português brasileiro para um Short do YouTube "
        f"sobre o tema: {topic}.\n"
        f"Roteiro resumido: {script[:200]}\n\n"
        f"Retorne EXATAMENTE um JSON válido (sem texto extra) com as chaves:\n"
        f"  viral_curiosity  (gera curiosidade extrema, use emoji)\n"
        f"  high_stakes      (alto impacto emocional, CAPS parcial)\n"
        f"  seo_optimized    (SEO com palavras-chave relevantes)\n"
        f"Máximo 80 caracteres por título."
    )

    raw: Optional[str] = None
    gemini_key = _get_gemini_key()
    openai_key = _get_openai_key()

    if gemini_key:
        raw = _call_gemini(prompt, gemini_key)
    if not raw and openai_key:
        raw = _call_openai(prompt, openai_key)

    if not raw:
        return default_titles

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:])
        if clean.endswith("```"):
            clean = "\n".join(clean.split("\n")[:-1])
        data = json.loads(clean.strip())
        return {
            "viral_curiosity": str(data.get("viral_curiosity", default_titles["viral_curiosity"])),
            "high_stakes": str(data.get("high_stakes", default_titles["high_stakes"])),
            "seo_optimized": str(data.get("seo_optimized", default_titles["seo_optimized"])),
        }
    except Exception as exc:
        logger.warning(f"[LLM] Falha ao parsear JSON de títulos: {exc}. Usando padrao.")
        return default_titles
