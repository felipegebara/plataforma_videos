import os
import sys
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

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def fetch_wikimedia_photorealistic_hd(query_terms: list, out_path: Path) -> bool:
    """Busca FOTOS REALISTAS EM ALTA DEFINIÇÃO (1280px) via Wikimedia Commons API."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    
    for term in query_terms:
        encoded_term = urllib.parse.quote(term)
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=12&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    imageinfo = page_data.get('imageinfo', [])
                    if imageinfo:
                        img_url = imageinfo[0].get('thumburl') or imageinfo[0].get('url')
                        if img_url and any(img_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                            img_req = urllib.request.Request(img_url, headers=headers)
                            with urllib.request.urlopen(img_req, timeout=12) as img_resp:
                                with open(out_path, 'wb') as f:
                                    f.write(img_resp.read())
                            print(f"    ✓ Foto REALISTA HD Obtida com Sucesso: '{term}' ({out_path.name})")
                            return True
        except Exception:
            pass
    return False


def fetch_photorealistic_ai_fallback(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera fotografia hiper-realista em 8K via Pollinations AI Engine caso a foto histórica falhe."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(f"{prompt}, National Geographic photograph 8k resolution, photorealistic, 35mm lens, sharp focus, natural daylight")
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={105000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=16) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ Fotografia Hiper-Realista por IA obtida: '{prompt[:40]}...'")
                return True
    except Exception:
        pass
    return False


def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata foto para 9:16 HD 1080x1920 com crop perfeito e tratamento fotográfico."""
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
        
        # Tratamento fotográfico
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        pass


def render_photorealistic_scene_clip(img_path: Path, scene_id: int, narration_text: str, duration: float, out_mp4_path: Path):
    """
    Renderiza o clipe MP4 com a FOTO REALISTA HD, movimento de câmera parallax 24 FPS,
    legendas dinâmicas amarelas/brancas e moldura de cinema dourada.
    """
    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)

    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
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

        # Movimento Cinematográfico Suave de Foto Realista
        scale = 1.0 + 0.10 * np.sin(prog * np.pi * 0.5)
        angle = -0.8 + 1.6 * prog

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)

        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), angle, 1.0)
        frame_rot = cv2.warpAffine(frame_res, M, (nw, nh), flags=cv2.INTER_CUBIC)

        sx = int((nw - w) * (0.5 + 0.3 * np.cos(prog * np.pi)))
        sy = int((nh - h) * (0.5 + 0.3 * np.sin(prog * np.pi)))

        sx = max(0, min(sx, nw - w))
        sy = max(0, min(sy, nh - h))

        frame_cropped = frame_rot[sy : sy + h, sx : sx + w].copy()
        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        # 1. Banner Principal de Título APENAS na Cena 1 (Sem Marcas d'Água de Modelos!)
        if scene_id == 1:
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 240), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 290), "O CALDEIRÃO DE SANTA CRUZ", fill=(255, 215, 0), font=font_title, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), "O SEGUNDO CANUDOS DO SERTÃO", fill=(255, 255, 255), font=font_subhead, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # 2. Legendas Dinâmicas Amarelas e Brancas da Narração
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # 3. Moldura Dourada Elegante
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [FOTO REALISTA CLIP OK] Cena {scene_id} renderizada em 24 FPS ({duration:.1f}s)")


PHOTOREALISTIC_SCENES = [
    # CENA 1: Foto REAL HD da Serra do Araripe no Ceará
    {
        "scene_id": 1,
        "narration": "Você sabia que anos após a destruição de Canudos, o sertão do Ceará viveu outro império de fé e tragédia esquecido pela história?",
        "duration": 8.5,
        "queries": ["Serra do Araripe Crato Ceara", "Chapada do Araripe Ceara landscape", "Caatinga Ceara Brazil landscape"],
        "ai_prompt": "National Geographic 8k photograph of Serra do Araripe mountains at golden sunrise in Ceara Brazil sertao"
    },
    # CENA 2: Foto REAL HD da Estátua do Padre Cícero em Juazeiro do Norte
    {
        "scene_id": 2,
        "narration": "Na década de 1920, o Beato José Lourenço fundou na Serra do Araripe a comunidade do Caldeirão de Santa Cruz, sob benção do Padre Cícero.",
        "duration": 9.0,
        "queries": ["Statue of Padre Cicero in Juazeiro do Norte", "Estatua de Padre Cicero Horto Juazeiro", "Padre Cicero Juazeiro do Norte Ceara"],
        "ai_prompt": "High resolution photograph of the Statue of Padre Cicero in Juazeiro do Norte Ceara Brazil at sunset"
    },
    # CENA 3: Foto REAL HD de Lavouras e Agricultores no Sertão do Ceará
    {
        "scene_id": 3,
        "narration": "Milhares de sertanejos miseráveis migraram para lá, criando uma sociedade igualitária com lavouras prósperas no meio da seca.",
        "duration": 8.5,
        "queries": ["Agricultura sertao Ceara", "Sertao farm dam water Ceara", "Sertao farm Brazil historical"],
        "ai_prompt": "National Geographic photograph of poor 1930s Brazilian farmers working together in green crops in Ceara sertao"
    },
    # CENA 4: Foto REAL HD de Fazenda Antiga e Paisagem da Caatinga sob Tempestade
    {
        "scene_id": 4,
        "narration": "Assustados com o poder daquela comunidade que lembrava o Arraial de Canudos, autoridades e fazendeiros acusaram o povo de fanatismo.",
        "duration": 9.0,
        "queries": ["Fazenda antiga sertao Ceara", "Sertao Ceara landscape", "Caatinga Ceara storm sky"],
        "ai_prompt": "Authentic historical photograph of 1930s Brazilian sertao land barons on horseback in dry countryside"
    },
    # CENA 5: Foto REAL HD Histórica de Biplanos Militares dos Anos 1930
    {
        "scene_id": 5,
        "narration": "Em 1937, a Força Pública e aviões militares bombardearam o Caldeirão, destruindo o arraial e sepultando uma das maiores utopias do sertão.",
        "duration": 9.5,
        "queries": ["1930s military biplane aircraft", "Vintage biplane 1930s military", "1930s military airplane"],
        "ai_prompt": "Historical photograph of 1930s military biplane airplane in dark sky over Brazilian countryside with smoke"
    },
    # CENA 6: Foto REAL HD Espetacular do Pôr do Sol na Chapada do Araripe
    {
        "scene_id": 6,
        "narration": "Conhecia a impressionante história do Caldeirão do Ceará? Deixe seu comentário e siga o canal para mais histórias épicas!",
        "duration": 8.0,
        "queries": ["Chapada do Araripe sunset Ceara", "Serra do Araripe sunset landscape", "Rio Sao Francisco sunset Pernambuco"],
        "ai_prompt": "National Geographic golden sunset photograph over Chapada do Araripe mountains Ceara Brazil"
    }
]


async def generate_voice(text: str, out_path: str):
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


def produce_photorealistic_caldeirao_video():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-RENDER COM FOTOS REALISTAS HD] C:\\...\\output\\videos\\misterio_caldeirao_do_deserto")
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

    for sc in PHOTOREALISTIC_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        queries = sc["queries"]
        ai_prompt = sc["ai_prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Obter Foto Realista HD
        got_photo = fetch_wikimedia_photorealistic_hd(queries, raw_img_path)
        if not got_photo:
            fetch_photorealistic_ai_fallback(ai_prompt, scene_id, raw_img_path)

        format_photo_to_916_hd(raw_img_path, formatted_img_path)

        # 2. Renderizar Clipe em Movimento Parallax 24 FPS
        render_photorealistic_scene_clip(formatted_img_path, scene_id, narration, dur, scene_mp4)

        # 3. Gerar Voz Humana Neural
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # 4. Acoplar Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += voice_dur
        print(f"    [SCENE OK] Cena {scene_id}/6 com Foto Realista concluída ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # 5. Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 6. Exportar Vídeo Master Final em C:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\misterio_caldeirao_do_deserto
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_photorealistic.m4a")

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

    print(f"\n  🎉 [SUCESSO DEFINITIVO FOTOS REALISTAS] VÍDEO CONCLUÍDO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_photorealistic_caldeirao_video()


if __name__ == "__main__":
    main()
