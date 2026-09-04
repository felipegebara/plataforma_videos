"""
core/series_builder.py
======================
Módulo para criação automática de Séries de Shorts a partir de pastas de mídia.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.db import db

logger = logging.getLogger("core.series_builder")


def build_series_from_folder(
    folder_path: str,
    series_name: str,
    max_shorts: int = 10,
    voice_name: str = "pt-BR-AntonioNeural",
    format_type: str = "short"
) -> Dict[str, Any]:
    """
    Escaneia uma pasta contendo arquivos de vídeo (.mp4), agrupa os mídias
    e cria uma série de jobs na fila para produção automática de N Shorts.
    """
    p = Path(folder_path)
    if not p.exists() or not p.is_dir():
        raise ValueError(f"Diretório não encontrado: {folder_path}")

    video_files = list(p.glob("*.mp4")) + list(p.glob("*.mov")) + list(p.glob("*.avi"))
    if not video_files:
        raise ValueError(f"Nenhum arquivo de vídeo encontrado na pasta: {folder_path}")

    # Cria ID da série
    series_id = f"series_{uuid.uuid4().hex[:8]}"

    # Agrupa vídeos (máximo max_shorts)
    video_files = video_files[:max_shorts]
    created_jobs = []

    for idx, vid in enumerate(video_files, start=1):
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        topic_name = f"{series_name} — Episódio {idx}: {vid.stem.replace('_', ' ').title()}"
        
        raw_media = str(vid)
        
        # Insere job no DB com a flag da série
        db.create_job(
            job_id=job_id,
            topic=topic_name,
            format_type=format_type,
            raw_media_dir=folder_path,
            voice_name=voice_name
        )
        
        created_jobs.append({
            "job_id": job_id,
            "episode": idx,
            "topic": topic_name,
            "video_path": raw_media,
            "status": "PENDING"
        })

    logger.info(f"Série '{series_name}' criada com {len(created_jobs)} episódios. ID: {series_id}")

    return {
        "series_id": series_id,
        "series_name": series_name,
        "total_episodes": len(created_jobs),
        "jobs": created_jobs
    }


def get_series_status(job_ids: List[str]) -> Dict[str, Any]:
    """Retorna o status consolidado de uma série de jobs."""
    statuses = []
    completed_count = 0

    for jid in job_ids:
        job = db.get_job(jid)
        if job:
            st = job.get("status", "UNKNOWN")
            statuses.append({
                "job_id": jid,
                "topic": job.get("topic"),
                "status": st,
                "progress": job.get("progress", 0),
                "output_video": job.get("output_video")
            })
            if st == "COMPLETED":
                completed_count += 1

    total = len(job_ids)
    progress_percent = int((completed_count / total * 100)) if total > 0 else 0

    return {
        "total_jobs": total,
        "completed_jobs": completed_count,
        "overall_progress": progress_percent,
        "jobs": statuses
    }
