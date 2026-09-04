import os
import sys
import time
import json
import shutil
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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

legoland_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland")
output_shorts_dir = Path(__file__).resolve().parent / "output" / "videos" / "legoland_shorts"
output_long_dir = Path(__file__).resolve().parent / "output" / "videos" / "legoland_master_doc"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "legoland_suite"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
output_long_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# MAPEAMENTO AUDITADO DEFICIENTE PARA OS 12 SHORTS DA LEGOLAND BILLUND:
LEGOLAND_12_SHORTS_DEFINITIONS = [
    {
        "short_id": "short_legoland_1",
        "title": "O Primeiro Legoland do Mundo 🧱",
        "hook": "O PRIMEIRO LEGOLAND DO MUNDO! 🧱",
        "narration": "Você sabia que o primeiro parque Legoland do planeta foi inaugurado em mil novecentos e sessenta e oito na Dinamarca? Construído ao lado da fábrica original da Lego, o parque conta com réplicas gigantes, canais aquáticos e atrações radicais!",
        "image_clip": {"file": "legoland_entrance.jpg", "dur": 4.5},
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.46.18.mp4", "start": 1.0, "dur": 3.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.46.21.mp4", "start": 1.0, "dur": 3.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (3).mp4", "start": 1.0, "dur": 3.0}
        ]
    },
    {
        "short_id": "short_legoland_2",
        "title": "A Banda de Animatrônicos de Lego 🤖",
        "hook": "A BANDA DE ANIMATRÔNICOS! 🤖",
        "narration": "Olha que sensacional a banda de personagens animatrônicos de Lego tocando instrumentos no palco e fazendo um show interativo incrível para os visitantes da Legoland!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.45 (8).mp4", "start": 1.0, "dur": 14.5}]
    },
    {
        "short_id": "short_legoland_3",
        "title": "A Banda do Capitão Jack Sparrow 🏴‍☠️",
        "hook": "A BANDA DO CAPITAO JACK SPARROW! 🏴‍☠️",
        "narration": "Na terra dos piratas da Legoland, você encontra a banda do Capitão Jack Sparrow! Um show pirateco animado com música ao vivo e personagens marcantes dos sete mares!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.45 (10).mp4", "start": 1.0, "dur": 11.0}]
    },
    {
        "short_id": "short_legoland_4",
        "title": "LEGO Ninjago World 🥷",
        "hook": "O MUNDO SECRETO DOS NINJAS! 🥷",
        "narration": "Bem-vindo ao incrível Ninjago World na Legoland! Uma área temática interativa onde você treina como um verdadeiro ninja de Lego e encara desafios imersivos com Kai, Lloyd e Zane!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.44 (5).mp4", "start": 2.0, "dur": 14.5}]
    },
    {
        "short_id": "short_legoland_5",
        "title": "A Atração Interativa de Ninjago 🥷",
        "hook": "A ATRAÇÃO DO LEGO NINJAGO! 🥷",
        "narration": "Veja a fachada e a entrada da atração interativa do Lego Ninjago World! Um brinquedo de última geração onde você usa os poderes dos elementos para derrotar os vilões!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.45 (2).mp4", "start": 0.5, "dur": 5.4}]
    },
    {
        "short_id": "short_legoland_6",
        "title": "A Misteriosa Caverna de Gelo 🧊",
        "hook": "A MISTERIOSA CAVERNA DE GELO! 🧊",
        "narration": "Explore a misteriosa caverna de gelo da Legoland! Uma atração fascinante com esculturas congeladas, criaturas polares e efeitos visuais incríveis construídos em tamanho real!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.46.mp4", "start": 1.0, "dur": 11.5}]
    },
    {
        "short_id": "short_legoland_7",
        "title": "Copenhague em Miniatura de Lego 🇩🇰",
        "hook": "COPENHAGUE FEITA DE LEGO! 🇩🇰",
        "narration": "Esta é a réplica perfeita do famoso porto de Nyhavn e dos canais de Copenhague em Miniland! Mais de três milhões de pecinhas de Lego recriam a capital dinamarquesa com navios e casinhas coloridas em movimento!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.44 (6).mp4", "start": 3.0, "dur": 14.5}]
    },
    {
        "short_id": "short_legoland_8",
        "title": "Passeio de Barco pelas Maravilhas do Mundo 🚤",
        "hook": "PASSEIO DE BARCO PELAS MARAVILHAS! 🚤",
        "narration": "Neste passeio de barco interativo da Legoland, você navega por canais cercados pelas maiores maravilhas e monumentos do mundo em miniatura! Réplicas da Estátua da Liberdade, palácios e paisagens históricas de Lego!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.45 (3).mp4", "start": 3.0, "dur": 14.5}]
    },
    {
        "short_id": "short_legoland_9",
        "title": "O Aeroporto de Billund em Lego ✈️",
        "hook": "O AEROPORTO DE BILLUND EM LEGO! ✈️",
        "narration": "Olha a perfeição da réplica do Aeroporto Internacional de Billund na Miniland! Aviões, jatos e pistas de pouso em escala reduzida, onde cada aeronave de Lego taxia de verdade movida por motores elétricos!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.46 (5).mp4", "start": 3.0, "dur": 14.8}]
    },
    {
        "short_id": "short_legoland_10",
        "title": "Os Animais e a Fazenda de Lego 🐄",
        "hook": "OS ANIMAIS DA FAZENDA DE LEGO! 🐄",
        "narration": "Olha os detalhes dos animais e da fazenda de Lego na Miniland! Tratores em movimento, animais do campo e celeiros perfeitos montados tijolo por tijolo!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (4).mp4", "start": 0.0, "dur": 4.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (7).mp4", "start": 1.0, "dur": 8.0}
        ]
    },
    {
        "short_id": "short_legoland_11",
        "title": "A Mini Fazenda de Lego 🚜",
        "hook": "A MINI FAZENDA DE LEGO! 🚜",
        "narration": "Conheça a incrível mini fazenda de Lego! Moinhos de vento, celeiros, tratores e cenários rurais montados com milhares de peças em movimento!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-12 at 18.49.46 (7).mp4", "start": 1.0, "dur": 12.5}]
    },
    {
        "short_id": "short_legoland_12",
        "title": "Vale a Pena Visitar a Legoland? 🇩🇰",
        "hook": "VALE A PENA CONHECER A LEGOLAND? 🇩🇰",
        "narration": "Visitar o parque Legoland original em Billund na Dinamarca é uma experiência mágica e inesquecível para toda a família! Um passeio espetacular que vale cada segundo!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.46.18.mp4", "start": 0.5, "dur": 4.5},
            {"file": "WhatsApp Video 2026-08-12 at 18.46.21.mp4", "start": 0.5, "dur": 6.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (3).mp4", "start": 0.5, "dur": 4.5}
        ]
    }
]

async def generate_voice(text: str, out_path: str):
    p = Path(out_path)
    if p.exists() and p.stat().st_size > 1000:
        return

    for attempt in range(5):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-1%")
            await communicate.save(out_path)
            if p.exists() and p.stat().st_size > 1000:
                return
        except Exception:
            await asyncio.sleep(2.0)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        pass

def create_dynamic_entrance_image_clip(img_path: Path, dur: float, w_t=1080, h_t=1920) -> ImageClip:
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
    img_np = np.array(img_pil)

    base_clip = ImageClip(img_np).with_duration(dur)

    def pan_zoom_effect(get_frame, t):
        prog = t / float(dur)
        scale = 1.0 + 0.18 * prog
        nw, nh = int(w_t * scale), int(h_t * scale)
        f_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w_t) * 0.5)
        sy = int((nh - h_t) * 0.3 * prog)
        return f_res[sy : sy + h_t, sx : sx + w_t].copy()

    return base_clip.transform(pan_zoom_effect)

def produce_all_legoland_videos():
    print("==========================================")
    print("[PRODUZINDO OS 12 SHORTS DA LEGOLAND COM CORRESPONDÊNCIA VISUAL ABSOLUTA AUDITADA!]")
    print("==========================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    # PRODUZIR OS 12 SHORTS
    for idx, sdef in enumerate(LEGOLAND_12_SHORTS_DEFINITIONS, 1):
        short_id = sdef["short_id"]
        title = sdef["title"]
        hook_text = sdef["hook"]
        narration = sdef["narration"]
        v_clips_def = sdef.get("video_clips", [])
        img_clip_def = sdef.get("image_clip", None)

        voice_file = audio_dir / f"voice_{short_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.3

        clips_list = []
        raw_keepalive = []
        current_time = 0.0

        if img_clip_def:
            i_fname = img_clip_def["file"]
            img_dur = img_clip_def["dur"]
            i_path = legoland_dir / i_fname
            if i_path.exists():
                i_clip = create_dynamic_entrance_image_clip(i_path, img_dur, w_t, h_t).with_start(current_time)
                clips_list.append(i_clip)
                current_time += img_dur

            rem_dur = max(6.0, target_dur - img_dur)
            dur_per_v = rem_dur / float(len(v_clips_def))

            for v_info in v_clips_def:
                v_fname = v_info["file"]
                v_st = v_info.get("start", 3.0)
                v_path = legoland_dir / v_fname
                if v_path.exists():
                    v_raw = VideoFileClip(str(v_path))
                    raw_keepalive.append(v_raw)

                    sub_d = min(dur_per_v, max(0.1, v_raw.duration - v_st))
                    v_sub = v_raw.subclipped(v_st, v_st + sub_d)

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
        else:
            item_dur = target_dur / float(len(v_clips_def))
            for v_info in v_clips_def:
                v_fname = v_info["file"]
                v_st = v_info.get("start", 1.0)
                v_path = legoland_dir / v_fname
                if v_path.exists():
                    v_raw = VideoFileClip(str(v_path))
                    raw_keepalive.append(v_raw)

                    sub_d = min(item_dur, max(0.1, v_raw.duration - v_st))
                    v_sub = v_raw.subclipped(v_st, v_st + sub_d)

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
            draw.text((540, 120), "ROTA CALCULADA | LEGOLAND 🧱", fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
            return np.array(frame_pil)

        v_final_short = v_comp.transform(add_short_overlay)

        first_frame = Image.fromarray(v_final_short.get_frame(1.2))
        first_frame.save(artifacts_dir / f"{short_id}_thumb.png", format="PNG")

        bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.7)]

        if bgm_p.exists():
            bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
            audio_mix.append(bgm)

        comp_a = CompositeAudioClip(audio_mix)
        v_final_short = v_final_short.with_audio(comp_a).with_duration(current_time)

        master_path = output_shorts_dir / f"{short_id}_FINAL_MOVIE.mp4"
        temp_aud = str(output_shorts_dir / f"temp_audio_{short_id}_{run_id}_{idx}.m4a")

        v_final_short.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

        v_final_short.close()
        comp_a.close()
        for c in clips_list:
            c.close()
        for v in raw_keepalive:
            v.close()

        print(f"  ✓ Short {idx:02d} [{short_id}]: {title} | Duração: {current_time:.1f}s -> {master_path}")

if __name__ == "__main__":
    produce_all_legoland_videos()
