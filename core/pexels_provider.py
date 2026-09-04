import os
import sys
import json
import logging
import urllib.parse
from pathlib import Path
from typing import List, Optional
import httpx

logger = logging.getLogger("PexelsProvider")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# Dicionário de tradução rápida e keywords para temas históricos/lendas
KEYWORD_MAP = {
    "triangulo das bermudas": "ocean sea mystery stormy water aerial",
    "bermudas": "ocean storm clouds deep sea",
    "canudos": "arid sertao dry lands brazil historical village",
    "egito": "pyramids desert egypt camels sand",
    "roma": "rome colosseum ancient ruins ancient city",
    "castelo": "medieval castle misty mountains stone fortress",
    "deserto": "desert sand dunes sunset desert storm",
    "oceano": "deep ocean dark waters underwater waves",
    "floresta": "mystical forest dark woods trees fog",
    "samurai": "japan temple sakura japanese mountains",
    "viking": "nordic mountains fjord dramatic sea longship",
    "dinossauro": "jungle prehistoric forest dramatic nature fog",
    "espaco": "galaxy stars universe earth from space",
    "lego": "colorful toys building blocks creativity miniature"
}

def translate_to_search_keywords(topic: str) -> str:
    topic_lower = topic.lower()
    for key, kw in KEYWORD_MAP.items():
        if key in topic_lower:
            return kw
    
    # Limpa termos em português
    clean = topic.replace("O ", "").replace("A ", "").replace("Os ", "").replace("As ", "")
    clean = clean.replace("de ", "").replace("do ", "").replace("da ", "").replace("em ", "")
    return clean.strip() or "cinematic dramatic landscape nature"

def fetch_pexels_videos(query: str, orientation: str = "portrait", count: int = 3, min_duration: int = 4) -> List[dict]:
    """Busca vídeos de estoque no Pexels API."""
    api_key = os.getenv("PEXELS_API_KEY", PEXELS_API_KEY)
    if not api_key:
        logger.info("[Pexels] Chave PEXELS_API_KEY não configurada. Usando fallback...")
        return []

    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page={count*2}&orientation={orientation}"
    headers = {"Authorization": api_key}
    
    try:
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                videos = data.get("videos", [])
                results = []
                for v in videos:
                    if v.get("duration", 0) < min_duration:
                        continue
                    v_files = v.get("video_files", [])
                    # Seleciona qualidade HD vertical/horizontal
                    best_file = None
                    for vf in v_files:
                        if orientation == "portrait" and vf.get("width", 0) < vf.get("height", 0):
                            best_file = vf.get("link")
                            break
                        elif orientation == "landscape" and vf.get("width", 0) > vf.get("height", 0):
                            best_file = vf.get("link")
                            break
                    if not best_file and v_files:
                        best_file = v_files[0].get("link")

                    if best_file:
                        results.append({
                            "id": v.get("id"),
                            "url": best_file,
                            "duration": v.get("duration"),
                            "width": v.get("width"),
                            "height": v.get("height")
                        })
                    if len(results) >= count:
                        break
                return results
            else:
                logger.warning(f"[Pexels] Erro {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"[Pexels] Exceção ao buscar vídeos: {e}")
    return []

def fetch_pixabay_videos(query: str, count: int = 3) -> List[dict]:
    """Busca vídeos de estoque no Pixabay API."""
    api_key = os.getenv("PIXABAY_API_KEY", PIXABAY_API_KEY)
    if not api_key:
        return []

    url = f"https://pixabay.com/api/videos/?key={api_key}&q={urllib.parse.quote(query)}&per_page={count*2}"
    try:
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                results = []
                for hit in hits:
                    v_data = hit.get("videos", {})
                    # Pega medium ou large
                    med = v_data.get("medium", {}) or v_data.get("large", {}) or v_data.get("small", {})
                    v_url = med.get("url")
                    if v_url:
                        results.append({
                            "id": hit.get("id"),
                            "url": v_url,
                            "duration": hit.get("duration", 10),
                            "width": med.get("width", 1080),
                            "height": med.get("height", 1920)
                        })
                    if len(results) >= count:
                        break
                return results
    except Exception as e:
        logger.error(f"[Pixabay] Exceção ao buscar vídeos: {e}")
    return []

def download_video_clip(url: str, dest_path: Path) -> bool:
    """Baixa com segurança um clipe de vídeo da web."""
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200 and len(resp.content) > 10000:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"[StockVideo] Vídeo salvo: {dest_path} ({len(resp.content)/(1024*1024):.2f} MB)")
                return True
    except Exception as e:
        logger.error(f"[StockVideo] Falha no download de {url}: {e}")
    return False

def get_stock_videos_for_topic(
    topic: str,
    output_dir: Path,
    count: int = 3,
    orientation: str = "portrait"
) -> List[Path]:
    """
    Coordena a busca e download de vídeos de apoio no Pexels e Pixabay.
    Retorna lista de caminhos locais dos vídeos baixados.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    keywords = translate_to_search_keywords(topic)
    logger.info(f"[StockVideo] Buscando vídeos de apoio para '{topic}' com keywords: '{keywords}'")

    video_items = []
    # 1. Tenta Pexels
    video_items = fetch_pexels_videos(keywords, orientation=orientation, count=count)

    # 2. Tenta Pixabay se Pexels não retornar
    if not video_items:
        video_items = fetch_pixabay_videos(keywords, count=count)

    downloaded_paths = []
    for idx, item in enumerate(video_items, 1):
        v_url = item["url"]
        safe_name = f"stock_{idx}_{item['id']}.mp4"
        dest_p = output_dir / safe_name
        if dest_p.exists() and dest_p.stat().st_size > 10000:
            downloaded_paths.append(dest_p)
        else:
            if download_video_clip(v_url, dest_p):
                downloaded_paths.append(dest_p)

    return downloaded_paths
