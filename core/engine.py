import os
import sys
import time
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)

# Project paths
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.db import db
from core.broker import get_broker
from core.resilience import ensure_ffmpeg_configured, resilient_edge_tts, resilient_search_and_download_image

import importlib
try:
    viral_agent_mod = importlib.import_module("agents.19_viral_packaging.agent")
    create_viral_package = viral_agent_mod.create_viral_package
except Exception as e:
    def create_viral_package(*args, **kwargs):
        return {"titles": {"viral_curiosity": "O Segredo Revelado!"}, "thumbnail_path": "", "description": "", "hashtags": []}

logger = logging.getLogger("core.engine")
ensure_ffmpeg_configured()

# =====================================================================
# TEMPLATES DE ROTEIROS INTELIGENTES PARA CADA CATEGORIA
# =====================================================================
LORE_TEMPLATES = {
    "MISTERY_HISTORY": {
        "hook_prefix": "O SEGREDO OCULTO DE",
        "intro": "Poucas pessoas sabem, mas escondido sob as aparências de {topic}, existe um dos maiores mistérios já registrados!",
        "development": "Documentos antigos e relatos de exploradores revelam segredos impressionantes que desafiam o que nos foi ensinado nos livros de história!",
        "conclusion": "O que você acha dessa revelação sobre {topic}? Deixe sua teoria nos comentários e siga o canal Rota Calculada!"
    },
    "LEGENDS_FOLKLORE": {
        "hook_prefix": "A LENDA QUE O TEMPO NÃO APAGOU:",
        "intro": "As antigas tradições contam que em {topic} repousa uma força mística que atravessou séculos de gerações!",
        "development": "Criaturas mitológicas, juramentos esquecidos e lendas fascinantes cercam este lugar extraordinário em cada detalhe!",
        "conclusion": "Você teria coragem de explorar esse mistério? Comente abaixo e acompanhe as expedições do Rota Calculada!"
    },
    "TRAVEL_TOURISM": {
        "hook_prefix": "O LUGAR MAIS FASCINANTE DE",
        "intro": "Prepare-se para conhecer uma das atrações mais espetaculares do mundo em {topic}!",
        "development": "Com uma estrutura impressionante e cenários de tirar o fôlego, este destino reúne cultura, diversão e engenharia de ponta!",
        "conclusion": "Já colocou {topic} na sua lista de viagens dos sonhos? Deixe seu like e inscreva-se no canal Rota Calculada!"
    }
}


def build_smart_script(topic: str, category: str = "MISTERY_HISTORY", custom_text: Optional[str] = None) -> str:
    if custom_text and len(custom_text.strip()) > 20:
        return custom_text.strip()

    template = LORE_TEMPLATES.get(category, LORE_TEMPLATES["MISTERY_HISTORY"])
    script = f"{template['intro'].format(topic=topic)} {template['development']} {template['conclusion'].format(topic=topic)}"
    return script


# =====================================================================
# PROCESSADOR DE VÍDEO & ANIMAÇÃO DE IMAGENS
# =====================================================================
def prepare_subclip(
    v_path: Path,
    st: float,
    dur: float,
    w_t: int = 1080,
    h_t: int = 1920,
    keepalive: Optional[List] = None
) -> VideoFileClip:
    raw = VideoFileClip(str(v_path))
    if keepalive is not None:
        keepalive.append(raw)

    max_avail = max(0.1, raw.duration - st)
    actual_dur = min(dur, max_avail)
    sub = raw.subclipped(st, st + actual_dur)

    vw, vh = sub.w, sub.h
    aspect_t = w_t / float(h_t)
    aspect_v = vw / float(vh)

    if aspect_v > aspect_t:
        new_w = int(vh * aspect_t)
        crop_x = (vw - new_w) // 2
        v_crop = sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
    else:
        new_h = int(vw / aspect_t)
        crop_y = (vh - new_h) // 2
        v_crop = sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)

    return v_crop.resized((w_t, h_t))


def create_ken_burns_clip(img_path: Path, dur: float, w_t: int = 1080, h_t: int = 1920) -> ImageClip:
    img_pil = Image.open(img_path).convert("RGB")
    aspect_t = w_t / float(h_t)
    aspect_img = img_pil.width / float(img_pil.height)

    if aspect_img > aspect_t:
        new_w = int(img_pil.height * aspect_t)
        left = (img_pil.width - new_w) // 2
        img_pil = img_pil.crop((left, 0, left + new_w, img_pil.height))
    else:
        new_h = int(img_pil.width / aspect_t)
        top = (img_pil.height - new_h) // 2
        img_pil = img_pil.crop((0, top, img_pil.width, top + new_h))

    img_pil = img_pil.resize((w_t, h_t), Image.Resampling.LANCZOS)
    img_np = np.array(img_pil)

    base_clip = ImageClip(img_np).with_duration(dur)

    def pan_zoom_transform(get_frame, t):
        prog = t / float(dur) if dur > 0 else 0
        scale = 1.0 + 0.12 * prog
        nw, nh = int(w_t * scale), int(h_t * scale)
        f_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w_t) * 0.5)
        sy = int((nh - h_t) * 0.5)
        return f_res[sy : sy + h_t, sx : sx + w_t].copy()

    return base_clip.transform(pan_zoom_transform)


# =====================================================================
# MOTOR PRINCIPAL DE PROCESSAMENTO DO JOB (ASYNC PIPELINE)
# =====================================================================
async def process_video_job(job_id: str, broker=None):
    """Executa a renderização completa do vídeo de ponta a ponta com persistência e progresso em tempo real."""
    if broker is None:
        broker = get_broker(mode="desktop")

    job_data = db.get_job(job_id)
    if not job_data:
        logger.error(f"[Engine] Job {job_id} não encontrado no banco.")
        return

    topic = job_data["topic"]
    category = job_data.get("category", "MISTERY_HISTORY")
    format_type = job_data.get("format_type", "short")
    voice_name = job_data.get("voice_name", "pt-BR-AntonioNeural")
    metadata = job_data.get("metadata", {})

    output_dir = project_root / "output" / "videos" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = project_root / "output" / "audio" / "temp"
    audio_dir.mkdir(parents=True, exist_ok=True)
    images_dir = project_root / "output" / "images" / "web_temp"
    images_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. ROTEIRO INTELIGENTE (LLM → template fallback)
        db.update_job_progress(job_id, 10, "Gerando roteiro narrativo com IA...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 10, "step": "Roteiro"})

        custom_script = metadata.get("custom_script")

        # Try LLM-generated viral script first (Gemini or OpenAI)
        llm_script: Optional[str] = None
        if not custom_script:
            try:
                import core.llm as _llm_module
                llm_script = _llm_module.generate_script(topic, category, format_type)
                if llm_script:
                    logger.info(f"[Engine] Roteiro LLM gerado ({len(llm_script.split())} palavras).")
            except Exception as _llm_err:
                logger.warning(f"[Engine] LLM indisponivel: {_llm_err}. Usando template.")

        script_text = build_smart_script(topic, category, llm_script or custom_script)

        # 2. SÍNTESE DE VOZ NEURAL RESILIENTE
        db.update_job_progress(job_id, 25, "Sintetizando voz humana neural...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 25, "step": "Voz Neural"})

        voice_file = audio_dir / f"voice_{job_id}.mp3"
        await resilient_edge_tts(script_text, str(voice_file), voice=voice_name)
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.35

        # 3. BUSCA DE ILUSTRAÇÕES COMPLEMENTARES DA WEB
        db.update_job_progress(job_id, 40, "Buscando ilustrações históricas na web...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 40, "step": "Ilustrações Web"})

        illustration_path = images_dir / f"illus_{job_id}.jpg"
        resilient_search_and_download_image(f"{topic} painting illustration", illustration_path)

        # 4. COMPOSIÇÃO DE VÍDEO HÍBRIDO (VÍDEO REAL + KEN BURNS)
        db.update_job_progress(job_id, 60, "Compondo cenas e efeitos dinâmicos...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 60, "step": "Composição"})

        w_t, h_t = (1080, 1920) if format_type == "short" else (1920, 1080)
        raw_keepalive = []
        scene_parts = []

        # Localiza vídeos brutos do usuário ou busca vídeos de apoio no Pexels/Pixabay
        input_clips = metadata.get("raw_video_files", [])
        stock_videos_dir = project_root / "output" / "videos" / "stock_temp" / job_id

        if input_clips:
            clip_dur = target_dur / float(len(input_clips) + (1 if illustration_path.exists() else 0))
            for c_path in input_clips:
                p = Path(c_path)
                if p.exists():
                    scene_parts.append(prepare_subclip(p, 0.0, clip_dur, w_t, h_t, raw_keepalive))
        else:
            # Fallback 1: Busca vídeos reais de apoio no Pexels / Pixabay
            db.update_job_progress(job_id, 45, "Buscando vídeos de apoio no Pexels / Pixabay...")
            from core.pexels_provider import get_stock_videos_for_topic
            stock_clips = get_stock_videos_for_topic(
                topic,
                stock_videos_dir,
                count=3,
                orientation="portrait" if format_type == "short" else "landscape"
            )

            if stock_clips:
                clip_dur = target_dur / float(len(stock_clips) + (1 if illustration_path.exists() else 0))
                for s_path in stock_clips:
                    scene_parts.append(prepare_subclip(s_path, 0.0, clip_dur, w_t, h_t, raw_keepalive))
            else:
                # Fallback 2: Acervo local de amostras
                sample_videos = list((project_root / "legohouse").glob("*.mp4")) + list((project_root / "arabia").glob("*.mp4"))
                if sample_videos:
                    scene_parts.append(prepare_subclip(sample_videos[0], 0.0, target_dur * 0.5, w_t, h_t, raw_keepalive))

        if illustration_path.exists():
            illus_dur = min(4.5, target_dur * 0.35)
            scene_parts.append(create_ken_burns_clip(illustration_path, illus_dur, w_t, h_t))

        if len(scene_parts) > 1:
            joined_scene = concatenate_videoclips(scene_parts)
        elif scene_parts:
            joined_scene = scene_parts[0]
        else:
            # Fallback seguro com background estilizado
            blank = np.zeros((h_t, w_t, 3), dtype=np.uint8)
            joined_scene = ImageClip(blank).with_duration(target_dur)

        if joined_scene.duration < target_dur:
            joined_scene = joined_scene.with_effects([vfx.Loop(duration=target_dur)])
        else:
            joined_scene = joined_scene.subclipped(0, target_dur)

        # 5. OVERLAY VISUAL E MARCA D'ÁGUA DO CANAL
        try:
            font_hook = ImageFont.truetype("arialbd.ttf", 46 if format_type == "short" else 64)
            font_canal = ImageFont.truetype("arialbd.ttf", 32 if format_type == "short" else 42)
        except Exception:
            font_hook = ImageFont.load_default()
            font_canal = ImageFont.load_default()

        hook_text = f"{topic.upper()} 🌟"

        def apply_branding_overlay(get_frame, t):
            frame = get_frame(t)
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)

            if format_type == "short":
                # Hook inicial de 2.5s
                if t < 2.5:
                    draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
                    draw.rectangle([(0, 260), (25, 440)], fill=(255, 215, 0))
                    draw.text((540, 350), hook_text[:35], fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

                draw.rectangle([(0, 70), (1080, 150)], fill=(0, 0, 0, 180))
                draw.text((540, 110), "ROTA CALCULADA 🌟", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
                draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
            else:
                draw.rectangle([(0, 40), (1920, 120)], fill=(0, 0, 0, 180))
                draw.text((960, 80), "ROTA CALCULADA | DOCUMENTÁRIO 🌟", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
                draw.rectangle([(25, 25), (1895, 1055)], outline=(255, 215, 0), width=6)

            return np.array(frame_pil)

        v_branded = joined_scene.transform(apply_branding_overlay)

        # 6. MIXAGEM DE ÁUDIO (VOZ + BGM)
        bgm_path = project_root / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.6)]

        if bgm_path.exists():
            try:
                bgm = AudioFileClip(str(bgm_path))
                if bgm.duration >= target_dur:
                    bgm_sub = bgm.subclipped(0, target_dur)
                else:
                    bgm_sub = bgm.subclipped(0, max(0.1, bgm.duration - 0.05))
                audio_mix.append(bgm_sub.with_volume_scaled(0.10))
            except Exception as e:
                logger.warning(f"[Engine] Erro ao carregar BGM: {e}")

        comp_audio = CompositeAudioClip(audio_mix)
        v_final = v_branded.with_audio(comp_audio).with_duration(target_dur)

        # 7. EXPORTAÇÃO DO ARQUIVO MP4 COM NOME CHAMATIVO E VIRAL
        db.update_job_progress(job_id, 80, "Renderizando arquivo MP4 final...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 80, "step": "Exportando MP4"})

        # Sanitiza o nome do arquivo para torná-lo atraente e chamativo
        clean_slug = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in topic]).strip().replace(" ", "_")
        clean_slug = clean_slug[:60] if clean_slug else f"video_{job_id}"
        output_movie_path = output_dir / f"{clean_slug}_{format_type}.mp4"
        temp_aud_file = str(output_dir / f"temp_aud_{job_id}.m4a")

        loop = asyncio.get_event_loop()
        def _render_task():
            v_final.write_videofile(
                str(output_movie_path),
                codec="libx264",
                audio_codec="aac",
                preset="fast",
                threads=4,
                temp_audiofile=temp_aud_file,
                remove_temp=True,
                fps=24,
                logger=None
            )

        await loop.run_in_executor(None, _render_task)

        # Fechamento de recursos
        v_final.close()
        comp_audio.close()
        for c in scene_parts:
            c.close()
        for r in raw_keepalive:
            r.close()

        # 8. AGENTE 19: PACOTE VIRAL (TÍTULOS, THUMBNAILS DE ALTO CTR & HASHTAGS)
        db.update_job_progress(job_id, 92, "Gerando títulos virais e thumbnail de alto CTR...")
        await broker.publish("stream:job_updates", {"job_id": job_id, "progress": 92, "step": "Pacote Viral"})

        viral_pkg = create_viral_package(
            video_path=str(output_movie_path),
            topic=topic,
            narration=script_text,
            format_type=format_type,
            category=category,
            output_dir=project_root / "output" / "thumbnails"
        )

        # 9. FINALIZAÇÃO E PERSISTÊNCIA COMPLETA NO BANCO
        db.complete_job(
            job_id=job_id,
            video_path=str(output_movie_path),
            thumbnail_path=viral_pkg["thumbnail_path"],
            titles=viral_pkg["titles"],
            selected_title=viral_pkg["selected_title"],
            description=viral_pkg["description"],
            hashtags=viral_pkg["hashtags"]
        )

        await broker.publish("stream:job_updates", {
            "job_id": job_id,
            "progress": 100,
            "step": "Concluído",
            "status": "COMPLETED",
            "video_path": str(output_movie_path),
            "thumbnail_path": viral_pkg["thumbnail_path"],
            "title": viral_pkg["selected_title"]
        })

        logger.info(f"[Engine] Job {job_id} finalizado com sucesso! Vídeo: {output_movie_path.name}")

    except Exception as err:
        logger.error(f"[Engine] Erro crítico no Job {job_id}: {err}", exc_info=True)
        db.fail_job(job_id, str(err))
        await broker.publish("stream:job_updates", {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(err)
        })
