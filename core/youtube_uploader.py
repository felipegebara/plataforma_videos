# -*- coding: utf-8 -*-
"""
core/youtube_uploader.py
Módulo de upload automático para o YouTube via OAuth2.
Utiliza google-auth, google-auth-oauthlib e google-api-python-client.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("core.youtube_uploader")

_YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def _get_youtube_client():
    """
    Tenta construir o cliente autenticado da YouTube Data API v3.
    Retorna (client, None) em caso de sucesso ou (None, error_message).
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        return None, (
            f"Dependências do Google não instaladas: {exc}. "
            "Execute: pip install google-auth google-auth-oauthlib google-api-python-client"
        )

    client_secret_path = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH", "").strip()
    if not client_secret_path or not Path(client_secret_path).is_file():
        return None, (
            "YouTube não configurado. Adicione client_secret.json e configure "
            "YOUTUBE_CLIENT_SECRET_PATH no .env"
        )

    token_path = Path(client_secret_path).parent / "youtube_token.json"
    creds: Optional[Credentials] = None

    if token_path.is_file():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), _YOUTUBE_SCOPES)
        except Exception as e:
            logger.warning(f"[YouTubeUploader] Não foi possível carregar token salvo: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"[YouTubeUploader] Falha ao renovar token: {e}")
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_path, _YOUTUBE_SCOPES
                )
                creds = flow.run_local_server(port=0, open_browser=False)
            except Exception as e:
                return None, f"Falha no fluxo OAuth2: {e}"

        try:
            with open(token_path, "w", encoding="utf-8") as fh:
                fh.write(creds.to_json())
        except Exception as e:
            logger.warning(f"[YouTubeUploader] Não foi possível salvar token: {e}")

    try:
        client = build("youtube", "v3", credentials=creds)
        return client, None
    except Exception as e:
        return None, f"Erro ao construir cliente YouTube: {e}"


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "22",
    privacy: str = "private",
    is_shorts: bool = False,
) -> dict:
    """
    Faz upload de um vídeo para o YouTube com upload resumível.

    Args:
        video_path:   Caminho absoluto para o arquivo .mp4
        title:        Título do vídeo
        description:  Descrição completa do vídeo
        tags:         Lista de tags
        category_id:  ID de categoria (default: "22" = People & Blogs)
        privacy:      "private", "unlisted" ou "public"
        is_shorts:    Se True, acrescenta #Shorts ao título

    Returns:
        dict com video_id, url e status, ou "error" em caso de falha.
    """
    video_path = str(video_path)
    if not Path(video_path).is_file():
        return {"error": f"Arquivo de vídeo não encontrado: {video_path}"}

    youtube, err = _get_youtube_client()
    if err:
        return {"error": err}

    final_title = title
    if is_shorts and "#Shorts" not in final_title:
        final_title = f"{title} #Shorts"

    body = {
        "snippet": {
            "title": final_title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
            "defaultLanguage": "pt",
            "defaultAudioLanguage": "pt",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    try:
        from googleapiclient.http import MediaFileUpload

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=256 * 1024,
        )
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        logger.info(f"[YouTubeUploader] Iniciando upload resumível: {video_path}")
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                logger.info(f"[YouTubeUploader] Upload {pct}%...")

        video_id = response.get("id", "")
        logger.info(f"[YouTubeUploader] Upload concluído! video_id={video_id}")
        return {
            "video_id": video_id,
            "url": f"https://youtube.com/watch?v={video_id}",
            "status": "uploaded",
            "title": final_title,
            "privacy": privacy,
        }
    except Exception as e:
        logger.error(f"[YouTubeUploader] Erro durante upload: {e}", exc_info=True)
        return {"error": str(e)}


def get_upload_status(video_id: str) -> dict:
    """
    Consulta o status de processamento de um vídeo já enviado ao YouTube.

    Args:
        video_id: ID do vídeo no YouTube

    Returns:
        dict com video_id, upload_status, processing_status e detalhes.
    """
    youtube, err = _get_youtube_client()
    if err:
        return {"error": err}

    try:
        response = youtube.videos().list(
            part="status,processingDetails,snippet",
            id=video_id,
        ).execute()

        items = response.get("items", [])
        if not items:
            return {"error": f"Vídeo não encontrado: {video_id}"}

        item = items[0]
        status = item.get("status", {})
        processing = item.get("processingDetails", {})
        snippet = item.get("snippet", {})

        return {
            "video_id": video_id,
            "url": f"https://youtube.com/watch?v={video_id}",
            "upload_status": status.get("uploadStatus", "unknown"),
            "privacy": status.get("privacyStatus", "unknown"),
            "processing_status": processing.get("processingStatus", "unknown"),
            "processing_progress": processing.get("processingProgress", {}),
            "title": snippet.get("title", ""),
            "published_at": snippet.get("publishedAt", ""),
        }
    except Exception as e:
        logger.error(f"[YouTubeUploader] Erro ao consultar status: {e}", exc_info=True)
        return {"error": str(e)}
