import os
import sys
import uuid
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.db import db
from core.broker import get_broker
from core.engine import process_video_job
from core.resilience import ensure_ffmpeg_configured
from core.config import Config
from core.voice_profiles import list_voices
from core.trends import get_trending_topics_brazil, suggest_next_video
from core.series_builder import build_series_from_folder, get_series_status
from core.youtube_uploader import upload_to_youtube

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api.server")
ensure_ffmpeg_configured()

app = FastAPI(
    title="Rota Calculada AI Chat Studio",
    description="Interface Conversacional Inteligente para Produção de Vídeos, Shorts e Empacotamento Viral",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
output_dir = project_root / "output"
upload_dir = output_dir / "uploads"
ui_dir = project_root / "ui"

try:
    upload_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)
except Exception as _dir_err:
    logger.warning(f"Diretórios não puderam ser criados (ambiente Vercel Serverless): {_dir_err}")


class ChatRequest(BaseModel):
    message: str
    media_path: Optional[str] = None
    use_web_images: bool = True
    format_type: Optional[str] = "auto"
    voice_name: Optional[str] = "pt-BR-AntonioNeural"


def parse_chat_intent(prompt: str) -> Dict[str, Any]:
    """Analisa o prompt em linguagem natural do usuário para extrair formato, tema e estilo."""
    p_lower = prompt.lower()

    # Detecta formato
    if "short" in p_lower or "vertical" in p_lower or "reels" in p_lower or "tiktok" in p_lower:
        fmt = "short"
    elif "longo" in p_lower or "documentario" in p_lower or "documentário" in p_lower or "horizontal" in p_lower:
        fmt = "long"
    else:
        fmt = "short"

    # Detecta estilo
    if any(k in p_lower for k in ["lenda", "mito", "mitologia", "folclore", "arabia", "arábia", "aladim", "sinbad"]):
        category = "LEGENDS_FOLKLORE"
    elif any(k in p_lower for k in ["historia", "história", "segredo", "antigo", "ouro", "tunel", "túnel", "guerra"]):
        category = "MISTERY_HISTORY"
    elif any(k in p_lower for k in ["trem", "parque", "legoland", "viagem", "turismo", "guia", "visita"]):
        category = "TRAVEL_TOURISM"
    else:
        category = "MISTERY_HISTORY"

    # Extrai o tema
    topic = prompt.strip()
    for prefix in ["monte um video", "monte um vídeo", "crie um video", "crie um vídeo", "monte shorts", "crie shorts", "faça um video", "gere um video"]:
        if p_lower.startswith(prefix):
            topic = prompt[len(prefix):].strip(" :,.-")
            break

    if len(topic) < 3:
        topic = "Aventuras e Mistérios pelo Mundo"

    return {
        "format_type": fmt,
        "category": category,
        "topic": topic
    }


def resolve_media_files(media_path_input: Optional[str]) -> List[str]:
    """Resolve caminhos de arquivos ou diretórios passados pelo usuário."""
    if not media_path_input or not media_path_input.strip():
        return []

    p = Path(media_path_input.strip().strip('"').strip("'"))
    if not p.is_absolute():
        p = project_root / p

    if p.is_file():
        return [str(p)]
    elif p.is_dir():
        vids = []
        for ext in ["*.mp4", "*.mov", "*.avi", "*.mkv"]:
            vids.extend(list(p.glob(ext)))
        return [str(v) for v in sorted(vids)]
    return []


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "Rota Calculada AI Chat Studio",
        "version": "2.1.0",
        "database": str(db.db_path)
    }


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job


@app.post("/api/chat")
async def chat_interaction(request: ChatRequest, background_tasks: BackgroundTasks):
    """Processa a mensagem conversacional do usuário e inicia a criação do vídeo."""
    intent = parse_chat_intent(request.message)

    fmt = request.format_type if request.format_type and request.format_type != "auto" else intent["format_type"]
    category = intent["category"]
    topic = intent["topic"]

    # Resolve arquivos de mídia
    resolved_clips = resolve_media_files(request.media_path)
    
    # Se nenhum caminho for informado, busca automaticamente nos diretórios conhecidos
    if not resolved_clips:
        if "arabia" in request.message.lower():
            resolved_clips = [str(f) for f in (project_root / "arabia").glob("*.mp4")]
        elif "legoland" in request.message.lower():
            resolved_clips = [str(f) for f in (project_root / "output" / "legoland").glob("*.mp4")]

    job_id = f"chat_{uuid.uuid4().hex[:8]}"

    msg_lower = request.message.lower().strip()
    is_explicit_script = any(msg_lower.startswith(prefix) for prefix in ["roteiro:", "script:", "narração:", "narracao:"])
    
    metadata = {
        "raw_video_files": resolved_clips,
        "use_web_images": request.use_web_images,
        "user_prompt": request.message,
        "custom_script": request.message if is_explicit_script else None
    }

    job_entry = db.create_job(
        job_id=job_id,
        topic=topic,
        category=category,
        format_type=fmt,
        voice_name=request.voice_name or "pt-BR-AntonioNeural",
        metadata=metadata
    )

    # Inicia a renderização em background
    background_tasks.add_task(process_video_job, job_id)

    assistant_reply = (
        f"🎬 **Entendido!** Iniciei a produção do seu vídeo com base nas suas instruções:\n\n"
        f"• **Tema**: {topic}\n"
        f"• **Formato**: {'⚡ Short (9:16 Vertical)' if fmt == 'short' else '📜 Vídeo Longo (16:9 Horizontal)'}\n"
        f"• **Estilo**: {category}\n"
        f"• **Imagens da Web**: {'✓ Ativadas (com efeito Ken Burns)' if request.use_web_images else 'Desativadas'}\n"
        f"• **Vídeos Brutos**: {len(resolved_clips)} arquivos carregados\n\n"
        f"Estou gerando o roteiro, narrando com voz neural e preparando o pacote viral..."
    )

    return {
        "job_id": job_id,
        "assistant_reply": assistant_reply,
        "intent": intent,
        "media_count": len(resolved_clips),
        "job": job_entry
    }


@app.get("/api/media/{category_folder}/{filename}")
async def serve_media(category_folder: str, filename: str):
    """Serve arquivos de mídia com segurança."""
    base_search = output_dir if category_folder not in ["arabia"] else project_root / category_folder
    matches = list(base_search.rglob(filename))
    if not matches:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    media_path = matches[0]
    media_type = "video/mp4" if filename.endswith(".mp4") else ("image/png" if filename.endswith(".png") else "application/octet-stream")
    return FileResponse(str(media_path), media_type=media_type)


@app.post("/api/upload")
async def upload_video_files(files: List[UploadFile] = File(...)):
    """Recebe arquivos de vídeo enviados pelo navegador e armazena no diretório de uploads."""
    target_dir = Path("/tmp/uploads") if os.environ.get("VERCEL") else upload_dir
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    saved_files = []
    for file in files:
        file_path = target_dir / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        saved_files.append(str(file_path))

    logger.info(f"[Upload] {len(saved_files)} arquivo(s) salvos em {target_dir}")
    return {
        "status": "success",
        "message": f"{len(saved_files)} arquivo(s) de vídeo enviado(s) com sucesso!",
        "folder_path": str(target_dir),
        "files": saved_files
    }


@app.get("/api/settings/status")
async def get_settings_status():
    """Retorna o status de configuracao das chaves de API."""
    return Config.status()


@app.get("/api/voices")
async def get_voices():
    """Retorna a lista de vozes neurais disponiveis."""
    return list_voices()


@app.get("/api/trends")
async def get_trends(max_results: int = 10, category: str = "travel"):
    """Retorna sugestoes de trending topics (Viagens, História, Geral)."""
    return get_trending_topics_brazil(max_results=max_results, category_filter=category)


@app.get("/api/jobs")
async def list_all_jobs(limit: int = 50):
    """Retorna a lista de todos os jobs criados no sistema."""
    all_jobs = db.list_jobs(limit=limit)
    return {"jobs": all_jobs}


class SeriesRequest(BaseModel):
    folder_path: str
    series_name: str
    max_shorts: Optional[int] = 10
    voice_name: Optional[str] = "pt-BR-AntonioNeural"
    format_type: Optional[str] = "short"


@app.post("/api/series/create")
async def create_series(req: SeriesRequest, background_tasks: BackgroundTasks):
    """Cria e dispara uma serie automatica de N shorts a partir de uma pasta de videos."""
    try:
        series_info = build_series_from_folder(
            folder_path=req.folder_path,
            series_name=req.series_name,
            max_shorts=req.max_shorts,
            voice_name=req.voice_name,
            format_type=req.format_type
        )
        
        # Enfileira a renderizacao de cada episodio em background
        for job in series_info["jobs"]:
            background_tasks.add_task(process_video_job, job["job_id"])
            
        return {
            "status": "success",
            "message": f"Série '{req.series_name}' iniciada com {len(series_info['jobs'])} episódios!",
            "series": series_info
        }
    except Exception as e:
        logger.error(f"Erro ao criar série: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/jobs/{job_id}/upload-youtube")
async def upload_job_to_youtube(job_id: str):
    """Faz o upload do video gerado no job para o canal do YouTube."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nao encontrado")
    
    video_path = job.get("output_video")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=400, detail="Video nao encontrado ou nao concluido")
        
    title = job.get("topic", "Short Rota Calculada")
    result = upload_to_youtube(
        video_path=video_path,
        title=title,
        description=f"{title}\n\nInscreva-se no canal Rota Calculada para mais historias, lendas e mistérios!\n\n#Shorts #RotaCalculada #Historia #Lendas",
        tags=["Shorts", "RotaCalculada", "Historia", "Lendas", "Curiosidades"]
    )
    return result


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_html = ui_dir / "index.html"
    if index_html.exists():
        with open(index_html, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Rota Calculada AI Chat Studio</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

