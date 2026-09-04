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
    
    for search_term in [query, fallback_query, "Petrolandia Pernambuco", "Rio Sao Francisco"]:
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
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={45000 + seed_id}"
    
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


def create_epic_custom_canvas(scene_id: int, out_path: Path):
    """Garante 100% que uma imagem procedural texturizada HD 9:16 exista se todas as APIs externas falharem."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (10, 30, 50))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        r = int(10 - y/h * 5)
        g = int(50 - y/h * 30)
        b = int(100 - y/h * 50)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")


def format_to_916_hd(raw_img_path: Path, scene_id: int, short_title: str, out_path: Path):
    """Formata foto para 9:16 HD 1080x1920 com crop perfeito e moldura."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        create_epic_custom_canvas(scene_id, raw_img_path)

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

        draw.text((540, 1780), f"CENA {scene_id}/6 - PETROLÂNDIA: A CIDADE SUBMERSA", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        create_epic_custom_canvas(scene_id, out_path)


PETROLANDIA_SCENES = [
    # CENA 1: Foto REAL HD da Igreja de São Francisco de Assis Submersa
    {
        "scene_id": 1,
        "type": "real_photo",
        "narration": "Você sabia que no fundo do Rio São Francisco existe uma cidade inteira submersa com uma igreja misteriosa surgindo das águas?",
        "duration": 8.5,
        "motion": "zoom_in",
        "query": "Igreja de Sao Francisco de Assis Petrolandia Pernambuco submersa",
        "fallback": "Igreja Petrolandia Pernambuco submersa",
        "prompt": "Authentic photograph 9:16 vertical, submerged gothic church ruins of Petrolandia in Rio Sao Francisco Pernambuco Brazil, clear blue water, golden hour sunlight, 8k"
    },
    # CENA 2: Foto REAL HD da Construção da Usina de Itaparica em 1988
    {
        "scene_id": 2,
        "type": "real_photo",
        "narration": "Em 1988, para a construção da grande Usina Hidrelétrica de Itaparica, a antiga cidade de Petrolândia em Pernambuco teve que ser inundada.",
        "duration": 9.0,
        "motion": "pan_left",
        "query": "Usina Hidreletrica de Itaparica Petrolandia Pernambuco",
        "fallback": "Rio Sao Francisco Petrolandia Pernambuco",
        "prompt": "Historical 1988 scene 9:16 vertical, water rising over old town streets of Petrolandia Pernambuco Brazil, dam construction, dramatic sunset"
    },
    # CENA 3: Ilustração IA Épica de Mergulhadores explorando as ruínas submersas
    {
        "scene_id": 3,
        "type": "ai_art",
        "narration": "Casas, praças e ruas inteiras foram cobertas pelo Velho Chico, criando um cenário subaquático fascinante que atrai mergulhadores de todo o mundo.",
        "duration": 8.5,
        "motion": "zoom_out",
        "prompt": "Cinematic underwater photography 9:16 vertical, scuba diver exploring gothic flooded church ruins of Petrolandia under clear blue Sao Francisco river water, sunbeams piercing water, fish swimming through arches, 8k"
    },
    # CENA 4: Foto REAL HD das ruínas da Igreja emergindo das águas azuis
    {
        "scene_id": 4,
        "type": "real_photo",
        "narration": "Hoje, apenas o topo da Igreja de São Francisco de Assis permanece visível acima da água, como um monumento sagrado do passado.",
        "duration": 9.0,
        "motion": "pan_right",
        "query": "Igreja de Sao Francisco Petrolandia Pernambuco",
        "fallback": "Petrolandia Pernambuco igreja submersa",
        "prompt": "Stunning aerial drone shot 9:16 vertical, flooded Gothic church ruins standing in middle of blue Rio Sao Francisco Petrolandia Pernambuco, 8k"
    },
    # CENA 5: Ilustração IA Épica da Cidade Submersa Iluminada com Visão Subaquática
    {
        "scene_id": 5,
        "type": "ai_art",
        "narration": "A nova cidade de Petrolândia foi reconstruída nas margens do lago, mantendo viva a memória da Atlântida brasileira do sertão.",
        "duration": 9.5,
        "motion": "zoom_in",
        "prompt": "Surreal cinematic art 9:16 vertical, ancient submerged city underwater with illuminated Gothic church and fish swimming at sunset, mystical atmosphere, 8k"
    },
    # CENA 6: Foto REAL HD do Pôr do Sol Dourado no Rio São Francisco em Petrolândia
    {
        "scene_id": 6,
        "type": "real_photo",
        "narration": "Gostou de conhecer a incrível história de Petrolândia? Deixe seu comentário, compartilhe e siga o canal para mais mistérios do Nordeste!",
        "duration": 8.0,
        "motion": "zoom_out",
        "query": "Rio Sao Francisco Petrolandia Pernambuco sunset",
        "fallback": "Rio Sao Francisco sunset Pernambuco",
        "prompt": "Golden sunset over Rio Sao Francisco Petrolandia Pernambuco Brazil, boat near submerged church, 8k"
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


def produce_improved_petrolandia_video():
    topic_id = "misterio_petrolandia_submersa"
    t1 = "PETROLÂNDIA SUBMERSA"
    t2 = "A ATLÂNTIDA DO VELHO CHICO"

    print(f"\n==========================================")
    print(f"[RE-RENDER COM FOTOS PERFEITAS DA IGREJA SUBMERSA] Petrolândia (6 Cenas HD Híbridas)")
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

    for sc in PETROLANDIA_SCENES:
        scene_id = sc["scene_id"]
        img_type = sc["type"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        prompt_txt = sc["prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        img_path = images_dir / f"scene_{scene_id}.png"

        # Geração Híbrida Aprimorada com Fallback Procedural
        img_obtained = False
        if img_type == "real_photo":
            query_txt = sc["query"]
            fallback_txt = sc["fallback"]
            img_obtained = fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
        else:
            img_obtained = fetch_ai_generated_image(prompt_txt, scene_id, raw_img_path)

        if not img_obtained or not raw_img_path.exists():
            create_epic_custom_canvas(scene_id, raw_img_path)

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
            if img_cv is None:
                create_epic_custom_canvas(scene_id, img_path)
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
        print(f"    [SCENE] Cena {scene_id}/6 ({img_type}) renderizada ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Aprimorado com Safe Lock
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_petrolandia.m4a")

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio_file,
        remove_temp=True,
        fps=24,
        logger=None
    )

    # Fechamento Limpo de Clipes
    comp_v.close()
    comp_a.close()
    for vc in video_clips:
        vc.close()
    for ac in audio_clips:
        ac.close()

    print(f"  [OK] VÍDEO APRIMORADO DE PETROLÂNDIA CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_improved_petrolandia_video()


if __name__ == "__main__":
    main()
