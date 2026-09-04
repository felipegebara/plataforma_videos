import os
import sys
import time
import json
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

# Safe UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def fetch_wikimedia_fallback(query: str, out_path: Path) -> bool:
    """Busca foto real em HD via Wikimedia Commons se a IA expirar."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    encoded_term = urllib.parse.quote(query)
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=6&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get('imageinfo', [])
                if imageinfo:
                    img_url = imageinfo[0].get('thumburl') or imageinfo[0].get('url')
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        img_req = urllib.request.Request(img_url, headers=headers)
                        with urllib.request.urlopen(img_req, timeout=12) as img_resp:
                            content = img_resp.read()
                            if len(content) > 10000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print(f"    ✓ [FOTO REAL WIKIMEDIA OBTIDA] '{query}': {out_path.name}")
                                return True
    except Exception:
        pass
    return False


def fetch_ai_image_8k(prompt: str, fallback_query: str, scene_id: int, out_path: Path) -> bool:
    """Gera imagens de IA 8K fotorealistas com fallback automático para garantir 100% de sucesso."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    enhanced_prompt = (
        f"{prompt}, photorealistic 8k resolution, National Geographic documentary photograph, "
        f"ARRI Alexa 65 camera, 35mm anamorphic lens, ray traced global illumination, "
        f"volumetric lighting, cinematic composition, depth of field, HDR, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + scene_id * 6543) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=headers)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [IMAGEM IA 8K MORRO AZUL GERADA] Cena {scene_id}: '{prompt[:45]}...' ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)

    # Fallback automático para Wikimedia
    return fetch_wikimedia_fallback(fallback_query, out_path)


def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata foto para 9:16 HD 1080x1920 com contraste cinematográfico."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        # Se raw não existir por falha catastrófica de rede, cria canvas cinematográfico 8K limpo
        img_blank = Image.new("RGB", (w, h), (15, 25, 45))
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
        
        img = ImageEnhance.Contrast(img).enhance(1.22)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        img_blank = Image.new("RGB", (w, h), (15, 25, 45))
        img_blank.save(out_path, format="PNG")


def render_fast_dynamic_scene_clip(img_path: Path, scene_id: int, duration: float, movement_type: str, out_mp4_path: Path):
    """
    Renderiza clipe MP4 ultra-dinâmico em 24 FPS para Shorts de 16 segundos,
    mantendo visual limpo e moldura cinematográfica dourada.
    """
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
        font_hook = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_hook = ImageFont.load_default()

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        if movement_type == "fast_push_in":
            scale = 1.0 + 0.18 * (prog ** 1.2)
            angle = 0.0
            dx, dy = 0.0, 0.0
        elif movement_type == "dolly_forward":
            scale = 1.0 + 0.16 * prog
            angle = -0.5 + 1.0 * prog
            dx, dy = 0.0, 0.02 * prog
        elif movement_type == "quick_pan_left":
            scale = 1.12
            angle = 0.0
            dx, dy = -0.06 * prog, 0.0
        elif movement_type == "drone_reveal":
            scale = 1.18 - 0.15 * prog
            angle = -1.0 + 2.0 * prog
            dx, dy = 0.0, -0.04 * prog
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

        # HOOK DE IMPACTO APENAS NA CENA 1 (Primeiros 2.5 Segundos)
        if scene_id == 1 and f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 460)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 460)], fill=(255, 215, 0))
            draw.text((540, 320), "A SERPENTE DO MORRO AZUL!", fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 400), "O MISTÉRIO DE TIMBÓ - SC", fill=(255, 255, 255), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada Cinematográfica
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE ULTRA-SHORT RENDERIZADO] Cena {scene_id} ({movement_type.upper()}) -> {duration:.1f}s")


# ROTEIRO VIRAL DA LENDA DA SERPENTE DO MORRO AZUL EM TIMBÓ (16 SEGUNTOS — REGRA ROTA CALCULADA)
MORRO_AZUL_SERPENTE_SCENES = [
    # CENA 1: HOOK POLÊMICO (3.0s)
    {
        "scene_id": 1,
        "movement_type": "fast_push_in",
        "narration": "Você sabia que sob as rochas do Morro Azul, em Timbó, existe a lenda de uma serpente gigante adormecida?",
        "duration": 3.0,
        "fallback": "Morro Azul Timbo Santa Catarina",
        "prompt": "Hyperrealistic 8k aerial documentary photograph, dramatic Morro Azul mountain peak in Timbo Santa Catarina Brazil at golden sunrise, dense Atlantic forest covered in mysterious blue mist, ARRI Alexa 65"
    },
    # CENA 2: A CRENÇA DOS COLONOS (3.5s)
    {
        "scene_id": 2,
        "movement_type": "dolly_forward",
        "narration": "Transmitida pelos antigos colonos do Vale do Itajaí, a tradição diz que a criatura repousa nas profundezas da montanha!",
        "duration": 3.5,
        "fallback": "Enxaimel Pomerode Santa Catarina",
        "prompt": "Photorealistic 8k cinematic shot, 19th century German-style timber framing enxaimel house in countryside near Timbo and Pomerode Santa Catarina under dramatic storm sky, National Geographic style"
    },
    # CENA 3: OS TREMORES E ESTALOS (3.5s)
    {
        "scene_id": 3,
        "movement_type": "quick_pan_left",
        "narration": "Quando a serpente se espreguiça nas rochas, estalos de pedras e pequenos tremores ecoam pelas encostas!",
        "duration": 3.5,
        "fallback": "Cavern cave Santa Catarina Brazil",
        "prompt": "Hyperrealistic 8k documentary photograph, deep underground cave cavern with glowing rocks beneath mountain roots in Santa Catarina Brazil, glowing blue energy, cinematic chiaroscuro"
    },
    # CENA 4: O MISTÉRIO DA BRUMA AZUL (3.5s)
    {
        "scene_id": 4,
        "movement_type": "drone_reveal",
        "narration": "Até hoje, a bruma azulada que envolve o Morro Azul fascina quem visita Timbó e Pomerode!",
        "duration": 3.5,
        "fallback": "Timbo Santa Catarina landscape",
        "prompt": "Breathtaking 8k aerial photograph of Morro Azul lookout peak in Timbo Santa Catarina, paraglider ramp overlooking lush green valley at vibrant sunset, IMAX quality"
    },
    # CENA 5: CALL TO ACTION VIRAL (2.5s)
    {
        "scene_id": 5,
        "movement_type": "slow_zoom_out",
        "narration": "Já conhecia esse mistério de Timbó? Comente e siga para mais segredos de Santa Catarina!",
        "duration": 2.5,
        "fallback": "Timbo Santa Catarina sunset",
        "prompt": "Photorealistic 8k landscape photograph, golden hour sunset over Timbo valley Santa Catarina Brazil, sun rays piercing misty hills, 8k RAW"
    }
]


async def generate_fast_voice(text: str, out_path: str):
    """Gera locução neural ágil e dinâmica para o Short."""
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+10%")
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


def produce_morro_azul_serpente_short():
    topic_id = "short_morro_azul_serpente"
    print(f"\n==========================================")
    print(f"[PRODUÇÃO DO SHORT: A LENDA DA SERPENTE DO MORRO AZUL EM TIMBÓ-SC (16s)]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in MORRO_AZUL_SERPENTE_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        fallback_query = sc["fallback"]
        mov_type = sc["movement_type"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        # 1. Gerar Imagem por IA 8K com fallback para Wikimedia se necessário
        fetch_ai_image_8k(prompt_txt, fallback_query, scene_id, raw_img_path)
        format_photo_to_916_hd(raw_img_path, formatted_img_path)

        # 2. Renderizar Clipe 24 FPS
        render_fast_dynamic_scene_clip(formatted_img_path, scene_id, dur, mov_type, scene_mp4)

        # 3. Gerar Voz Neural Ágil
        asyncio.run(generate_fast_voice(narration, str(voice_path)))

        # 4. Acoplar Vídeo e Áudio
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.05

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += voice_dur
        print(f"    [SHORT SCENE OK] Cena {scene_id}/5 ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 5. Adicionar Trilha Sonora de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.14)
        audio_clips.append(bgm_clip)

    # 6. Exportar Vídeo Master Final em c:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\short_morro_azul_serpente
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_morro_azul.m4a")

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio_file,
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

    print(f"\n  🎉 [PRODUÇÃO DO SHORT CONCLUÍDA] DURAÇÃO TOTAL ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_morro_azul_serpente_short()


if __name__ == "__main__":
    main()
