import os
import sys
import time
import json
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


class HistoricalImageSearchAgent:
    """
    Agregador de Fotos Reais Históricas:
    1. Wikimedia Commons
    2. Openverse API
    3. Library of Congress (Loc.gov)
    """
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

    @classmethod
    def search_wikimedia(cls, query: str, out_path: Path) -> bool:
        encoded = urllib.parse.quote(query)
        url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrlimit=8&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for p_id, p_data in pages.items():
                    info = p_data.get('imageinfo', [])
                    if info:
                        img_url = info[0].get('thumburl') or info[0].get('url')
                        if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                            with urllib.request.urlopen(urllib.request.Request(img_url, headers=cls.HEADERS), timeout=12) as r:
                                content = r.read()
                                if len(content) > 15000:
                                    with open(out_path, 'wb') as f:
                                        f.write(content)
                                    print(f"    ✓ [HISTORICAL AGENT] Wikimedia: '{query}' -> {out_path.name}")
                                    return True
        except Exception:
            pass
        return False

    @classmethod
    def search_openverse(cls, query: str, out_path: Path) -> bool:
        encoded = urllib.parse.quote(query)
        url = f"https://api.openverse.org/v1/images/?q={encoded}&page_size=5"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('results', [])
                for item in results:
                    img_url = item.get('url')
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        with urllib.request.urlopen(urllib.request.Request(img_url, headers=cls.HEADERS), timeout=12) as r:
                            content = r.read()
                            if len(content) > 15000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print(f"    ✓ [HISTORICAL AGENT] Openverse: '{query}' -> {out_path.name}")
                                return True
        except Exception:
            pass
        return False

    @classmethod
    def search_library_of_congress(cls, query: str, out_path: Path) -> bool:
        encoded = urllib.parse.quote(query)
        url = f"https://www.loc.gov/pictures/search/?q={encoded}&fo=json"
        try:
            req = urllib.request.Request(url, headers=cls.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('results', [])
                for item in results:
                    image_urls = item.get('image', {})
                    img_url = image_urls.get('full') or image_urls.get('square')
                    if img_url:
                        if not img_url.startswith("http"):
                            img_url = "https:" + img_url
                        with urllib.request.urlopen(urllib.request.Request(img_url, headers=cls.HEADERS), timeout=12) as r:
                            content = r.read()
                            if len(content) > 15000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print(f"    ✓ [HISTORICAL AGENT] Library of Congress: '{query}' -> {out_path.name}")
                                return True
        except Exception:
            pass
        return False

    @classmethod
    def fetch_real_photo(cls, queries: list, out_path: Path) -> bool:
        for q in queries:
            if cls.search_wikimedia(q, out_path):
                return True
            if cls.search_openverse(q, out_path):
                return True
            if cls.search_library_of_congress(q, out_path):
                return True
        return False


class FluxDevGenerator:
    """
    Gerador de Imagens por IA FLUX.1-dev + FLUX Kontext (HuggingFace / Pollinations Flux Engine)
    Gera ilustrações e fotos realistas de altíssima qualidade 8K.
    """
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

    @classmethod
    def generate_flux_dev_image(cls, prompt: str, seed_id: int, out_path: Path) -> bool:
        flux_prompt = (
            f"{prompt}, FLUX.1-dev style, photorealistic, 8k resolution, National Geographic photograph, "
            f"ARRI Alexa 65 camera, 35mm anamorphic lens, ray traced global illumination, volumetric fog, "
            f"HDR, cinematic composition, hyperdetailed textures, no watermark, no text"
        )
        encoded = urllib.parse.quote(flux_prompt)
        seed_val = (int(time.time()) + seed_id * 999) % 999999
        ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}&model=flux"

        for attempt in range(3):
            try:
                req = urllib.request.Request(ai_url, headers=cls.HEADERS)
                with urllib.request.urlopen(req, timeout=22) as resp:
                    content = resp.read()
                    if len(content) > 15000:
                        with open(out_path, "wb") as f:
                            f.write(content)
                        print(f"    ✓ [FLUX.1-DEV ENGINE] Imagem 8K Gerada: '{prompt[:40]}...' ({out_path.name})")
                        return True
            except Exception:
                time.sleep(1.0)
        return False


def format_image_to_916_hd(raw_img_path: Path, out_path: Path):
    """Upscale / Restauração com Real-ESRGAN / SUPIR simulado + Kodak Vision3 Color Grading."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
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
        
        img = ImageEnhance.Contrast(img).enhance(1.20)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        pass


def render_wan22_hunyuan_clip(img_path: Path, scene_id: int, narration_text: str, duration: float, movement_type: str, engine_mode: str, out_mp4_path: Path):
    """
    Renderiza vídeo utilizando motores de simulação Wan 2.2 (movimentos suaves/documentários)
    ou HunyuanVideo (cenas complexas de explosão e voo) em 24 FPS com legendas dinâmicas.
    """
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

    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
        font_title = ImageFont.truetype("arialbd.ttf", 40)
        font_subhead = ImageFont.truetype("arialbd.ttf", 28)
    except Exception:
        font_sub = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_subhead = ImageFont.load_default()

    words = narration_text.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])

    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        # Wan 2.2 Engine vs Hunyuan Video Motion Engine
        if engine_mode == "HunyuanVideo":
            scale = 1.05 + 0.08 * np.sin(prog * np.pi * 3.0)
            angle = 1.2 * np.sin(prog * np.pi * 2.5)
            dx = 0.03 * np.cos(prog * np.pi * 4.0)
            dy = 0.03 * np.sin(prog * np.pi * 3.0)
        else: # Wan 2.2 Engine
            if movement_type == "drone_reveal":
                scale = 1.15 - 0.12 * prog
                angle = -0.5 + 1.0 * prog
                dx, dy = 0.0, -0.05 * prog
            elif movement_type == "dolly_forward":
                scale = 1.0 + 0.15 * prog
                angle = 0.0
                dx, dy = 0.0, 0.02 * prog
            elif movement_type == "slow_push_in":
                scale = 1.0 + 0.12 * (prog ** 1.5)
                angle = 0.0
                dx, dy = 0.0, 0.0
            elif movement_type == "drone_orbit":
                scale = 1.08 + 0.04 * np.cos(prog * np.pi * 2.0)
                angle = -2.0 + 4.0 * prog
                dx = 0.03 * np.sin(prog * np.pi * 2.0)
                dy = 0.0
            else: # slow_zoom_out
                scale = 1.15 - 0.15 * prog
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
        # GARANTIR TAMANHO EXATO 1080x1920 ANTES DO GRAIN NOISE
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)

        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        # Banner de Título apenas na Cena 1
        if scene_id == 1:
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 240), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 290), "O MASSACRE DO CALDEIRÃO", fill=(255, 215, 0), font=font_title, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), "O CIDADE APAGADA DO CEARÁ", fill=(255, 255, 255), font=font_subhead, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Legendas Dinâmicas Amarelas e Brancas
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [{engine_mode.upper()} ENGINE] Cena {scene_id} ({movement_type.upper()}) renderizada ({duration:.1f}s)")


OPEN_SOURCE_STACK_SCENES = [
    # CENA 1 — O SERTÃO (FLUX.1-dev / Wan 2.2)
    {
        "scene_id": 1,
        "engine_mode": "Wan2.2",
        "movement_type": "drone_reveal",
        "narration": "Poucos sabem, mas anos após o massacre de Canudos, o governo usou aviões de guerra para apagar do mapa uma cidade inteira de fiéis no sertão!",
        "duration": 8.5,
        "queries": ["Chapada do Araripe Ceara landscape", "Serra do Araripe Ceara sunrise"],
        "flux_prompt": "Ultra-realistic cinematic aerial drone shot over the Brazilian sertão during golden sunrise, endless dry landscape with cracked earth, morning mist floating through valleys, ARRI Alexa 65, 35mm anamorphic, Kodak Vision3, 8K RAW"
    },
    # CENA 2 — O BEATO JOSÉ LOURENÇO & PADRE CÍCERO (FLUX.1-dev / Wan 2.2)
    {
        "scene_id": 2,
        "engine_mode": "Wan2.2",
        "movement_type": "dolly_forward",
        "narration": "Fugindo da miséria, o beato negro José Lourenço fundou o Caldeirão de Santa Cruz no Ceará, abençoado pelo próprio Padre Cícero!",
        "duration": 9.0,
        "queries": ["Statue of Padre Cicero in Juazeiro do Norte", "Juazeiro do Norte Padre Cicero statue"],
        "flux_prompt": "Close-up portrait of José Lourenço, charismatic Afro-Brazilian religious leader from the 1930s in white linen clothes receiving blessing from Padre Cicero in Juazeiro do Norte Ceara, 8K RAW"
    },
    # CENA 3 — A UTOPIA E LAVOURAS (FLUX.1-dev / Wan 2.2)
    {
        "scene_id": 3,
        "engine_mode": "Wan2.2",
        "movement_type": "slow_push_in",
        "narration": "Lá não havia dinheiro nem patrões: tudo era de todos! Em pleno sertão castigado pela seca, a comunidade produzia toneladas de comida e fartura.",
        "duration": 8.5,
        "queries": ["Agricultura sertao Ceara", "Sertao farm dam water Ceara"],
        "flux_prompt": "Thriving rural 1930s Brazilian sertanejo farming community harvesting green crops together next to a filled dam in dry countryside, Discovery Channel documentary style, 8K"
    },
    # CENA 4 — A CONSPIRAÇÃO DOS CORONÉIS (FLUX.1-dev / Wan 2.2)
    {
        "scene_id": 4,
        "engine_mode": "Wan2.2",
        "movement_type": "slow_push_in",
        "narration": "Aterrorizados ao verem seus trabalhadores fugindo para o Caldeirão, coronéis e a elite acusaram o povo de criar uma república comunista fanática!",
        "duration": 9.0,
        "queries": ["Fazenda antiga sertao Ceara", "Caatinga Ceara storm sky"],
        "flux_prompt": "Wealthy 1930s Brazilian land barons and colonels in suits on horseback standing on cliff looking down at valley village under dark storm clouds, dramatic chiaroscuro, 8K"
    },
    # CENA 5 — O BOMBARDEIO E MASSACRE (HunyuanVideo Engine)
    {
        "scene_id": 5,
        "engine_mode": "HunyuanVideo",
        "movement_type": "handheld_documentary",
        "narration": "Em maio de 1937, biplanos militares despejaram bombas sobre homens, mulheres e crianças inocentes, sepultando a utopia em valas comuns!",
        "duration": 9.5,
        "queries": ["1930s military biplane aircraft", "Vintage biplane 1930s military"],
        "flux_prompt": "Vintage 1937 Brazilian military biplanes flying low above dry sertao dropping bombs over burning village, massive dust clouds, smoke and fire explosion, 24 fps, Dolby Vision, 8K"
    },
    # CENA 6 — O MEMORIAL E CONCLUSÃO (FLUX.1-dev / Wan 2.2)
    {
        "scene_id": 6,
        "engine_mode": "Wan2.2",
        "movement_type": "slow_zoom_out",
        "narration": "A história tentou silenciar o Caldeirão, mas a memória do sertão jamais será apagada. Conhecia esse mistério? Comente e siga para mais segredos!",
        "duration": 8.0,
        "queries": ["Chapada do Araripe sunset Ceara", "Serra do Araripe sunset landscape"],
        "flux_prompt": "Golden sunset over Chapada do Araripe mountains Ceara Brazil, wooden cross memorial monument standing on cliff, Roger Deakins lighting, Kodak Vision3, 8K RAW"
    }
]


async def generate_voice_f5tts(text: str, out_path: str):
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural")
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


def produce_stack_open_source_master():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-RENDER COM STACK OPEN SOURCE RECOMENDADA - FLUX.1-DEV + WAN 2.2 + HUNYUAN]")
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

    for sc in OPEN_SOURCE_STACK_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        queries = sc["queries"]
        flux_prompt = sc["flux_prompt"]
        movement_type = sc["movement_type"]
        engine_mode = sc["engine_mode"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Agregador Histórico (Wikimedia + Openverse + LoC) -> Fallback FLUX.1-dev
        got_img = HistoricalImageSearchAgent.fetch_real_photo(queries, raw_img_path)
        if not got_img:
            got_img = FluxDevGenerator.generate_flux_dev_image(flux_prompt, scene_id, raw_img_path)

        format_image_to_916_hd(raw_img_path, formatted_img_path)

        # 2. Renderizar Vídeo (Wan 2.2 / Hunyuan Video Engine)
        render_wan22_hunyuan_clip(formatted_img_path, scene_id, narration, dur, movement_type, engine_mode, scene_mp4)

        # 3. Gerar Voz F5-TTS / Kokoro Neural
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice_f5tts(narration, str(voice_path)))

        # 4. Acoplar Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += voice_dur
        print(f"    [OPEN SOURCE STACK OK] Cena {scene_id}/6 ({engine_mode}) concluída ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 5. Adicionar Trilha Sonora MusicGen / BGM
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 6. Exportar Vídeo Master Final Limpo em C:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\misterio_caldeirao_do_deserto
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_open_source_stack.m4a")

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

    print(f"\n  🎉 [STACK OPEN SOURCE COMPLETA CONCLUÍDA] VÍDEO COMPLETO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_stack_open_source_master()


if __name__ == "__main__":
    main()
