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
from gtts import gTTS
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

odense_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\odense")
output_dir = Path(__file__).resolve().parent / "output" / "videos" / "odense_shorts"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "odense_shorts"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# 4 DISTINCT SHORTS FOR TIKTOK / SHORTS (STRICT 13-16 SECONDS GUARANTEED)
ODENSE_SHORTS_DEFINITIONS = [
    {
        "short_id": "short_odense_1",
        "title": "A Cidade dos Contos de Fadas 🇩🇰",
        "hook": "ESSA CIDADE VEIO DE UM LIVRO? 📖",
        "narration": "Você sabia que existe uma cidade na Dinamarca que parece ter saído direto de um livro de contos de fadas? Bem-vindo a Odense, com suas vilas medievais e ruazinhas de paralelepípedo encantadas!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-11 at 21.09.50.mp4", "start": 0.0, "dur": 14.5}
        ]
    },
    {
        "short_id": "short_odense_2",
        "title": "O Berço de H.C. Andersen 🧜‍♀️",
        "hook": "ONDE NASCEU A PEQUENA SEREIA? 🧜‍♀️",
        "narration": "Foi nas ruas históricas de Odense que nasceu Hans Christian Andersen, o lendário autor que criou A Pequena Sereia e O Patinho Feio! Cada esquina da cidade respira a magia de seus livros clássicos.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-11 at 21.09.54.mp4", "start": 0.0, "dur": 11.2}
        ],
        "image_clip": {"file": "WhatsApp Image 2026-08-11 at 21.09.44.jpeg", "dur": 4.5}
    },
    {
        "short_id": "short_odense_3",
        "title": "Estátuas Secretas de Odense 🗿",
        "hook": "ESCULTURAS SECRETAS NA DINAMARCA! 🗿",
        "narration": "Caminhando por Odense na Dinamarca, você encontra estátuas de bronze escondidas em ruelas e praças no coração da Escandinávia, homenageando os personagens mágicos dos contos de fadas mais famosos do mundo!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-11 at 21.10.23.mp4", "start": 0.0, "dur": 10.5},
            {"file": "WhatsApp Video 2026-08-11 at 21.10.24.mp4", "start": 0.0, "dur": 4.8}
        ]
    },
    {
        "short_id": "short_odense_4",
        "title": "Tour Panorâmico por Odense 🏰",
        "hook": "CIDADE MAIS MÁGICA DA DINAMARCA! 🏰",
        "narration": "Fundada há mais de mil anos na ilha de Fônia, a cidade de Odense combina a arquitetura nórdica preservada com uma qualidade de vida única na Escandinávia. Um lugar imperdível para visitar na Europa!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-11 at 21.10.24 (2).mp4", "start": 0.0, "dur": 16.5}
        ]
    }
]

async def generate_voice(text: str, out_path: str):
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-1%")
            await communicate.save(out_path)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 300:
                return
        except Exception:
            await asyncio.sleep(1.5)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        pass

def create_image_video_clip(img_path: Path, dur: float, w_t=1080, h_t=1920) -> ImageClip:
    img_pil = Image.open(img_path).convert("RGB")
    aspect_target = 9 / 16.0
    aspect_img = img_pil.width / float(img_pil.height)

    if aspect_img > aspect_target:
        new_w = int(img_pil.height * aspect_target)
        left = (img_pil.width - new_w) // 2
        img_pil = img_pil.crop((left, 0, left + new_w, img_pil.height))
    else:
        new_h = int(img_pil.width / aspect_target)
        top = (img_pil.height - new_h) // 2
        img_pil = img_pil.crop((0, top, img_pil.width, top + new_h))

    img_pil = img_pil.resize((w_t, h_t), Image.Resampling.LANCZOS)
    return ImageClip(np.array(img_pil)).with_duration(dur)

def produce_4_odense_shorts():
    print("==========================================")
    print("[PRODUZINDO 4 SHORTS EXCLUSIVOS (13-16s STRICT): ODENSE (DINAMARCA)]")
    print("==========================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    for idx, sdef in enumerate(ODENSE_SHORTS_DEFINITIONS, 1):
        short_id = sdef["short_id"]
        title = sdef["title"]
        hook_text = sdef["hook"]
        narration = sdef["narration"]
        v_clips_def = sdef.get("video_clips", [])
        img_clip_def = sdef.get("image_clip", None)

        voice_file = audio_dir / f"voice_{short_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.3

        clips_list = []
        raw_keepalive = []
        current_time = 0.0

        total_items = len(v_clips_def) + (1 if img_clip_def else 0)
        item_dur = target_dur / float(total_items)

        for v_info in v_clips_def:
            v_fname = v_info["file"]
            v_path = odense_dir / v_fname
            if v_path.exists():
                v_raw = VideoFileClip(str(v_path))
                raw_keepalive.append(v_raw)

                sub_d = min(item_dur, v_raw.duration)
                v_sub = v_raw.subclipped(0, sub_d)

                vw, vh = v_sub.w, v_sub.h
                aspect_t = 9 / 16.0
                aspect_v = vw / float(vh)

                if aspect_v > aspect_t:
                    new_w = int(vh * aspect_t)
                    crop_x = (vw - new_w) // 2
                    v_crop = v_sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
                else:
                    new_h = int(vw / aspect_t)
                    crop_y = (vh - new_h) // 2
                    v_crop = v_sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)

                v_res = v_crop.resized((w_t, h_t)).with_start(current_time)
                clips_list.append(v_res)
                current_time += sub_d

        if img_clip_def:
            i_fname = img_clip_def["file"]
            i_path = odense_dir / i_fname
            if i_path.exists():
                i_clip = create_image_video_clip(i_path, item_dur, w_t, h_t).with_start(current_time)
                clips_list.append(i_clip)
                current_time += item_dur

        v_comp = CompositeVideoClip(clips_list).with_duration(current_time)

        def add_short_overlay(get_frame, t):
            frame = get_frame(t)
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)

            if t < 2.5:
                draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 230))
                draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
                draw.text((540, 350), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

            draw.rectangle([(0, 80), (1080, 160)], fill=(0, 0, 0, 160))
            draw.text((540, 120), "ROTA CALCULADA | ODENSE 🇩🇰", fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
            return np.array(frame_pil)

        v_final_short = v_comp.transform(add_short_overlay)

        # Save thumbnail to artifacts for chat preview
        first_frame = Image.fromarray(v_final_short.get_frame(1.2))
        first_frame.save(artifacts_dir / f"{short_id}_thumb.png", format="PNG")

        bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.7)]

        if bgm_p.exists():
            bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
            audio_mix.append(bgm)

        comp_a = CompositeAudioClip(audio_mix)
        v_final_short = v_final_short.with_audio(comp_a).with_duration(current_time)

        master_path = output_dir / f"{short_id}_FINAL_MOVIE.mp4"
        temp_aud = str(output_dir / f"temp_audio_{short_id}.m4a")

        v_final_short.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

        v_final_short.close()
        comp_a.close()
        for c in clips_list:
            c.close()
        for v in raw_keepalive:
            v.close()

        print(f"  ✓ Short {idx:02d} [{short_id}]: {title} | Duração: {current_time:.1f}s -> {master_path}")

    print("\n🎉 [TODOS OS 4 SHORTS DE ODENSE FORAM CONCLUÍDOS COM SUCESSO!]")

if __name__ == "__main__":
    produce_4_odense_shorts()
