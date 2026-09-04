import os
import sys
import time
import json
import shutil
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import cv2
import numpy as np
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

# Sequence of 7 eras requested by user
ERAS_CONFIG = [
    {
        "era": "Hoje",
        "title": "PELOURINHO HOJE 📍",
        "sub": "SALVADOR - BAHIA",
        "narration": "Começamos no Pelourinho de hoje em Salvador, com suas cores vivas e calçamento colonial preservado.",
        "prompt": "Modern photograph of Pelourinho square in Salvador Bahia Brazil, vibrant colorful colonial facades, sunny day, tourists walking, 8k RAW photo"
    },
    {
        "era": "1980",
        "title": "PELOURINHO NOS ANOS 1980 📼",
        "sub": "ÉPOCA DE OURO DA MPB E AXÉ",
        "narration": "Voltando aos anos 1980! Época de ouro da cultura baiana, com veículos vintage e estética retro.",
        "prompt": "1980s photograph of Pelourinho square in Salvador Bahia, vintage 1980s retro film colors, 1980s cars parked, people in 80s fashion, Kodachrome 35mm"
    },
    {
        "era": "1970",
        "title": "PELOURINHO NOS ANOS 1970 ☮️",
        "sub": "TROPICÁLIA E ANOS 70",
        "narration": "Chegamos nos anos 1970! O movimento tropicalista ecoa pelas ladeiras históricas.",
        "prompt": "1970s vintage photograph of Pelourinho square in Salvador Bahia, 1970s warm film grain, Volkswagen beetles, 70s attire, classic 35mm photo"
    },
    {
        "era": "1960",
        "title": "PELOURINHO NOS ANOS 1960 🎞️",
        "sub": "CINEMA NOVO E BOSSA NOVA",
        "narration": "Anos 1960! A efervescência do Cinema Novo em imagens de época marcantes.",
        "prompt": "1960s vintage photograph of Pelourinho square Salvador Bahia, 1960s black and white and muted film tones, classic 1960s European style cars, retro style"
    },
    {
        "era": "1950",
        "title": "PELOURINHO NOS ANOS 1950 📻",
        "sub": "BAHIA DOS ANOS DOURADOS",
        "narration": "Anos 1950! Os anos dourados do Brasil com bondes elétricos e elegância clássica.",
        "prompt": "1950s photograph of Pelourinho square Salvador Bahia, 1950s vintage film grain, vintage electric tram, men in classic suits and hats, 1950s ambiance"
    },
    {
        "era": "1900",
        "title": "PELOURINHO EM 1900 📜",
        "sub": "INÍCIO DO SÉCULO XX",
        "narration": "Virada do século XX em 1900! Lampiões a gás, primeiras carruagens elétricas e fotografia clássica.",
        "prompt": "Early 1900s photograph of Pelourinho square Salvador Bahia, sepia monochrome tone, horse carriages, gas street lamps, Victorian Edwardian clothing, historical archive"
    },
    {
        "era": "1800",
        "title": "PELOURINHO EM 1800 ⚔️",
        "sub": "PERÍODO IMPERIAL COLONIAL",
        "narration": "E finalmente 1800! Período imperial colonial com carruagens de tração animal e a arquitetura original.",
        "prompt": "1800s historical 19th century photograph of Pelourinho square Salvador Bahia, sepia tone, 1800s colonial architecture, horse drawn carriages, authentic historic 1800s clothing"
    }
]

def fetch_image_for_era(prompt: str, era_id: str, out_path: Path):
    encoded = urllib.parse.quote(f"{prompt}, high quality, detailed, no watermark")
    seed_val = (int(time.time()) + hash(era_id) * 333) % 999999
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"  ✓ Imagem da Era '{era_id}' gerada com sucesso!")
                    return True
        except Exception:
            time.sleep(1.0)
    return False

def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    w, h = 1080, 1920
    if not raw_img_path.exists():
        img_blank = Image.new("RGB", (w, h), (20, 20, 20))
        img_blank.save(out_path, format="PNG")
        return

    img = Image.open(raw_img_path).convert("RGB")
    aspect_target = 9 / 16.0
    aspect_img = img.width / float(img.height)

    if aspect_img > aspect_target:
        new_w = int(img.height * aspect_target)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / aspect_target)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))

    img = img.resize((w, h), Image.Resampling.LANCZOS)
    img.save(out_path, format="PNG")

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+6%")
    await communicate.save(out_path)

def render_era_morph_clip(img1_path: Path, img2_path: Path, dur: float, title: str, sub: str, out_mp4: Path):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    img1_np = cv2.resize(np.array(Image.open(img1_path).convert("RGB")), (w, h))
    img2_np = cv2.resize(np.array(Image.open(img2_path).convert("RGB")), (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 42)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        alpha = f_idx / float(total_frames)
        blended = cv2.addWeighted(img1_np, 1.0 - alpha, img2_np, alpha, 0)

        scale = 1.0 + 0.08 * alpha
        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(blended, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w) * 0.5)
        sy = int((nh - h) * 0.5)
        frame_cropped = frame_res[sy : sy + h, sx : sx + w].copy()
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)

        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)
        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        if f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), title, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_banner, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
        out_v.write(cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR))

    out_v.release()

def produce_7_eras_pelourinho():
    topic_id = "pelourinho_7_eras_timetravel"
    print(f"\n==========================================")
    print(f"[PRODUZINDO DOCUMENTÁRIO COMPLETO: PELOURINHO EM 7 ÉPOCAS DA HISTÓRIA]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    formatted_images = []

    # 1. Gerar e formatar imagens para as 7 épocas
    for idx, cfg in enumerate(ERAS_CONFIG, 1):
        era = cfg["era"]
        prompt = cfg["prompt"]
        raw_path = images_dir / f"raw_era_{era}.jpg"
        fmt_path = images_dir / f"era_{era}.png"
        art_path = artifacts_dir / f"pelourinho_era_{era}.png"

        fetch_image_for_era(prompt, era, raw_path)
        format_photo_to_916_hd(raw_path, fmt_path)
        shutil.copy(fmt_path, art_path)
        formatted_images.append(fmt_path)

    # 2. Gerar locuções
    audio_clips = []
    video_clips = []
    current_time = 0.0

    for idx, cfg in enumerate(ERAS_CONFIG):
        era = cfg["era"]
        title = cfg["title"]
        sub = cfg["sub"]
        narr = cfg["narration"]
        voice_path = audio_dir / f"voice_{era}.mp3"
        scene_mp4 = output_dir / f"scene_{era}.mp4"

        asyncio.run(generate_voice(narr, str(voice_path)))
        v_audio = AudioFileClip(str(voice_path))
        dur = v_audio.duration + 0.25

        img_curr = formatted_images[idx]
        img_next = formatted_images[idx + 1] if idx + 1 < len(formatted_images) else formatted_images[idx]

        render_era_morph_clip(img_curr, img_next, dur, title, sub, scene_mp4)

        v_clip = VideoFileClip(str(scene_mp4)).with_start(current_time).with_duration(dur)
        a_clip = v_audio.with_start(current_time).with_volume_scaled(1.6)

        video_clips.append(v_clip)
        audio_clips.append(a_clip)

        current_time += dur
        print(f"  ✓ Cena Era {era} acoplada ({dur:.2f}s | Total: {current_time:.1f}s)")

    # 3. Trilha sonora de fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(output_dir / "temp_audio_7eras.m4a")

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio,
        remove_temp=True,
        fps=24,
        logger=None
    )

    comp_v.close()
    comp_a.close()
    for c in video_clips:
        c.close()
    for a in audio_clips:
        a.close()

    print(f"\n🎉 VÍDEO COMPLETO PELOURINHO EM 7 ÉPOCAS CONCLUÍDO ({current_time:.1f}s): {master_path}")
    return master_path

if __name__ == "__main__":
    produce_7_eras_pelourinho()
