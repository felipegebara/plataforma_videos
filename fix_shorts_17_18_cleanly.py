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

# SHORT 17 E SHORT 18 CORRIGIDOS SEM CORTE BRUSCO
SHORTS_TO_FIX = [
    {
        "short_id": "short_legoland_17",
        "title": "A Área Aquática e Splash Zone 💦",
        "hook": "A DIVERSÃO NA ÁGUA! 💦",
        "narration": "Nos dias quentes de verão na Dinamarca, a área aquática da Legoland garante a diversão da criançada com jatos d'água interativos, fontes e brinquedos molhados!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (1).mp4", "start": 0.0, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (5).mp4", "start": 2.0, "dur": 7.5}
        ]
    },
    {
        "short_id": "short_legoland_18",
        "title": "Dicas para Visitar a Legoland 🇩🇰",
        "hook": "DICAS PARA VISITAR A LEGOLAND! 🇩🇰",
        "narration": "Vai viajar para a Dinamarca? A dica de ouro do Rota Calculada é reservar o dia inteiro para explorar a Legoland com calma e garantir os ingressos antecipados para curtir o parque!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 5.0, "dur": 14.5}
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

def main():
    print("==========================================")
    print("[CORRIGINDO SHORT 17 E SHORT 18 SEM CORTES BRUSCOS!]")
    print("==========================================")

    w_t, h_t = 1080, 1920
    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    for idx, sdef in enumerate(SHORTS_TO_FIX, 17):
        short_id = sdef["short_id"]
        title = sdef["title"]
        hook_text = sdef["hook"]
        narration = sdef["narration"]
        v_clips_def = sdef["video_clips"]

        voice_file = audio_dir / f"voice_{short_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.3

        clips_list = []
        raw_keepalive = []
        current_time = 0.0

        item_dur = target_dur / float(len(v_clips_def))

        for v_info in v_clips_def:
            v_fname = v_info["file"]
            v_st = v_info.get("start", 0.0)
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
        temp_aud = str(output_shorts_dir / f"temp_audio_{short_id}_{run_id}.m4a")

        v_final_short.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

        v_final_short.close()
        comp_a.close()
        for c in clips_list:
            c.close()
        for v in raw_keepalive:
            v.close()

        print(f"  ✓ Short {idx:02d} [{short_id}]: {title} | Duração: {current_time:.1f}s -> {master_path}")

if __name__ == "__main__":
    main()
