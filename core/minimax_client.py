"""
core/minimax_client.py
======================
Cliente de integração com a API MiniMax para síntese de voz ultra-realista (T2A / Speech-01)
e geração de vídeos I2V/T2V (Hailuo / Video-01).
"""
import os
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any

from core.config import Config

logger = logging.getLogger("core.minimax")


def get_minimax_credentials() -> Dict[str, Optional[str]]:
    """Retorna a chave de API e o Group ID do MiniMax."""
    api_key = Config.MINIMAX_API_KEY() or os.environ.get("MINIMAX_API_KEY")
    group_id = Config.MINIMAX_GROUP_ID() or os.environ.get("MINIMAX_GROUP_ID")
    return {"api_key": api_key, "group_id": group_id}


def synthesize_speech_minimax(
    text: str,
    output_audio_path: str,
    voice_id: str = "male-qn-qingse",
    speed: float = 1.0,
    vol: float = 1.0,
    model: str = "speech-01-hd"
) -> Optional[str]:
    """
    Sintetiza voz de alta qualidade usando a API MiniMax T2A (Text-to-Audio).

    Args:
        text: Texto para narração.
        output_audio_path: Caminho do arquivo .mp3 ou .wav de saída.
        voice_id: ID da voz MiniMax (ex: male-qn-qingse, female-shaonv, presenter_male, etc).
        speed: Velocidade da fala (0.5 a 2.0).
        vol: Volume (0.1 a 10.0).
        model: Modelo de voz MiniMax (speech-01-hd, speech-01, t2a_v2).

    Returns:
        Caminho do arquivo gerado se bem sucedido, None caso contrário.
    """
    creds = get_minimax_credentials()
    api_key = creds["api_key"]
    group_id = creds["group_id"]

    if not api_key:
        logger.debug("[MiniMax TTS] MINIMAX_API_KEY não encontrada no .env ou ambiente.")
        return None

    out_p = Path(output_audio_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://api.minimax.chat/v1/t2a_v2"
    if group_id:
        url += f"?GroupId={group_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "format": "mp3",
            "channel": 1
        }
    }

    try:
        logger.info(f"[MiniMax TTS] Enviando requisição de áudio ({len(text)} caracteres)...")
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

            base_resp = data.get("base_resp", {})
            if base_resp.get("status_code", 0) != 0:
                msg = base_resp.get("status_msg", "Erro desconhecido")
                logger.error(f"[MiniMax TTS] Erro da API: {msg} (code {base_resp.get('status_code')})")
                return None

            audio_hex = data.get("audio_file")
            if not audio_hex:
                logger.error("[MiniMax TTS] Resposta da API não contém 'audio_file'.")
                return None

            # MiniMax envia o áudio em formato hexadecimal string
            audio_bytes = bytes.fromhex(audio_hex)
            with open(out_p, "wb") as f:
                f.write(audio_bytes)

            if out_p.exists() and out_p.stat().st_size > 1000:
                logger.info(f"[MiniMax TTS] Áudio salvo com sucesso ({round(out_p.stat().st_size/1024, 1)} KB): {out_p.name}")
                return str(out_p)

    except Exception as err:
        logger.error(f"[MiniMax TTS] Erro na requisição T2A: {err}")

    return None
