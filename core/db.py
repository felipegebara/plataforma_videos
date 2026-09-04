import os
import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger("core.db")

class Database:
    """Gerenciador de Banco de Dados SQLite embutido para persistência de Jobs e Vídeos."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            if os.environ.get("VERCEL"):
                self.db_path = Path("/tmp/rotacalculada.sqlite3")
            else:
                try:
                    base_dir = Path(__file__).resolve().parents[1]
                    data_dir = base_dir / "output" / "data"
                    data_dir.mkdir(parents=True, exist_ok=True)
                    self.db_path = data_dir / "rotacalculada.sqlite3"
                except Exception:
                    self.db_path = Path("/tmp/rotacalculada.sqlite3")
        else:
            self.db_path = Path(db_path)
            try:
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    category TEXT DEFAULT 'MISTERY_HISTORY',
                    format_type TEXT DEFAULT 'short',
                    voice_name TEXT DEFAULT 'pt-BR-AntonioNeural',
                    status TEXT DEFAULT 'PENDING',
                    progress INTEGER DEFAULT 0,
                    current_step TEXT DEFAULT 'Iniciando',
                    video_path TEXT,
                    thumbnail_path TEXT,
                    titles_json TEXT,
                    selected_title TEXT,
                    description TEXT,
                    hashtags_json TEXT,
                    metadata_json TEXT,
                    error_message TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()
            logger.info(f"[Database] Banco SQLite pronto em: {self.db_path}")

    def create_job(self, job_id: str, topic: str, category: str = "MISTERY_HISTORY", format_type: str = "short", voice_name: str = "pt-BR-AntonioNeural", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (
                    job_id, topic, category, format_type, voice_name,
                    status, progress, current_step, metadata_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'PENDING', 0, 'Criado na fila', ?, ?, ?)
            """, (
                job_id, topic, category, format_type, voice_name,
                json.dumps(metadata or {}, ensure_ascii=False),
                now, now
            ))
            conn.commit()
        return self.get_job(job_id)

    def update_job_progress(self, job_id: str, progress: int, current_step: str, status: str = "PROCESSING"):
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs SET
                    progress = ?,
                    current_step = ?,
                    status = ?,
                    updated_at = ?
                WHERE job_id = ?
            """, (progress, current_step, status, now, job_id))
            conn.commit()

    def complete_job(
        self,
        job_id: str,
        video_path: str,
        thumbnail_path: str,
        titles: Dict[str, str],
        selected_title: str,
        description: str,
        hashtags: List[str]
    ):
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs SET
                    status = 'COMPLETED',
                    progress = 100,
                    current_step = 'Concluído com sucesso! 🎉',
                    video_path = ?,
                    thumbnail_path = ?,
                    titles_json = ?,
                    selected_title = ?,
                    description = ?,
                    hashtags_json = ?,
                    updated_at = ?
                WHERE job_id = ?
            """, (
                video_path,
                thumbnail_path,
                json.dumps(titles, ensure_ascii=False),
                selected_title,
                description,
                json.dumps(hashtags, ensure_ascii=False),
                now,
                job_id
            ))
            conn.commit()

    def fail_job(self, job_id: str, error_message: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs SET
                    status = 'FAILED',
                    error_message = ?,
                    current_step = 'Falha no processamento',
                    updated_at = ?
                WHERE job_id = ?
            """, (error_message, now, job_id))
            conn.commit()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["titles"] = json.loads(d["titles_json"]) if d.get("titles_json") else {}
        d["hashtags"] = json.loads(d["hashtags_json"]) if d.get("hashtags_json") else []
        d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
        return d

# Instância global padrão
db = Database()
