import os
import sys
import time
import asyncio
import logging
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import Optional, List, Tuple
import edge_tts
from gtts import gTTS

logger = logging.getLogger("core.resilience")

def ensure_ffmpeg_configured():
    """Garante que o FFmpeg esteja disponível através do imageio-ffmpeg sem exigir configuração de PATH."""
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and Path(ffmpeg_exe).exists():
            os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_exe)
            # Adiciona ao início do PATH se necessário
            ffmpeg_dir = str(Path(ffmpeg_exe).parent)
            if ffmpeg_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"[FFmpeg] Configurado estaticamente via imageio: {ffmpeg_exe}")
            return ffmpeg_exe
    except Exception as e:
        logger.warning(f"[FFmpeg] Falha ao configurar imageio-ffmpeg: {e}")
    return "ffmpeg"


async def resilient_edge_tts(
    text: str,
    output_audio_path: str,
    voice: str = "pt-BR-AntonioNeural",
    rate: str = "-1%",
    max_retries: int = 5
) -> str:
    """
    Síntese de voz neural resiliente. Suporta MiniMax TTS, Edge-TTS e fallback gTTS.
    """
    out_p = Path(output_audio_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if out_p.exists() and out_p.stat().st_size > 1000:
        return str(out_p)

    # 1. Tenta MiniMax TTS se chave estender no ambiente ou se a voz for MiniMax
    if os.environ.get("MINIMAX_API_KEY") or voice.startswith("minimax") or "male-qn-" in voice:
        try:
            import core.minimax_client as _minimax
            mm_voice = "male-qn-qingse"
            if "female" in voice:
                mm_voice = "female-shaonv"
            mm_res = _minimax.synthesize_speech_minimax(text, str(out_p), voice_id=mm_voice)
            if mm_res and Path(mm_res).exists() and Path(mm_res).stat().st_size > 1000:
                logger.info("[TTS] Voz gerada com sucesso via MiniMax T2A!")
                return str(out_p)
        except Exception as mmerr:
            logger.warning(f"[TTS] MiniMax TTS falhou ({mmerr}). Tentando Edge-TTS...")

    # 2. Edge-TTS (Padrão)
    delay = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(str(out_p))
            if out_p.exists() and out_p.stat().st_size > 1000:
                logger.info(f"[TTS] Voz gerada com sucesso via Edge-TTS (Tentativa {attempt})")
                return str(out_p)
        except Exception as err:
            logger.warning(f"[TTS] Tentativa {attempt}/{max_retries} falhou ({err}). Aguardando {delay:.1f}s...")
            await asyncio.sleep(delay)
            delay *= 1.8

    # Fallback automático para gTTS
    try:
        logger.info("[TTS] Executando Fallback para gTTS...")
        loop = asyncio.get_event_loop()
        def _gtts_task():
            tts = gTTS(text=text, lang="pt", tld="com.br")
            tts.save(str(out_p))
        await loop.run_in_executor(None, _gtts_task)
        if out_p.exists() and out_p.stat().st_size > 1000:
            return str(out_p)
    except Exception as gerr:
        logger.error(f"[TTS] Falha total no TTS (Edge e gTTS): {gerr}")
        raise RuntimeError(f"Falha na síntese de voz: {gerr}")

    return str(out_p)


def resilient_search_and_download_image(
    query: str,
    output_path: Path,
    user_agent: str = "RotaCalculadaBot/2.0 (contact@rotacalculada.com)"
) -> Optional[Path]:
    """
    Busca e baixa ilustrações em alta resolução da Wikipedia/Wikimedia
    com cabeçalhos adequados e prevenção contra Rate-Limiting (HTTP 429).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 5000:
        return output_path

    url = (
        f"https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search"
        f"&gsrnamespace=0&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3&prop=pageimages&pithumbsize=1200"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                src = pdata.get("thumbnail", {}).get("source")
                if src:
                    d_req = urllib.request.Request(src, headers={"User-Agent": user_agent})
                    with urllib.request.urlopen(d_req, timeout=12) as d_resp, open(output_path, "wb") as out_f:
                        out_f.write(d_resp.read())
                    if output_path.exists() and output_path.stat().st_size > 5000:
                        logger.info(f"[WebImage] Imagem baixada com sucesso para '{query}': {output_path.name}")
                        return output_path
    except Exception as err:
        logger.warning(f"[WebImage] Erro ao buscar imagem para '{query}': {err}")

    return None
