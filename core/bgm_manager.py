# -*- coding: utf-8 -*-
"""
core/bgm_manager.py
===================
Background Music (BGM) manager for Rota Calculada AI Video Studio PRO.

Provides smart category-based BGM selection from the output/audio/ directory.
Falls back gracefully through: category-specific file -> default file ->
any .wav -> any .mp3 -> None.

Does NOT perform downloads — see download_bgm_pack.py at project root for that.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("core.bgm_manager")

# -----------------------------------------------------------------------
# Category → filename mapping
# -----------------------------------------------------------------------

CATEGORY_BGM_MAP: dict = {
    "MISTERY_HISTORY":  "bgm_mystery.wav",
    "LEGENDS_FOLKLORE": "bgm_legends.wav",
    "TRAVEL_TOURISM":   "bgm_travel.wav",
    "ACTION_DRAMA":     "bgm_action.wav",
}

_DEFAULT_BGM = "bgm_tuneis_secretos_do_pelourinho.wav"

# Tags that identify voice/sfx production files (excluded from BGM listing)
_EXCLUDE_TAGS = ("voice_", "sfx_", "temp_", "_temp", "job_voice", "job_sfx")


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def get_bgm_for_category(
    category: str,
    project_root: Path,
) -> Optional[Path]:
    """
    Return the Path to the best-matching BGM file for the given category.

    Resolution order
    ----------------
    1. Category-specific file (e.g. bgm_mystery.wav for MISTERY_HISTORY)
    2. Default file (bgm_tuneis_secretos_do_pelourinho.wav)
    3. Any .wav file in output/audio/
    4. Any .mp3 file in output/audio/
    5. None

    Parameters
    ----------
    category     : Content category string (e.g. 'MISTERY_HISTORY')
    project_root : Absolute Path to the project root directory

    Returns
    -------
    Path or None
    """
    audio_dir = project_root / "output" / "audio"

    if not audio_dir.exists():
        logger.warning(f"[BGM] Diretório de áudio nao encontrado: {audio_dir}")
        return None

    # 1. Category-specific match
    preferred_name = CATEGORY_BGM_MAP.get(category.upper().strip())
    if preferred_name:
        preferred_path = audio_dir / preferred_name
        if preferred_path.exists():
            logger.info(f"[BGM] Usando BGM especifico da categoria: {preferred_path.name}")
            return preferred_path

    # 2. Default track
    default_path = audio_dir / _DEFAULT_BGM
    if default_path.exists():
        logger.info(f"[BGM] Usando BGM padrao: {default_path.name}")
        return default_path

    # 3. Any .wav
    wav_files = sorted(
        f for f in audio_dir.glob("*.wav")
        if not any(tag in f.name for tag in _EXCLUDE_TAGS)
    )
    if wav_files:
        logger.info(f"[BGM] Fallback .wav: {wav_files[0].name}")
        return wav_files[0]

    # 4. Any .mp3 (last resort)
    mp3_files = sorted(
        f for f in audio_dir.glob("*.mp3")
        if not any(tag in f.name for tag in _EXCLUDE_TAGS)
    )
    if mp3_files:
        logger.info(f"[BGM] Fallback .mp3: {mp3_files[0].name}")
        return mp3_files[0]

    logger.warning("[BGM] Nenhum arquivo BGM encontrado em output/audio/")
    return None


def list_available_bgm(project_root: Path) -> list:
    """
    Return all available BGM tracks in output/audio/ as metadata dicts.

    Each dict contains:
        name     : filename (str)
        path     : absolute path string
        category : matched category label or 'GENERAL'
        size_mb  : file size in MB (float)

    Parameters
    ----------
    project_root : Absolute Path to the project root directory

    Returns
    -------
    list of dicts (empty if directory missing or no BGM files found)
    """
    audio_dir = project_root / "output" / "audio"
    if not audio_dir.exists():
        return []

    # Reverse map: filename -> category label
    _reverse = {v: k for k, v in CATEGORY_BGM_MAP.items()}
    _reverse[_DEFAULT_BGM] = "MISTERY_HISTORY"

    results = []
    for ext in ("*.wav", "*.mp3"):
        for f in sorted(audio_dir.glob(ext)):
            if any(tag in f.name for tag in _EXCLUDE_TAGS):
                continue
            results.append({
                "name": f.name,
                "path": str(f),
                "category": _reverse.get(f.name, "GENERAL"),
                "size_mb": round(f.stat().st_size / 1_048_576, 2),
            })

    logger.info(f"[BGM] {len(results)} faixa(s) BGM disponivel(is).")
    return results
