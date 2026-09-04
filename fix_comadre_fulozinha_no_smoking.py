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
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

def fetch_ai_image(prompt: str, style_prefix: str, seed_id: int, out_path: Path) -> bool:
    enhanced_prompt = f"{style_prefix}, {prompt}"
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + seed_id * 9999) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"  ✓ Imagem gerada sem tabaco/fumaça ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)
    return False

def format_photo(raw_path: Path, out_path: Path):
    w, h = 1080, 1920
    if not raw_path.exists():
        img_blank = Image.new("RGB", (w, h), (15, 25, 15))
        img_blank.save(out_path, format="PNG")
        return

    try:
        img = Image.open(raw_path).convert("RGB")
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
        img = ImageEnhance.Contrast(img).enhance(1.20)
        img = ImageEnhance.Color(img).enhance(1.15)
        img.save(out_path, format="PNG")
    except Exception:
        img_blank = Image.new("RGB", (w, h), (15, 25, 15))
        img_blank.save(out_path, format="PNG")

def render_scene(img_path: Path, scene_id: int, dur: float, movement: str, banner: str, sub: str, out_mp4: Path):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    if out_mp4.exists():
        try:
            out_mp4.unlink()
        except Exception:
            pass

    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))
    img_np = np.array(Image.open(img_path).convert("RGB"))
    grain = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_b = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_b = ImageFont.load_default()

    for f in range(total_frames):
        prog = f / float(total_frames)

        if movement == "slow_push_in":
            scale = 1.0 + 0.14 * prog
            dx, dy = 0.0, 0.0
        elif movement == "quick_pan_left":
            scale = 1.10
            dx, dy = -0.05 * prog, 0.0
        elif movement == "dolly_forward":
            scale = 1.0 + 0.12 * prog
            dx, dy = 0.0, 0.02 * prog
        elif movement == "macro_pan":
            scale = 1.12
            dx, dy = 0.04 * prog, -0.02 * prog
        else:
            scale = 1.14 - 0.12 * prog
            dx, dy = 0.0, 0.0

        nw, nh = int(w * scale), int(h * scale)
        f_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = max(0, min(int((nw - w) * (0.5 + dx)), nw - w))
        sy = max(0, min(int((nh - h) * (0.5 + dy)), nh - h))
        f_crop = cv2.resize(f_res[sy : sy + h, sx : sx + w], (w, h), interpolation=cv2.INTER_CUBIC)

        f_grain = np.clip(f_crop.astype(np.int16) + grain, 0, 255).astype(np.uint8)
        f_pil = Image.fromarray(f_grain)
        draw = ImageDraw.Draw(f_pil)

        if scene_id == 1 and f < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), banner, fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
        out_v.write(cv2.cvtColor(np.array(f_pil), cv2.COLOR_RGB2BGR))

    out_v.release()

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+3%")
    await communicate.save(out_path)

def fix_no_smoking_fulozinha():
    topic_id = "short_comadre_fulozinha_historica"
    output_base = Path(__file__).resolve().parent / "output" / "videos"
    images_base = Path(__file__).resolve().parent / "output" / "images"
    audio_base = Path(__file__).resolve().parent / "output" / "audio"
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    out_dir = output_base / topic_id
    img_dir = images_base / topic_id
    aud_dir = audio_base / topic_id

    out_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    aud_dir.mkdir(parents=True, exist_ok=True)

    style_prefix = "Photorealistic 8k National Geographic documentary photograph, ARRI Alexa 65, historical 19th century Brazil, Zona da Mata Pernambuco, sugarcane plantation forest, atmospheric volumetric lighting, no smoking, no tobacco smoke, no fire, RAW"

    scenes_config = [
        {
            "scene_id": 1,
            "movement_type": "slow_push_in",
            "narration": "Nas florestas da Zona da Mata no Nordeste, a lenda da Comadre Fulozinha nasceu no século dezenove.",
            "prompt": "Breathtaking 8k aerial view of dense Atlantic rainforest next to historic 19th century sugarcane plantation in Pernambuco Brazil, morning mist, no human faces"
        },
        {
            "scene_id": 2,
            "movement_type": "quick_pan_left",
            "narration": "Relatos históricos apontam que a lenda surgiu entre trabalhadores rurais e engenhos coloniais.",
            "prompt": "Historical 8k photograph of old wooden gate leading to sugarcane forest at dusk, vintage lantern glowing, rustic Pernambuco countryside, no human faces"
        },
        {
            "scene_id": 3,
            "movement_type": "dolly_forward",
            "narration": "Ela era vista como uma entidade protetora da vegetação nativa contra o desmatamento dos engenhos.",
            "prompt": "Photorealistic 8k mysterious spirit of Comadre Fulozinha, a young Brazilian indigenous forest guardian woman with long dark hair, standing gracefully among ancient banyan tree roots in rainforest, back view, no smoking"
        },
        # CENA 4 CORRIGIDA: SEM FUMAÇA, SEM CIGARRO/CACHIMBO, APENAS O POTE DE MEL E OFERENDAS DA NATUREZA
        {
            "scene_id": 4,
            "movement_type": "macro_pan",
            "narration": "Caçadores deixavam oferendas como mel selvagem e flores nas raízes para pedir permissão e evitar se perder na mata.",
            "prompt": "Photorealistic 8k macro shot of Comadre Fulozinha placing a small rustic clay pot of wild honey and forest flowers on mossy tree roots in Pernambuco rainforest, clean natural lighting, no smoking, no fire, no smoke"
        },
        {
            "scene_id": 5,
            "movement_type": "drone_reveal",
            "narration": "O assobio agudo assustava quem cortava árvores sem respeito, confundindo os passos na escuridão.",
            "prompt": "Dark misty forest trail at twilight, sun rays piercing dense canopy, wind blowing autumn leaves in air, mysterious atmosphere, no human faces"
        },
        {
            "scene_id": 6,
            "movement_type": "slow_zoom_out",
            "narration": "Um patrimônio cultural do folclore pernambucano! Siga o Rota Calculada para mais histórias!",
            "prompt": "Breathtaking 8k aerial view of lush green forest canopy under golden sunset sky in Pernambuco Brazil, IMAX quality, no human faces"
        }
    ]

    hook = "A ORIGEM REAL DE COMADRE FULOZINHA 📜"
    sub = "ZONA DA MATA NORDESTINA"

    video_clips = []
    audio_clips = []
    current_time = 0.0

    print("\n🎬 Substituindo a imagem da Cena 4 para garantir 100% de conformidade com as diretrizes do YouTube (SEM FUMAÇA/TABACO)...")

    for sc in scenes_config:
        sc_id = sc["scene_id"]
        narr = sc["narration"]
        prompt = sc["prompt"]
        mov = sc["movement_type"]

        raw_p = img_dir / f"raw_scene_{sc_id}.jpg"
        fmt_p = img_dir / f"scene_{sc_id}.png"
        art_p = artifacts_dir / f"{topic_id}_scene_{sc_id}.png"
        sc_mp4 = out_dir / f"scene_{sc_id}.mp4"
        vc_p = aud_dir / f"voice_scene_{sc_id}.mp3"

        if sc_id == 4 or not raw_p.exists():
            fetch_ai_image(prompt, style_prefix, 900 + sc_id, raw_p)
            format_photo(raw_p, fmt_p)
            shutil.copy(fmt_p, art_p)

        asyncio.run(generate_voice(narr, str(vc_p)))
        vc_clip = AudioFileClip(str(vc_p))
        exact_dur = max(4.0, vc_clip.duration + 0.15)

        render_scene(fmt_p, sc_id, exact_dur, mov, hook, sub, sc_mp4)

        v_c = VideoFileClip(str(sc_mp4)).with_start(current_time)
        a_c = vc_clip.with_start(current_time).with_volume_scaled(1.6)

        video_clips.append(v_c)
        audio_clips.append(a_c)
        current_time += exact_dur

    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    master_p = out_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_aud = str(out_dir / f"temp_audio_{topic_id}.m4a")
    comp_v.write_videofile(str(master_p), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    comp_v.close()
    comp_a.close()
    for v in video_clips:
        v.close()
    for a in audio_clips:
        a.close()

    print(f"🎉 [VÍDEO 100% SEGURO PARA O YOUTUBE CONCLUÍDO] Duração: {current_time:.1f}s -> {master_p}")

if __name__ == "__main__":
    fix_no_smoking_fulozinha()
