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
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
output_base = Path(__file__).resolve().parent / "output" / "videos"
audio_base = Path(__file__).resolve().parent / "output" / "audio"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

# Mapeamento 100% EXCLUSIVO de arquivos e trechos de vídeo sem nenhuma sobreposição
UNIQUE_SHORTS_SPECS = [
    {
        "topic_id": "short_tamar_floripa_1",
        "title": "Short 1: O Maior Refúgio de Tartarugas de Floripa",
        "hook_text": "O MAIOR REFÚGIO DE TARTARUGAS! 🐢🌊",
        "sub_text": "PROJETO TAMAR - FLORIANÓPOLIS",
        "narration": "Você sabia que em Florianópolis existe um santuário incrível dedicado a salvar as tartarugas marinhas? No Projeto Tamar da Barra da Lagoa, você fica frente a frente com espécies gigantes! Siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4", "start": 0.0, "end": 14.5}
        ]
    },
    {
        "topic_id": "short_tamar_floripa_2",
        "title": "Short 2: Como é a Alimentação das Tartarugas",
        "hook_text": "ALIMENTAÇÃO DAS TARTARUGAS! 🥬🐟",
        "sub_text": "BARRA DA LAGOA - FLORIPA",
        "narration": "Olhe só como funciona o momento da alimentação das tartarugas no Projeto Tamar! Os biólogos explicam a dieta de cada espécie enquanto elas nadam pertinho dos visitantes. Incrível né? Siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 14.01.13 (1).mp4", "start": 0.0, "end": 11.8},
            {"file": "WhatsApp Video 2026-08-08 at 14.03.13.mp4", "start": 40.0, "end": 43.5}
        ]
    },
    {
        "topic_id": "short_tamar_floripa_3",
        "title": "Short 3: Vale a Pena Visitar o Tamar em Floripa",
        "hook_text": "VALE A PENA VISITAR O TAMAR? 📍🇧🇷",
        "sub_text": "DICA DE VIAGEM EM FLORIPA",
        "narration": "Vale a pena visitar o Projeto Tamar na Barra da Lagoa em Floripa? Com tanques gigantes, museu interativo e passeio à beira-mar, é um dos melhores passeios da ilha! Salve esse vídeo e siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 13.29.10.mp4", "start": 0.0, "end": 7.0},
            {"file": "WhatsApp Video 2026-08-08 at 13.29.42.mp4", "start": 0.0, "end": 7.2}
        ]
    },
    {
        "topic_id": "short_tamar_floripa_4",
        "title": "Short 4: Como o Tamar Salva Tartarugas em Extinção",
        "hook_text": "COMO O TAMAR SALVA TARTARUGAS? 🛡️🐢",
        "sub_text": "CONSERVAÇÃO E REABILITAÇÃO",
        "narration": "Como o Projeto Tamar salva milhares de tartarugas marinhas da extinção? Muitas são resgatadas de redes de pesca e reabilitadas aqui antes de voltarem ao oceano! Deixe seu apoio e siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 13.29.07.mp4", "start": 15.0, "end": 29.0}
        ]
    },
    {
        "topic_id": "short_tamar_floripa_5",
        "title": "Short 5: Espaço Educativo e Atividades no Tamar",
        "hook_text": "ESPAÇO EDUCATIVO NO TAMAR! 🎨🦴",
        "sub_text": "CULTURA E PRESERVAÇÃO",
        "narration": "Além dos tanques, o Tamar em Florianópolis tem um espaço educativo sensacional com réplicas gigantes, esqueletos e oficinas para crianças! Um passeio perfeito para a família! Siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 14.01.43.mp4", "start": 0.0, "end": 14.3}
        ]
    },
    {
        "topic_id": "short_tamar_floripa_6",
        "title": "Short 6: Praia da Barra da Lagoa e o Tamar",
        "hook_text": "PRAIA DA BARRA DA LAGOA + TAMAR! 🏖️🌊",
        "sub_text": "FLORIANÓPOLIS - SC",
        "narration": "Localizado exatamente na Praia da Barra da Lagoa, o Projeto Tamar une a beleza natural de Florianópolis à conscientização ambiental. Qual sua praia favorita em Floripa? Comente e siga o Rota Calculada!",
        "video_segments": [
            {"file": "WhatsApp Video 2026-08-08 at 14.01.55.mp4", "start": 15.0, "end": 29.0}
        ]
    }
]

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+4%")
    await communicate.save(out_path)

def process_unique_short(spec: dict):
    topic_id = spec["topic_id"]
    title = spec["title"]
    hook = spec["hook_text"]
    sub = spec["sub_text"]
    narration = spec["narration"]
    segments = spec["video_segments"]

    out_dir = output_base / topic_id
    aud_dir = audio_base / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    aud_dir.mkdir(parents=True, exist_ok=True)

    voice_path = aud_dir / "voice.mp3"
    asyncio.run(generate_voice(narration, str(voice_path)))
    voice_clip = AudioFileClip(str(voice_path))
    target_dur = max(13.0, voice_clip.duration + 0.2)

    clips_to_concat = []
    current_t = 0.0

    for seg in segments:
        file_name = seg["file"]
        st = seg["start"]
        et = seg["end"]

        v_path = tamar_dir / file_name
        if not v_path.exists():
            print(f"Warning: {file_name} not found!")
            continue

        v_raw = VideoFileClip(str(v_path))
        max_sub = min(et - st, v_raw.duration - st)
        if max_sub <= 0:
            st = 0.0
            max_sub = min(et, v_raw.duration)

        v_sub = v_raw.subclipped(st, st + max_sub)

        # Scale & Crop 9:16 Vertical HD 1080x1920
        w_t, h_t = 1080, 1920
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

        v_res = v_crop.resized((w_t, h_t)).with_start(current_t)
        clips_to_concat.append(v_res)
        current_t += max_sub

    v_comp = CompositeVideoClip(clips_to_concat).with_duration(target_dur)

    try:
        font_b = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_b = ImageFont.load_default()

    def add_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        if t < 2.5:
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), hook, fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final = v_comp.transform(add_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final.get_frame(0.5))
    first_frame.save(artifacts_dir / f"{topic_id}_thumb.png", format="PNG")

    audio_clips = [voice_clip.with_volume_scaled(1.7)]
    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(target_dur, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    comp_a = CompositeAudioClip(audio_clips)
    v_final = v_final.with_audio(comp_a).with_duration(target_dur)

    master_path = out_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    temp_aud = str(out_dir / f"temp_audio_{topic_id}.m4a")

    v_final.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final.close()
    comp_a.close()
    voice_clip.close()
    for c in clips_to_concat:
        c.close()

    print(f"  ✓ [{title.upper()} RE-MASTERIZADO E EXCLUSIVO] Duração: {target_dur:.1f}s -> {master_path}")

def fix_all_shorts_unique():
    print("==========================================")
    print("[RE-PRODUZINDO OS 6 SHORTS COM TRECHOS 100% EXCLUSIVOS E DIFERENTES]")
    print("==========================================")

    for spec in UNIQUE_SHORTS_SPECS:
        process_unique_short(spec)

if __name__ == "__main__":
    fix_all_shorts_unique()
