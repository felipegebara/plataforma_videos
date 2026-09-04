import os
import sys
import time
import json
import shutil
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
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

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

def download_modern_salvador(out_path: Path):
    url = "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=85"
    # Search unsplash for Salvador Pelourinho modern photo
    search_url = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=Pelourinho+Salvador+Bahia&gsrlimit=5&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    try:
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p_id, p_data in pages.items():
                info = p_data.get('imageinfo', [])
                if info:
                    img_url = info[0].get('thumburl') or info[0].get('url')
                    if img_url:
                        with urllib.request.urlopen(urllib.request.Request(img_url, headers=HEADERS), timeout=12) as r:
                            content = r.read()
                            if len(content) > 20000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print("✓ Foto moderna de Salvador obtida com sucesso!")
                                return True
    except Exception:
        pass

    # Fallback to Unsplash
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        with open(out_path, 'wb') as f:
            f.write(r.read())
    return True

def generate_past_salvador_ai(out_path: Path):
    prompt = (
        "Historical 19th century 1880s photograph of Pelourinho square in Salvador Bahia Brazil, "
        "vintage sepia tone, cobblestone streets, colonial Portuguese architecture with colorful facades, "
        "people in 1880s traditional Bahian attire, horse-drawn carriages, gas street lamps, "
        "photorealistic 8k, National Geographic documentary style, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(prompt)
    seed_val = int(time.time()) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"✓ Foto histórica do passado 1880 gerada pela IA!")
                    return True
        except Exception:
            time.sleep(1.0)
    return False

def format_photo_to_916_hd(raw_img_path: Path, out_path: Path, is_past: bool = False):
    w, h = 1080, 1920
    if not raw_img_path.exists():
        img_blank = Image.new("RGB", (w, h), (20, 20, 20))
        img_blank.save(out_path, format="PNG")
        return

    try:
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
        
        if is_past:
            # Sepia vintage enhancement
            img = ImageEnhance.Contrast(img).enhance(1.20)
            img = ImageEnhance.Color(img).enhance(0.85)
        else:
            # Modern vibrant colors
            img = ImageEnhance.Contrast(img).enhance(1.15)
            img = ImageEnhance.Color(img).enhance(1.20)

        img.save(out_path, format="PNG")
    except Exception:
        img_blank = Image.new("RGB", (w, h), (20, 20, 20))
        img_blank.save(out_path, format="PNG")

def render_time_travel_video():
    topic_id = "salvador_viagem_ao_passado"
    print(f"\n==========================================")
    print(f"[PRODUZINDO VÍDEO: SALVADOR - VIAGEM NO TEMPO (PRESENTE VS 1880)]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    raw_mod = images_dir / "raw_modern.jpg"
    raw_past = images_dir / "raw_past.jpg"
    fmt_mod = images_dir / "modern.png"
    fmt_past = images_dir / "past.png"

    download_modern_salvador(raw_mod)
    generate_past_salvador_ai(raw_past)

    format_photo_to_916_hd(raw_mod, fmt_mod, is_past=False)
    format_photo_to_916_hd(raw_past, fmt_past, is_past=True)

    shutil.copy(fmt_mod, artifacts_dir / "salvador_modern.png")
    shutil.copy(fmt_past, artifacts_dir / "salvador_past.png")

    # Narration script
    narration_parts = [
        ("scene1", "Como seria caminhar pelo Pelourinho em Salvador, mas viajando no tempo 140 anos para o passado?"),
        ("scene2", "Em 1880, as ruas de pedra ganhavam vida com lampiões a gás, carruagens e a arquitetura colonial em seu esplendor original."),
        ("scene3", "Uma viagem fascinante pela história da Bahia! Quer ver outra cidade no passado? Deixe nos comentários e siga o Rota Calculada!")
    ]

    for name, txt in narration_parts:
        asyncio.run(generate_voice(txt, str(audio_dir / f"voice_{name}.mp3")))

    # Render video clips with time morph transition effect
    fps = 24
    w, h = 1080, 1920
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Scene 1: Modern Salvador (Present)
    v1_audio = AudioFileClip(str(audio_dir / "voice_scene1.mp3"))
    dur1 = v1_audio.duration + 0.2
    scene1_mp4 = output_dir / "scene1.mp4"
    render_clip(fmt_mod, dur1, "slow_push_in", "SALVADOR HOJE 📍", "PELOURINHO - BAHIA", scene1_mp4, is_hook=True)

    # Scene 2: Time Travel Morph Transition to 1880
    v2_audio = AudioFileClip(str(audio_dir / "voice_scene2.mp3"))
    dur2 = v2_audio.duration + 0.2
    scene2_mp4 = output_dir / "scene2.mp4"
    render_morph_clip(fmt_mod, fmt_past, dur2, "SALVADOR EM 1880 📜", "VIAGEM NO TEMPO COM IA", scene2_mp4)

    # Scene 3: Historic Past & CTA
    v3_audio = AudioFileClip(str(audio_dir / "voice_scene3.mp3"))
    dur3 = v3_audio.duration + 0.2
    scene3_mp4 = output_dir / "scene3.mp4"
    render_clip(fmt_past, dur3, "slow_zoom_out", "SIGA @ROTACALCULADA 👇", "MAIS VIAGENS NO TEMPO", scene3_mp4, is_hook=False)

    # Composite master movie
    c1 = VideoFileClip(str(scene1_mp4)).with_start(0).with_duration(dur1)
    c2 = VideoFileClip(str(scene2_mp4)).with_start(dur1).with_duration(dur2)
    c3 = VideoFileClip(str(scene3_mp4)).with_start(dur1 + dur2).with_duration(dur3)

    a1 = v1_audio.with_start(0).with_volume_scaled(1.6)
    a2 = v2_audio.with_start(dur1).with_volume_scaled(1.6)
    a3 = v3_audio.with_start(dur1 + dur2).with_volume_scaled(1.6)

    video_clips = [c1, c2, c3]
    audio_clips = [a1, a2, a3]
    total_dur = dur1 + dur2 + dur3

    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(total_dur, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(output_dir / "temp_audio_salvador.m4a")

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

    print(f"\n🎉 VÍDEO SALVADOR NO PASSADO CONCLUÍDO ({total_dur:.1f}s): {master_path}")
    return master_path

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+4%")
    await communicate.save(out_path)

def render_clip(img_path: Path, dur: float, movement: str, title: str, sub: str, out_mp4: Path, is_hook: bool = False):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        if movement == "slow_push_in":
            scale = 1.0 + 0.14 * prog
            angle = 0.0
            dx, dy = 0.0, 0.0
        else:
            scale = 1.14 - 0.14 * prog
            angle = 0.0
            dx, dy = 0.0, 0.0

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w) * 0.5)
        sy = int((nh - h) * 0.5)
        frame_cropped = frame_res[sy : sy + h, sx : sx + w].copy()
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)
        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        if is_hook and f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), title, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_banner, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
        out_v.write(cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR))

    out_v.release()

def render_morph_clip(img1_path: Path, img2_path: Path, dur: float, title: str, sub: str, out_mp4: Path):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    img1_np = cv2.resize(np.array(Image.open(img1_path).convert("RGB")), (w, h))
    img2_np = cv2.resize(np.array(Image.open(img2_path).convert("RGB")), (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        alpha = f_idx / float(total_frames)
        # Morphing blend from present to past
        blended = cv2.addWeighted(img1_np, 1.0 - alpha, img2_np, alpha, 0)

        frame_grain = np.clip(blended.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)
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

if __name__ == "__main__":
    render_time_travel_video()
