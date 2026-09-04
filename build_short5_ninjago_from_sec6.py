import os
import sys
import time
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

legoland_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland")
output_shorts_dir = Path(__file__).resolve().parent / "output" / "videos" / "legoland_shorts"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "legoland_suite"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

short_id = "short_legoland_5"
title = "A Atração Ninja de LEGO Ninjago 🥷"
hook_text = "A ATRAÇÃO DO LEGO NINJAGO! 🥷"
narration = "Bem-vindo ao LEGO Ninjago World! E a partir de agora, veja o vídeo por dentro da atração interativa dos ninjas com Kai, Lloyd e Zane!"

ninjago_vid1 = legoland_dir / "WhatsApp Video 2026-08-12 at 18.49.45 (2).mp4"
ninjago_vid2 = legoland_dir / "WhatsApp Video 2026-08-12 at 18.49.44 (5).mp4"

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

def main():
    print("==========================================")
    print("[PRODUZINDO SHORT 5: A PARTIR DO SEGUNDO 5.5 ENTRA A ATRAÇÃO DO NINJAGO!]")
    print("==========================================")

    w_t, h_t = 1080, 1920
    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    run_id = int(time.time() * 1000)
    voice_file = audio_dir / f"voice_{short_id}_{run_id}.mp3"
    asyncio.run(generate_voice(narration, str(voice_file)))
    voice_clip = AudioFileClip(str(voice_file))
    target_dur = voice_clip.duration + 0.3

    clips_list = []
    raw_keepalive = []
    current_time = 0.0

    # 1. Primeiros 5.5 segundos: Entrada do Ninjago World
    if ninjago_vid1.exists():
        v1 = VideoFileClip(str(ninjago_vid1))
        raw_keepalive.append(v1)
        v1_dur = min(5.5, max(0.1, v1.duration - 0.1))
        v1_sub = v1.subclipped(0.0, v1_dur)
        vw, vh = v1_sub.w, v1_sub.h
        aspect_t = 9 / 16.0
        aspect_v = vw / float(vh)
        if aspect_v > aspect_t:
            new_w = int(vh * aspect_t)
            crop_x = (vw - new_w) // 2
            v1_crop = v1_sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
        else:
            new_h = int(vw / aspect_t)
            crop_y = (vh - new_h) // 2
            v1_crop = v1_sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)
        v1_res = v1_crop.resized((w_t, h_t)).with_start(current_time)
        clips_list.append(v1_res)
        current_time += v1_dur

    # 2. A partir do corte: Substituído EXCLUSIVAMENTE PELA ATRAÇÃO DO NINJAGO
    rem_dur = max(3.0, target_dur - current_time)
    if ninjago_vid2.exists():
        v2 = VideoFileClip(str(ninjago_vid2))
        raw_keepalive.append(v2)
        v2_dur = min(rem_dur, max(0.1, v2.duration - 1.0))
        v2_sub = v2.subclipped(1.0, 1.0 + v2_dur)
        vw, vh = v2_sub.w, v2_sub.h
        aspect_t = 9 / 16.0
        aspect_v = vw / float(vh)
        if aspect_v > aspect_t:
            new_w = int(vh * aspect_t)
            crop_x = (vw - new_w) // 2
            v2_crop = v2_sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
        else:
            new_h = int(vw / aspect_t)
            crop_y = (vh - new_h) // 2
            v2_crop = v2_sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)
        v2_res = v2_crop.resized((w_t, h_t)).with_start(current_time)
        clips_list.append(v2_res)
        current_time += v2_dur

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
    temp_aud = str(output_shorts_dir / f"temp_audio_{short_id}_{run_id}.m4a")

    v_final_short.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final_short.close()
    comp_a.close()
    for c in clips_list:
        c.close()
    for v in raw_keepalive:
        v.close()

    print(f"\n  ✓ Short 5 [{short_id}]: {title} | Duração: {current_time:.1f}s -> {master_path}")

if __name__ == "__main__":
    main()
