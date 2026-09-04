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
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

# Safe UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

def fetch_wikimedia_fallback(query: str, out_path: Path) -> bool:
    encoded = urllib.parse.quote(query)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrlimit=6&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get('imageinfo', [])
                if imageinfo:
                    img_url = imageinfo[0].get('thumburl') or imageinfo[0].get('url')
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        with urllib.request.urlopen(urllib.request.Request(img_url, headers=HEADERS), timeout=12) as img_resp:
                            content = img_resp.read()
                            if len(content) > 10000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print(f"    ✓ [FOTO WIKIMEDIA OBTIDA] '{query}': {out_path.name}")
                                return True
    except Exception:
        pass
    return False

def fetch_ai_image_style(prompt: str, style_prefix: str, fallback_query: str, seed_id: int, out_path: Path) -> bool:
    enhanced_prompt = f"{style_prefix}, {prompt}, no watermark, high quality"
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + seed_id * 12345) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [IMAGEM IA ESTILO '{style_prefix[:20]}...'] Seed {seed_id}: ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)

    UNSPLASH_FALLBACKS = [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&h=1920&fit=crop&q=85",
        "https://images.unsplash.com/photo-1531384441138-2736e62e0919?w=1080&h=1920&fit=crop&q=85",
        "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1080&h=1920&fit=crop&q=85"
    ]
    fb_url = UNSPLASH_FALLBACKS[seed_id % len(UNSPLASH_FALLBACKS)]
    try:
        req = urllib.request.Request(fb_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            with open(out_path, "wb") as f:
                f.write(content)
            return True
    except Exception:
        return fetch_wikimedia_fallback(fallback_query, out_path)

def format_photo_to_916_hd(raw_img_path: Path, out_path: Path, style_mode: str = "doc"):
    w, h = 1080, 1920
    if not raw_img_path.exists():
        img_blank = Image.new("RGB", (w, h), (15, 25, 35))
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
        
        if style_mode == "doc":
            img = ImageEnhance.Contrast(img).enhance(1.25)
            img = ImageEnhance.Color(img).enhance(1.10)
            img = ImageEnhance.Sharpness(img).enhance(1.30)
        else:
            img = ImageEnhance.Contrast(img).enhance(1.30)
            img = ImageEnhance.Color(img).enhance(1.28)
            img = ImageEnhance.Sharpness(img).enhance(1.40)

        img.save(out_path, format="PNG")
    except Exception:
        img_blank = Image.new("RGB", (w, h), (15, 25, 35))
        img_blank.save(out_path, format="PNG")

def render_scene_clip(img_path: Path, scene_id: int, duration: float, movement_type: str, banner_text: str, sub_text: str, out_mp4_path: Path):
    if not img_path.exists():
        format_photo_to_916_hd(img_path, img_path)

    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)

    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    
    if out_mp4_path.exists():
        try:
            out_mp4_path.unlink()
        except Exception:
            pass

    out_v = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        if movement_type == "drone_reveal":
            scale = 1.18 - 0.15 * prog
            angle = -1.0 + 2.0 * prog
            dx, dy = 0.0, -0.04 * prog
        elif movement_type == "slow_push_in":
            scale = 1.0 + 0.16 * (prog ** 1.2)
            angle = 0.0
            dx, dy = 0.0, 0.0
        elif movement_type == "macro_pan":
            scale = 1.12
            angle = 0.0
            dx, dy = -0.05 * prog, 0.02 * prog
        else: # slow_zoom_out
            scale = 1.16 - 0.16 * prog
            angle = 0.5 - 1.0 * prog
            dx, dy = 0.0, 0.0

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)

        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), angle, 1.0)
        frame_rot = cv2.warpAffine(frame_res, M, (nw, nh), flags=cv2.INTER_CUBIC)

        sx = int((nw - w) * (0.5 + dx))
        sy = int((nh - h) * (0.5 + dy))

        sx = max(0, min(sx, nw - w))
        sy = max(0, min(sy, nh - h))

        frame_cropped = frame_rot[sy : sy + h, sx : sx + w].copy()
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)

        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        if scene_id == 1 and f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), banner_text, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub_text, fill=(255, 255, 255), font=font_banner, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE RENDERIZADO] Cena {scene_id} ({movement_type.upper()}) -> {duration:.1f}s")


SHORTS_SPECS = [
    {
        "topic_id": "short_ilha_das_cobras_1",
        "title": "Short 1: O Lugar Mais Proibido do Brasil! (Estilo Documentário Sombrio 8K)",
        "hook_text": "O LUGAR MAIS PROIBIDO DO BRASIL! 🚫🐍",
        "sub_text": "ILHA DA QUEIMADA GRANDE - SP",
        "style_mode": "doc",
        "style_prefix": "Photorealistic 8k National Geographic documentary photograph, ARRI Alexa 65 camera, 35mm lens, moody atmospheric lighting, dark cinematic chiaroscuro, ultra detailed, RAW",
        "scenes": [
            {
                "scene_id": 1,
                "movement_type": "drone_reveal",
                "narration": "Existe uma ilha no litoral de São Paulo onde a Marinha do Brasil proíbe estritamente a entrada de qualquer pessoa.",
                "fallback": "Queimada Grande island ocean cliffs",
                "prompt": "breathtaking aerial photograph of Ilha da Queimada Grande island in Atlantic ocean, steep jagged cliffs under dark moody storm clouds, navy patrol boat patrolling distant waters"
            },
            {
                "scene_id": 2,
                "movement_type": "macro_pan",
                "narration": "Na Ilha da Queimada Grande, conhecida como a Ilha das Cobras, vive a Jararaca-Ilhada, dona de um dos venenos mais letais do planeta. Dizem que há até cinco cobras por metro quadrado!",
                "fallback": "Golden lancehead snake forest rocks",
                "prompt": "extreme macro photograph of golden lancehead viper coiled around wet mossy rocks and thick rainforest leaves, yellow golden scales glowing under dark moonlight, shallow depth of field"
            },
            {
                "scene_id": 3,
                "movement_type": "slow_zoom_out",
                "narration": "Você teria coragem de navegar perto dessa ilha? Deixe nos comentários e siga o Rota Calculada!",
                "fallback": "Misty rocky island ocean wave",
                "prompt": "wide dramatic aerial view of forbidden rocky island engulfed in heavy sea mist at twilight, rough crashing waves, cinematic National Geographic style"
            }
        ]
    },
    {
        "topic_id": "short_ilha_das_cobras_2",
        "title": "Short 2: A Lenda do Último Faroleiro (Estilo Unreal Engine 5 Hyper-3D)",
        "hook_text": "A LENDA DO FAROL DA MORTE! 🕯️🐍",
        "sub_text": "MISTÉRIOS DA ILHA DAS COBRAS",
        "style_mode": "mythic",
        "style_prefix": "Unreal Engine 5 render, hyperrealistic 3D cinematic masterpiece, Octane render, ray tracing global illumination, Hollywood blockbuster VFX lighting, dramatic volumetric fog, 8k resolution",
        "scenes": [
            {
                "scene_id": 1,
                "movement_type": "slow_push_in",
                "narration": "Antes do farol da Ilha das Cobras ser automatizado, um faroleiro e sua família viviam isolados naquele rochedo no meio do oceano.",
                "fallback": "Lighthouse rocky island storm ocean",
                "prompt": "epic 3D render of vintage white stone lighthouse perched on tall jagged island cliff during violent lightning storm, glowing yellow beacon light cutting through dark rain clouds"
            },
            {
                "scene_id": 2,
                "movement_type": "macro_pan",
                "narration": "Conta a história popular que, em uma noite de tempestade, as cobras invadiram a casa pelas janelas. Desde aquele dia, ninguém mais morou lá e o farol funciona sozinho.",
                "fallback": "Interior lighthouse window snake storm",
                "prompt": "hyper-detailed 3D interior of old lighthouse room, golden vipers slithering over antique wooden desk and window frame, rain pouring outside glass with lightning flash"
            },
            {
                "scene_id": 3,
                "movement_type": "slow_zoom_out",
                "narration": "Você moraria em um lugar assim? Deixe seu comentário e siga o Rota Calculada para mais mistérios!",
                "fallback": "Lighthouse light beam night ocean storm",
                "prompt": "breathtaking 3D cinematic camera shot of automated lighthouse beam rotating over dark turbulent ocean at midnight, luminescent blue water highlights, IMAX blockbuster visual"
            }
        ]
    }
]


async def generate_narration_voice(text: str, out_path: str):
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+4%")
            await communicate.save(out_path)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 100:
                return
        except Exception:
            await asyncio.sleep(1.0)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        with open(out_path, "wb") as f:
            f.write(b"MOCK")


def produce_shorts_ilha_das_cobras():
    output_base = Path(__file__).resolve().parent / "output" / "videos"
    images_base = Path(__file__).resolve().parent / "output" / "images"
    audio_base = Path(__file__).resolve().parent / "output" / "audio"
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    print(f"\n==========================================")
    print(f"[RE-RENDERIZANDO 2 SHORTS DA ILHA DAS COBRAS EM ESTILOS VISUAIS DE IA TOTALMENTE DISTINTOS]")
    print(f"==========================================")

    results = []

    for s_idx, spec in enumerate(SHORTS_SPECS, 1):
        topic_id = spec["topic_id"]
        title_txt = spec["title"]
        hook_text = spec["hook_text"]
        sub_text = spec["sub_text"]
        style_prefix = spec["style_prefix"]
        style_mode = spec["style_mode"]
        scenes = spec["scenes"]

        output_dir = output_base / topic_id
        images_dir = images_base / topic_id
        audio_dir = audio_base / topic_id

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)

        video_clips = []
        audio_clips = []
        current_time = 0.0

        for sc in scenes:
            scene_id = sc["scene_id"]
            narration = sc["narration"]
            prompt_txt = sc["prompt"]
            fallback_query = sc["fallback"]
            mov_type = sc["movement_type"]

            raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
            formatted_img_path = images_dir / f"scene_{scene_id}.png"
            artifact_path = artifacts_dir / f"{topic_id}_style_scene_{scene_id}.png"
            scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
            voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

            fetch_ai_image_style(prompt_txt, style_prefix, fallback_query, s_idx * 100 + scene_id, raw_img_path)
            format_photo_to_916_hd(raw_img_path, formatted_img_path, style_mode)
            shutil.copy(formatted_img_path, artifact_path)

            asyncio.run(generate_narration_voice(narration, str(voice_path)))
            voice_clip = AudioFileClip(str(voice_path))
            exact_dur = voice_clip.duration + 0.25

            render_scene_clip(formatted_img_path, scene_id, exact_dur, mov_type, hook_text, sub_text, scene_mp4)

            v_clip = VideoFileClip(str(scene_mp4)).with_start(current_time)
            v_voice = voice_clip.with_start(current_time)

            video_clips.append(v_clip)
            audio_clips.append(v_voice.with_volume_scaled(1.6))

            current_time += exact_dur

        bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        if bgm_path.exists():
            raw_bgm = AudioFileClip(str(bgm_path))
            bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
            audio_clips.append(bgm_clip)

        master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
        comp_v = CompositeVideoClip(video_clips)
        comp_a = CompositeAudioClip(audio_clips)
        comp_v = comp_v.with_audio(comp_a)

        # Unique temporary audio filename per topic
        temp_audio = str(output_dir / f"temp_audio_{topic_id}.m4a")

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
        for vc in video_clips:
            vc.close()
        for ac in audio_clips:
            ac.close()

        print(f"\n  🎉 [{title_txt.upper()} CONCLUÍDO] ({current_time:.1f}s): {master_path}")
        results.append(master_path)

    return results


def main():
    produce_shorts_ilha_das_cobras()


if __name__ == "__main__":
    main()
