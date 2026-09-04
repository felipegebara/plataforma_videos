# -*- coding: utf-8 -*-
"""
core/subtitles.py
=================
Dynamic subtitle engine for Rota Calculada AI Video Studio PRO.

Provides CapCut-style animated word-level subtitles burnt directly onto video.
Uses openai-whisper for transcription with a simple fallback if not installed.
"""

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip, VideoFileClip

logger = logging.getLogger("core.subtitles")

# -----------------------------------------------------------------------
# Optional Whisper import
# -----------------------------------------------------------------------
try:
    import whisper as _whisper
    WHISPER_AVAILABLE = True
    logger.info("[Subtitles] openai-whisper disponivel.")
except ImportError:
    _whisper = None  # type: ignore
    WHISPER_AVAILABLE = False
    logger.warning("[Subtitles] openai-whisper nao instalado. Usando fallback de palavras uniformes.")


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try bold system font, fall back to PIL default."""
    for fname in ("arialbd.ttf", "Arial_Bold.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"):
        try:
            return ImageFont.truetype(fname, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _transcribe_with_whisper(audio_path: str) -> List[dict]:
    """
    Transcribe audio with Whisper tiny model.

    Returns
    -------
    list of {word: str, start: float, end: float}
    """
    model = _whisper.load_model("tiny")
    result = model.transcribe(audio_path, word_timestamps=True, language="pt")
    words: List[dict] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            words.append({
                "word": w["word"].strip(),
                "start": float(w["start"]),
                "end": float(w["end"]),
            })
    return words


def _fallback_word_timing(audio_path: str, video_duration: float) -> List[dict]:
    """Distribute placeholder words evenly across audio duration (no Whisper fallback)."""
    try:
        from moviepy import AudioFileClip
        ac = AudioFileClip(audio_path)
        duration = ac.duration
        ac.close()
    except Exception:
        duration = video_duration
    placeholder = ["[sem", "transcricao", "disponivel", "instale", "whisper]"]
    slot = duration / max(len(placeholder), 1)
    return [{"word": w, "start": i * slot, "end": (i + 1) * slot} for i, w in enumerate(placeholder)]


def generate_subtitle_clips(
    words_with_times: List[dict],
    w: int,
    h: int,
    font_size: int = 72,
    group_size: int = 3,
) -> List[ImageClip]:
    """
    Generate CapCut-style animated subtitle ImageClip list.

    Each group of `group_size` words is shown simultaneously. The active word
    is rendered in bright white; the others appear in bold yellow. All words
    have a black outline stroke for legibility on any background.

    Parameters
    ----------
    words_with_times : list of {word, start, end} dicts
    w, h             : video dimensions in pixels
    font_size        : base font size (default 72 for 1080-wide video)
    group_size       : number of words shown simultaneously (default 3)

    Returns
    -------
    list of ImageClip
    """
    if not words_with_times:
        return []

    font = _load_font(font_size)
    clips: List[ImageClip] = []

    for g_start in range(0, len(words_with_times), group_size):
        group = words_with_times[g_start: g_start + group_size]
        if not group:
            continue

        def _render(active_idx: int, grp=group):
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            texts = [wd["word"] for wd in grp]
            gap = 14
            bboxes, total_w_px = [], 0
            for txt in texts:
                bb = draw.textbbox((0, 0), txt, font=font)
                bw, bh = bb[2] - bb[0], bb[3] - bb[1]
                bboxes.append((bw, bh))
                total_w_px += bw + gap
            total_w_px -= gap
            x = (w - total_w_px) // 2
            y = int(h * 0.82)
            for i, (txt, (bw, _bh)) in enumerate(zip(texts, bboxes)):
                col = (255, 255, 255) if i == active_idx else (255, 215, 0)
                draw.text((x, y), txt, font=font, fill=col, stroke_width=4, stroke_fill=(0, 0, 0))
                x += bw + gap
            rgb = np.array(img.convert("RGB"))
            alpha = np.array(img.split()[-1])
            return rgb, alpha

        for rel_idx, wi in enumerate(group):
            dur = max(0.05, wi["end"] - wi["start"])
            rgb_arr, alpha_arr = _render(rel_idx)
            sc = ImageClip(rgb_arr).with_start(wi["start"]).with_duration(dur)
            mc = ImageClip(alpha_arr, is_mask=True).with_start(wi["start"]).with_duration(dur)
            clips.append(sc.with_mask(mc))

    return clips


def burn_subtitles(
    video_path: str,
    audio_path: str,
    output_path: str,
    style: str = "capcut",
) -> str:
    """
    Transcribe audio and burn animated word-level subtitles onto the video.

    Parameters
    ----------
    video_path  : Path to source video (.mp4)
    audio_path  : Path to narration audio (.mp3 / .wav)
    output_path : Destination path for the output video
    style       : Subtitle style preset ('capcut')

    Returns
    -------
    str - output_path
    """
    logger.info(f"[Subtitles] burn_subtitles -> {output_path}")
    video = VideoFileClip(video_path)
    w, h, video_dur = video.w, video.h, video.duration

    if WHISPER_AVAILABLE:
        try:
            words = _transcribe_with_whisper(audio_path)
        except Exception as exc:
            logger.warning(f"[Subtitles] Whisper falhou: {exc}. Usando fallback.")
            words = _fallback_word_timing(audio_path, video_dur)
    else:
        words = _fallback_word_timing(audio_path, video_dur)

    def _export_plain():
        video.write_videofile(output_path, codec="libx264", audio_codec="aac",
                              preset="fast", fps=24, logger=None)
        video.close()

    if not words:
        _export_plain()
        return output_path

    font_size = 68 if w <= 1080 else 88
    sub_clips = generate_subtitle_clips(words, w, h, font_size=font_size)

    if not sub_clips:
        _export_plain()
        return output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final = CompositeVideoClip([video] + sub_clips).with_duration(video_dur)
    final.write_videofile(
        output_path, codec="libx264", audio_codec="aac",
        preset="fast", threads=4, fps=24, logger=None
    )
    final.close()
    video.close()
    for sc in sub_clips:
        sc.close()

    logger.info(f"[Subtitles] Concluido: {output_path}")
    return output_path
