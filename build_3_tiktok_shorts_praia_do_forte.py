import os
import sys
import time
import json
import shutil
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, vfx

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

TIKTOK_SPECS = [
    {
        "topic_id": "tiktok_praia_do_forte_1",
        "title": "Short 1: O Segredo Escondido de Praia do Forte",
        "hook_text": "O SEGREDO ESCONDIDO DE PRAIA DO FORTE! 🌊🌿",
        "sub_text": "MATA DE SÃO JOÃO - BAHIA",
        "narration": "Você sabia que Praia do Forte na Bahia esconde um paraíso secreto além das praias? Conheça essa cachoeira deslumbrante cercada pela Mata Atlântica! Você encararia essa água cristalina? Siga o Rota Calculada!",
        "speed": 1.0,
        "start_time": 0.0
    },
    {
        "topic_id": "tiktok_praia_do_forte_2",
        "title": "Short 2: Cachoeira ou Praia na Bahia?",
        "hook_text": "CACHOEIRA OU PRAIA NA BAHIA? 🌴☀️",
        "sub_text": "QUAL A SUA ESCOLHA?",
        "narration": "Se você tivesse apenas um dia em Praia do Forte na Bahia, você escolheria mergulhar nas piscinas naturais do mar ou nessa cachoeira paradisíaca? Responda nos comentários e siga o Rota Calculada!",
        "speed": 1.05,
        "start_time": 1.5
    },
    {
        "topic_id": "tiktok_praia_do_forte_3",
        "title": "Short 3: O Refúgio Secreto da Bahia",
        "hook_text": "O REFÚGIO SECRETO DA BAHIA! 🧘‍♀️✨",
        "sub_text": "SALVE PARA A PRÓXIMA VIAGEM",
        "narration": "Esqueça a rotina por quinze segundos. Esse é o som e a paz da cachoeira em Praia do Forte, na Bahia. Salve esse vídeo para sua próxima viagem e siga o Rota Calculada!",
        "speed": 0.95,
        "start_time": 0.5
    }
]

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+5%")
    await communicate.save(out_path)

def process_tiktok_video(src_video_path: Path, spec: dict, output_dir: Path, artifacts_dir: Path):
    topic_id = spec["topic_id"]
    title = spec["title"]
    hook = spec["hook_text"]
    sub = spec["sub_text"]
    narration = spec["narration"]
    start_t = spec["start_time"]

    audio_dir = output_dir.parent.parent / "audio" / topic_id
    audio_dir.mkdir(parents=True, exist_ok=True)
    voice_path = audio_dir / "voice.mp3"

    asyncio.run(generate_voice(narration, str(voice_path)))
    voice_clip = AudioFileClip(str(voice_path))
    target_dur = max(13.0, min(18.0, voice_clip.duration + 0.3))

    # Process original raw video clip
    orig_v = VideoFileClip(str(src_video_path))
    
    # Handle video subclip slicing & duration looping if needed
    if orig_v.duration >= start_t + target_dur:
        v_sub = orig_v.subclipped(start_t, start_t + target_dur)
    else:
        # Loop subclip to reach target duration
        v_sub = orig_v.subclipped(0, min(orig_v.duration, target_dur))
        if v_sub.duration < target_dur:
            v_sub = v_sub.looped(duration=target_dur)

    # Re-scale & Crop to exact 9:16 vertical HD 1080x1920
    w_target, h_target = 1080, 1920
    vw, vh = v_sub.w, v_sub.h
    aspect_target = 9 / 16.0
    aspect_v = vw / float(vh)

    if aspect_v > aspect_target:
        new_w = int(vh * aspect_target)
        crop_x = (vw - new_w) // 2
        v_crop = v_sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
    else:
        new_h = int(vw / aspect_target)
        crop_y = (vh - new_h) // 2
        v_crop = v_sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)

    v_resized = v_crop.resized((w_target, h_target))

    # Add text overlay banner using MoviePy / PIL frame transformation
    try:
        font_b = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_b = ImageFont.load_default()

    def add_overlay(get_frame, t):
        frame = get_frame(t)
        if t < 2.5:
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), hook, fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
            draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
            return np.array(frame_pil)
        else:
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)
            draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
            return np.array(frame_pil)

    v_final = v_resized.transform(add_overlay)

    # Save thumbnail to artifacts for direct chat preview
    first_frame = Image.fromarray(v_final.get_frame(0.5))
    art_path = artifacts_dir / f"{topic_id}_thumb.png"
    first_frame.save(art_path, format="PNG")

    # Combine narration voice + original waterfall audio background
    audio_clips = [voice_clip.with_volume_scaled(1.7)]
    if orig_v.audio:
        orig_aud = orig_v.audio.subclipped(0, min(target_dur, orig_v.audio.duration)).with_volume_scaled(0.25)
        audio_clips.append(orig_aud)

    comp_a = CompositeAudioClip(audio_clips)
    v_final = v_final.with_audio(comp_a).with_duration(target_dur)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    temp_aud = str(output_dir / f"temp_audio_{topic_id}.m4a")

    v_final.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_aud,
        remove_temp=True,
        fps=24,
        logger=None
    )

    v_final.close()
    comp_a.close()
    voice_clip.close()
    orig_v.close()

    print(f"  ✓ [{title.upper()} CONCLUÍDO] Duração: {target_dur:.1f}s -> {master_path}")
    return master_path

def produce_3_praia_do_forte_tiktok_shorts():
    src_video = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\praia do forte\Cachoeira em Praia do Forte #bahia.mp4")
    output_base = Path(__file__).resolve().parent / "output" / "videos"
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    if not src_video.exists():
        print(f"Error: Source video not found at {src_video}")
        return

    print("==========================================")
    print("[PRODUZINDO 3 SHORTS TIKTOK DE PRAIA DO FORTE - BAHIA]")
    print("==========================================")

    for spec in TIKTOK_SPECS:
        topic_id = spec["topic_id"]
        out_dir = output_base / topic_id
        out_dir.mkdir(parents=True, exist_ok=True)
        process_tiktok_video(src_video, spec, out_dir, artifacts_dir)

if __name__ == "__main__":
    produce_3_praia_do_forte_tiktok_shorts()
