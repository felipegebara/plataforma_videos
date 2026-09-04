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

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    vfx
)

base_dir = Path(__file__).resolve().parent
legohouse_dir = base_dir / "legohouse"
output_shorts_dir = base_dir / "output" / "videos" / "legohouse_shorts"
audio_dir = base_dir / "output" / "audio" / "legohouse_suite"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\8289ff40-6fee-4bc8-a053-70c64e03f4f7")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir.mkdir(parents=True, exist_ok=True)

SHORT_DEF = {
    "title": "As Construções Mais Detalhadas em Lego 🏯🐑",
    "hook": "AS OBRAS MAIS DETALHADAS EM LEGO! 🏯🐑",
    "filename": "14_Construcoes_Mais_Detalhadas_em_Lego_Masterpieces",
    "narration": "Olha o detalhe inacreditável destas construções de Lego! Na Masterpiece Gallery, artistas recriaram desde um templo japonês tradicional cercado por cerejeiras floridas até um famoso quadro clássico com tosquia de ovelhas esculpido em relevo três D! Qual das duas você achou mais impressionante?",
    "video_file": "WhatsApp Video 2026-08-31 at 22.03.24.mp4",
    "start": 0.5,
    "dur": 15.0
}

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
            await asyncio.sleep(1.5)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception as e:
        print(f"Erro TTS: {e}")

def prepare_subclip_9_16(v_path: Path, st: float, dur: float, w_t=1080, h_t=1920, keepalive=None) -> VideoFileClip:
    raw = VideoFileClip(str(v_path))
    if keepalive is not None:
        keepalive.append(raw)

    max_avail = max(0.1, raw.duration - st)
    actual_dur = min(dur, max_avail)
    sub = raw.subclipped(st, st + actual_dur)

    vw, vh = sub.w, sub.h
    aspect_t = 9 / 16.0
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

def produce_obras_detalhadas_short():
    print("==================================================================")
    print(" [ATUALIZANDO VÍDEO 14: OBRAS-PRIMAS E CONSTRUÇÕES EM LEGO 🏯🐑] ")
    print("==================================================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_canal = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font_hook = ImageFont.load_default()
        font_canal = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    voice_file = audio_dir / f"voice_obras_detalhadas_{run_id}.mp3"
    asyncio.run(generate_voice(SHORT_DEF["narration"], str(voice_file)))
    voice_clip = AudioFileClip(str(voice_file))
    target_dur = voice_clip.duration + 0.35

    raw_keepalive = []
    v_path = legohouse_dir / SHORT_DEF["video_file"]
    sub_clip = prepare_subclip_9_16(v_path, SHORT_DEF["start"], target_dur, w_t, h_t, raw_keepalive)

    if sub_clip.duration < target_dur:
        sub_clip = sub_clip.with_effects([vfx.Loop(duration=target_dur)])
    else:
        sub_clip = sub_clip.subclipped(0, target_dur)

    # Dynamic overlay with 2-second viral hook and channel badge
    hook_text = SHORT_DEF["hook"]
    def add_short_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)

        # Hook nos primeiros 2.5 segundos (impacto viral)
        if t < 2.5:
            draw.rectangle([(0, 250), (1080, 440)], fill=(0, 0, 0, 230))
            draw.rectangle([(0, 250), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 345), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Barra do canal no topo
        draw.rectangle([(0, 80), (1080, 160)], fill=(0, 0, 0, 170))
        draw.text((540, 120), "ROTA CALCULADA | LEGO HOUSE 🧱", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        # Borda Dourada
        draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
        return np.array(frame_pil)

    v_final = sub_clip.transform(add_short_overlay)

    # Trilha de fundo
    bgm_p = base_dir / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.7)]

    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p))
        if bgm.duration < target_dur:
            bgm = bgm.with_effects([vfx.Loop(duration=target_dur)])
        else:
            bgm = bgm.subclipped(0, target_dur)
        audio_mix.append(bgm.with_volume_scaled(0.10))

    comp_a = CompositeAudioClip(audio_mix)
    v_final = v_final.with_audio(comp_a).with_duration(target_dur)

    # Salva thumbnail
    thumb_frame = Image.fromarray(v_final.get_frame(1.2))
    thumb_path = output_shorts_dir / f"{SHORT_DEF['filename']}_thumb.png"
    thumb_frame.save(thumb_path, format="PNG")
    thumb_frame.save(artifacts_dir / f"{SHORT_DEF['filename']}_thumb.png", format="PNG")

    master_path = output_shorts_dir / f"{SHORT_DEF['filename']}.mp4"
    temp_aud = str(output_shorts_dir / f"temp_audio_obras_{run_id}.m4a")

    print(f"Renderizando {SHORT_DEF['filename']}.mp4 | {target_dur:.1f}s...")
    v_final.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        threads=4,
        temp_audiofile=temp_aud,
        remove_temp=True,
        fps=24,
        logger=None
    )

    # Sincroniza com o nome antigo
    alt_p1 = output_shorts_dir / "14_O_Templo_Japones_e_Cerejeiras_Sakura_de_Lego.mp4"
    alt_p2 = output_shorts_dir / "short_legohouse_14_FINAL_MOVIE.mp4"
    import shutil
    shutil.copy2(master_path, alt_p1)
    shutil.copy2(master_path, alt_p2)

    v_final.close()
    comp_a.close()
    sub_clip.close()
    for v in raw_keepalive:
        v.close()

    print(f"\n🎉 [SHORT DE CONSTRUÇÕES DETALHADAS EM LEGO CONCLUÍDO COM SUCESSO!]")
    print(f"  - Duração: {target_dur:.1f}s")
    print(f"  - Arquivo: {master_path}")

if __name__ == "__main__":
    produce_obras_detalhadas_short()
