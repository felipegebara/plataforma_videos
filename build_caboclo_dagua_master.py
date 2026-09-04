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

def fetch_ai_image_8k(prompt: str, fallback_query: str, scene_id: int, out_path: Path) -> bool:
    enhanced_prompt = (
        f"{prompt}, photorealistic 8k resolution, National Geographic documentary photograph, "
        f"ARRI Alexa 65 camera, 35mm anamorphic lens, ray traced global illumination, "
        f"volumetric lighting, cinematic composition, depth of field, HDR, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + scene_id * 9999) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [IMAGEM IA 8K GERADA] Cena {scene_id}: '{prompt[:45]}...' ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)

    # Fallback to unsplash HD direct photo if AI times out
    UNSPLASH_FALLBACKS = {
        1: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=85",
        2: "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1080&h=1920&fit=crop&q=85",
        3: "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1080&h=1920&fit=crop&q=85",
        4: "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1080&h=1920&fit=crop&q=85"
    }
    fallback_url = UNSPLASH_FALLBACKS.get(scene_id, UNSPLASH_FALLBACKS[1])
    try:
        req = urllib.request.Request(fallback_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            with open(out_path, "wb") as f:
                f.write(content)
            print(f"    ✓ [FOTO FALLBACK UNSPLASH OBTIDA] Cena {scene_id}: {out_path.name}")
            return True
    except Exception:
        return fetch_wikimedia_fallback(fallback_query, out_path)

def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    w, h = 1080, 1920
    if not raw_img_path.exists():
        img_blank = Image.new("RGB", (w, h), (15, 20, 35))
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
        
        # Color grading
        img = ImageEnhance.Contrast(img).enhance(1.22)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        img_blank = Image.new("RGB", (w, h), (15, 20, 35))
        img_blank.save(out_path, format="PNG")

def render_scene_clip(img_path: Path, scene_id: int, duration: float, movement_type: str, banner_text: str, out_mp4_path: Path):
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

        if movement_type == "slow_push_in":
            scale = 1.0 + 0.16 * (prog ** 1.2)
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

        # BANNER DE TEXTO IMPACTANTE
        if banner_text:
            draw.rectangle([(0, 260), (1080, 420)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 420)], fill=(255, 215, 0))
            draw.text((540, 340), banner_text, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada Cinematográfica
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE CABOCLO D'ÁGUA RENDERIZADO] Cena {scene_id} ({movement_type.upper()}) -> {duration:.1f}s")


# ROTEIRO SOLICITADO (4 SEÇÕES — ~40 SEGUNDOS EXATOS)
CABOCLO_DAGUA_SCENES = [
    # SEÇÃO 1 [0:00 - 0:04] GANCHO (HOOK)
    {
        "scene_id": 1,
        "movement_type": "slow_push_in",
        "banner_text": "O MONSTRO DO VELHO CHICO 🐊⚠️",
        "narration": "Nas profundezas mais escuras do Rio São Francisco, vive uma criatura que tira o sono dos pescadores há gerações.",
        "duration": 4.5,
        "fallback": "Rio Sao Francisco night river canoe",
        "prompt": "Breathtaking 8k photograph of dark deep waters of Rio Sao Francisco river at moody dusk, solitary traditional wooden canoe floating, pair of terrifying glowing red eyes submerged beneath dark water surface, ARRI Alexa 65"
    },
    # SEÇÃO 2 [0:04 - 0:18] O MITO E O TERROR
    {
        "scene_id": 2,
        "movement_type": "quick_pan_left",
        "banner_text": "Olhos vermelhos e garras afiadas 👁️",
        "narration": "O Caboclo d'Água é o guardião implacável do rio. Um ser anfíbio de olhos vermelhos incandescentes, famoso por subir à superfície apenas para virar barcos e arrastar os incautos para o fundo.",
        "duration": 14.0,
        "fallback": "Underwater river monster whirlpool",
        "prompt": "Hyperrealistic 8k cinematic shot of Caboclo d'Agua, terrifying muscular amphibious humanoid river monster with dark leathery skin and glowing red eyes, sharp claws pulling a fishing net underwater into deep river whirlpools, National Geographic documentary style"
    },
    # SEÇÃO 3 [0:18 - 0:30] O SEGREDO DOS RIBEIRINHOS (O RITUAL DA FACA)
    {
        "scene_id": 3,
        "movement_type": "dolly_forward",
        "banner_text": "O RITUAL DE SOBREVIVÊNCIA 🔪",
        "narration": "Mas o que torna essa lenda real é o desespero de quem vive lá: até hoje, os barqueiros cravam uma faca afiada no fundo da canoa...",
        "duration": 12.0,
        "fallback": "Fisherman stabbing knife in wooden canoe",
        "prompt": "Hyperrealistic 8k macro photograph of weathered river fisherman hands stabbing a sharp steel knife into wooden floor of canoe, metallic reflection, moody night lighting, dramatic chiaroscuro"
    },
    # SEÇÃO 4 [0:30 - 0:40] FECHAMENTO & CTA
    {
        "scene_id": 4,
        "movement_type": "slow_zoom_out",
        "banner_text": "Você teria coragem? 👇 / @RotaCalculada",
        "narration": "...porque dizem que o monstro foge ao ver o brilho do aço. Você teria coragem de navegar no Velho Chico à noite? Siga o Rota Calculada!",
        "duration": 10.0,
        "fallback": "Rio Sao Francisco starry night canoe",
        "prompt": "Breathtaking 8k wide aerial photograph of traditional wooden canoe navigating safely on vast Rio Sao Francisco river under starry night sky, golden moonlight reflecting on water, IMAX quality"
    }
]


async def generate_narration_voice(text: str, out_path: str):
    """Gera locução neural documentária limpa."""
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+5%")
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


def produce_caboclo_dagua_master():
    topic_id = "short_caboclo_dagua"
    print(f"\n==========================================")
    print(f"[PRODUÇÃO DO VÍDEO MASTER: O CABOCLO D'ÁGUA DO RIO SÃO FRANCISCO (~40s)]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in CABOCLO_DAGUA_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        fallback_query = sc["fallback"]
        mov_type = sc["movement_type"]
        banner_text = sc["banner_text"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        artifact_path = artifacts_dir / f"caboclo_dagua_scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        # 1. Gerar Imagem por IA 8K
        fetch_ai_image_8k(prompt_txt, fallback_query, scene_id, raw_img_path)
        format_photo_to_916_hd(raw_img_path, formatted_img_path)
        shutil.copy(formatted_img_path, artifact_path)

        # 2. Gerar Voz Neural Documentária
        asyncio.run(generate_narration_voice(narration, str(voice_path)))

        # 3. Medir duração exata do áudio
        voice_clip = AudioFileClip(str(voice_path))
        exact_dur = voice_clip.duration + 0.15

        # 4. Renderizar Clipe 24 FPS
        render_scene_clip(formatted_img_path, scene_id, exact_dur, mov_type, banner_text, scene_mp4)

        # 5. Acoplar Vídeo e Áudio
        v_clip = VideoFileClip(str(scene_mp4)).with_start(current_time)
        voice_clip = voice_clip.with_start(current_time)

        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += exact_dur
        print(f"    [CABOCLO D'ÁGUA CENA OK] Cena {scene_id}/4 ({exact_dur:.2f}s | Total: {current_time:.1f}s)")

    # 6. Trilha Sonora de Mistério e Efeitos Sonoros
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.14)
        audio_clips.append(bgm_clip)

    # 7. Exportar Vídeo Master Final
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_caboclo.m4a")

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

    print(f"\n  🎉 [PRODUÇÃO CABOCLO D'ÁGUA CONCLUÍDA] DURAÇÃO TOTAL EXATA ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_caboclo_dagua_master()


if __name__ == "__main__":
    main()
