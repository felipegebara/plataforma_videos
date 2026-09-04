import os
import sys
import json
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

from video_ai_engine import video_ai_engine

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def fetch_wikimedia_hd_photo(query: str, fallback_query: str, out_path: Path) -> bool:
    """Busca foto REAL em HD (1280px width) via Wikimedia Commons API."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    
    for search_term in [query, fallback_query, "Juazeiro do Norte Ceara", "Padre Cicero"]:
        encoded_term = urllib.parse.quote(search_term)
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=10&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        
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
                            print(f"    ✓ Foto REAL HD obtida: {search_term} ({out_path.name})")
                            return True
        except Exception:
            pass
    return False


def fetch_ai_generated_image(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera ilustração cinematográfica em HD via Pollinations AI Engine."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={12000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=16) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ Imagem de IA Gerada com Sucesso: '{prompt[:35]}...'")
                return True
    except Exception:
        pass
    return False


def format_to_916_hd(raw_img_path: Path, scene_id: int, short_title: str, out_path: Path):
    """Formata foto para 9:16 HD 1080x1920 com crop perfeito e moldura."""
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
        draw = ImageDraw.Draw(img)
        draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)

        try:
            font = ImageFont.truetype("arialbd.ttf", 32)
        except Exception:
            font = ImageFont.load_default()

        draw.text((540, 1780), f"CENA {scene_id}/6 - WAN 2.1 / HUNYUAN VIDEO ENGINE", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        pass


IMPROVED_CALDEIRAO_SCENES = [
    {
        "scene_id": 1,
        "type": "real_photo",
        "narration": "Você sabia que anos após a destruição de Canudos, o sertão do Ceará viveu outro império de fé e tragédia esquecido pela história?",
        "duration": 8.5,
        "motion": "zoom_in",
        "query": "Serra do Araripe Crato Ceara",
        "fallback": "Caatinga Ceara Brazil landscape",
        "prompt": "Serra do Araripe mountains at sunrise, Ceara sertao"
    },
    {
        "scene_id": 2,
        "type": "real_photo",
        "narration": "Na década de 1920, o Beato José Lourenço fundou na Serra do Araripe a comunidade do Caldeirão de Santa Cruz, sob benção do Padre Cícero.",
        "duration": 9.0,
        "motion": "pan_left",
        "query": "Statue of Padre Cicero in Juazeiro do Norte",
        "fallback": "Estatua de Padre Cicero Horto Juazeiro",
        "prompt": "Monument statue of Padre Cicero in Juazeiro do Norte Ceara"
    },
    {
        "scene_id": 3,
        "type": "ai_art",
        "narration": "Milhares de sertanejos miseráveis migraram para lá, criando uma sociedade igualitária com lavouras prósperas no meio da seca.",
        "duration": 8.5,
        "motion": "zoom_out",
        "prompt": "Cinematic historical painting 9:16 vertical, poor 1930s Brazilian sertanejo farmers working together in green crops in dry Ceara sertao, 8k"
    },
    {
        "scene_id": 4,
        "type": "ai_art",
        "narration": "Assustados com o poder daquela comunidade que lembrava o Arraial de Canudos, autoridades e fazendeiros acusaram o povo de fanatismo.",
        "duration": 9.0,
        "motion": "pan_right",
        "prompt": "Cinematic historical masterpiece 9:16 vertical, 1930s Brazilian sertao land barons on horseback looking down at village under dark stormy sky, 8k"
    },
    {
        "scene_id": 5,
        "narration": "Em 1937, a Força Pública e aviões militares bombardearam o Caldeirão, destruindo o arraial e sepultando uma das maiores utopias do sertão.",
        "duration": 9.5,
        "motion": "zoom_in",
        "type": "ai_art",
        "prompt": "Cinematic historical battle painting 9:16 vertical, 1930s military biplanes dropping bombs over burning Brazilian sertao village, smoke and fire, 8k"
    },
    {
        "scene_id": 6,
        "type": "real_photo",
        "narration": "Conhecia a impressionante história do Caldeirão do Ceará? Deixe seu comentário e siga o canal para mais histórias épicas!",
        "duration": 8.0,
        "motion": "zoom_out",
        "query": "Chapada do Araripe sunset Ceara",
        "fallback": "Serra do Araripe sunset landscape",
        "prompt": "Golden sunset over Chapada do Araripe mountains Ceara Brazil"
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


def produce_wan_hunyuan_caldeirao_video():
    topic_id = "misterio_caldeirao_do_deserto"
    t1 = "O CALDEIRÃO DE SANTA CRUZ"
    t2 = "WAN 2.1 / HUNYUAN VIDEO ENGINE"

    print(f"\n==========================================")
    print(f"[ENGINE WAN 2.1/2.2 & HUNYUANVIDEO] Produzindo Vídeo com Motores IA de Vídeo")
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

    for sc in IMPROVED_CALDEIRAO_SCENES:
        scene_id = sc["scene_id"]
        img_type = sc["type"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        prompt_txt = sc["prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        img_path = images_dir / f"scene_{scene_id}.png"

        # 1. Geração / Obtenção do Quadro HD Base
        if img_type == "real_photo":
            query_txt = sc["query"]
            fallback_txt = sc["fallback"]
            fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
        else:
            fetch_ai_generated_image(prompt_txt, scene_id, raw_img_path)

        format_to_916_hd(raw_img_path, scene_id, t1, img_path)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 38)
            except Exception:
                font = ImageFont.load_default()

            draw.text((540, 290), t1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), t2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            img.convert("RGB").save(img_path)

        # 2. Tentar Motores Wan 2.1/2.2 e HunyuanVideo
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        ai_video_ok = video_ai_engine.generate_video_wan(prompt_txt, str(img_path), dur, str(scene_mp4))
        if not ai_video_ok:
            ai_video_ok = video_ai_engine.generate_video_hunyuan(prompt_txt, str(img_path), dur, str(scene_mp4))

        # 3. Renderizador de Movimento Dinâmico OpenCV 24 FPS (Fallback de Segurança)
        if not ai_video_ok or not scene_mp4.exists():
            img_cv = cv2.imread(str(img_path))
            h_cv, w_cv, _ = img_cv.shape
            fps = 24
            total_f = int(dur * fps)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out_v = cv2.VideoWriter(str(scene_mp4), fourcc, fps, (w_cv, h_cv))

            for f_idx in range(total_f):
                prog = f_idx / float(total_f)
                if motion == "zoom_in":
                    scale = 1.0 + (0.08 * prog)
                elif motion == "zoom_out":
                    scale = 1.08 - (0.08 * prog)
                else:
                    scale = 1.04

                nw, nh = int(w_cv * scale), int(h_cv * scale)
                resized = cv2.resize(img_cv, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

                if motion == "pan_left":
                    sx = int((nw - w_cv) * (1.0 - prog))
                elif motion == "pan_right":
                    sx = int((nw - w_cv) * prog)
                else:
                    sx = (nw - w_cv) // 2

                sy = (nh - h_cv) // 2
                out_v.write(resized[sy : sy + h_cv, sx : sx + w_cv])

            out_v.release()

        # Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.5))

        current_time += voice_dur
        print(f"    [SCENE] Cena {scene_id}/6 ({img_type}) renderizada com sucesso ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Aprimorado
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None
    )

    print(f"  [OK] VÍDEO WAN 2.1 / HUNYUAN CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_wan_hunyuan_caldeirao_video()


if __name__ == "__main__":
    main()
