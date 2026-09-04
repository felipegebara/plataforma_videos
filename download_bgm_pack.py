# -*- coding: utf-8 -*-
"""
download_bgm_pack.py
====================
Downloads 4 royalty-free background music tracks from Internet Archive
public domain sources and saves them to output/audio/ with canonical names.

Usage
-----
    python download_bgm_pack.py

Tracks
------
bgm_mystery.wav   - Epic/mystery background music (mystery/history videos)
bgm_legends.wav   - Ethereal/folklore ambient music (legends/folklore videos)
bgm_travel.wav    - Adventure/travel music (travel/tourism videos)
bgm_action.wav    - Dramatic/action music (action/drama videos)
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("download_bgm_pack")

# Project root is the directory containing this script
PROJECT_ROOT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT_ROOT / "output" / "audio"

# -----------------------------------------------------------------------
# Download targets — all sourced from archive.org public domain
# -----------------------------------------------------------------------

BGM_TRACKS = [
    {
        "name": "bgm_mystery.wav",
        "description": "Epic Mystery / History — dark orchestral ambient",
        "urls": [
            # Primary: Kevin MacLeod - Cipher (public domain, archive.org)
            "https://archive.org/download/kevin-macleod-incompetech/Kevin%20MacLeod%20-%20Cipher.mp3",
            # Fallback: generic epic ambient from archive.org
            "https://archive.org/download/free-music-archive-sampler-001_201410/01-Kevin_MacLeod-Cut_and_Run.mp3",
        ],
    },
    {
        "name": "bgm_legends.wav",
        "description": "Ethereal Folklore / Legends — mystic Celtic ambient",
        "urls": [
            # Kevin MacLeod - Feather (public domain)
            "https://archive.org/download/kevin-macleod-incompetech/Kevin%20MacLeod%20-%20Feather.mp3",
            # Fallback
            "https://archive.org/download/free-music-archive-sampler-001_201410/02-Podington_Bear-Shimmering.mp3",
        ],
    },
    {
        "name": "bgm_travel.wav",
        "description": "Adventure / Travel — uplifting orchestral",
        "urls": [
            # Kevin MacLeod - Adventure Meme (public domain)
            "https://archive.org/download/kevin-macleod-incompetech/Kevin%20MacLeod%20-%20Adventure%20Meme.mp3",
            # Fallback
            "https://archive.org/download/free-music-archive-sampler-001_201410/03-Podington_Bear-Float.mp3",
        ],
    },
    {
        "name": "bgm_action.wav",
        "description": "Dramatic Action — intense cinematic percussion",
        "urls": [
            # Kevin MacLeod - Impact Moderato (public domain)
            "https://archive.org/download/kevin-macleod-incompetech/Kevin%20MacLeod%20-%20Impact%20Moderato.mp3",
            # Fallback
            "https://archive.org/download/free-music-archive-sampler-001_201410/04-Podington_Bear-Twinkle.mp3",
        ],
    },
]

# -----------------------------------------------------------------------
# Download helpers
# -----------------------------------------------------------------------

def _download_with_urllib(url: str, dest: Path) -> bool:
    """Download a URL to dest using stdlib urllib (no extra deps)."""
    import urllib.request
    import urllib.error
    try:
        logger.info(f"  Tentando: {url}")
        headers = {"User-Agent": "Mozilla/5.0 (compatible; RotaCalculadaBGM/1.0)"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        dest.write_bytes(data)
        size_kb = dest.stat().st_size / 1024
        logger.info(f"  OK ({size_kb:.1f} KB)")
        return True
    except Exception as exc:
        logger.warning(f"  Falhou: {exc}")
        return False


def _try_download(track: dict) -> bool:
    """Try each URL in the track's url list; return True on first success."""
    name = track["name"]
    dest = AUDIO_DIR / name

    if dest.exists() and dest.stat().st_size > 10_000:
        logger.info(f"[BGM] {name} ja existe ({dest.stat().st_size // 1024} KB). Pulando.")
        return True

    tmp_mp3 = AUDIO_DIR / (name.replace(".wav", "_dl_tmp.mp3"))

    for url in track["urls"]:
        if _download_with_urllib(url, tmp_mp3):
            break
    else:
        logger.error(f"[BGM] Todas as URLs falharam para {name}")
        return False

    # Convert mp3 -> wav via moviepy/ffmpeg if available, else keep as mp3
    try:
        from moviepy import AudioFileClip
        logger.info(f"  Convertendo MP3 -> WAV: {name}")
        ac = AudioFileClip(str(tmp_mp3))
        ac.write_audiofile(str(dest), codec="pcm_s16le", logger=None)
        ac.close()
        tmp_mp3.unlink(missing_ok=True)
        logger.info(f"  Convertido: {dest.name}")
    except Exception as exc:
        # Keep as mp3, rename with .wav extension so BGM manager finds it
        logger.warning(f"  Conversao falhou ({exc}). Mantendo como mp3 renomeado.")
        tmp_mp3.rename(dest)

    return dest.exists()


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"[BGM] Destino: {AUDIO_DIR}")
    logger.info(f"[BGM] Baixando {len(BGM_TRACKS)} faixa(s)...\n")

    success_count = 0
    for track in BGM_TRACKS:
        logger.info(f"[BGM] {track['name']} — {track['description']}")
        if _try_download(track):
            success_count += 1
        print()

    logger.info(f"[BGM] Concluido: {success_count}/{len(BGM_TRACKS)} faixas baixadas.")
    if success_count < len(BGM_TRACKS):
        logger.warning(
            "[BGM] Algumas faixas falharam. "
            "O motor usara bgm_tuneis_secretos_do_pelourinho.wav como fallback."
        )


if __name__ == "__main__":
    main()
