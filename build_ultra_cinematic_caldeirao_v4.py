import os
import sys
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
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, AudioArrayClip

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
    
    for search_term in [query, fallback_query, "Juazeiro do Norte Ceara", "Crato Ceara"]:
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


def fetch_ultra_hd_ai_image(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera ilustração hyper-detalhada em 8K via Pollinations AI Engine."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={70000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=16) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ Imagem de IA Ultra-HD Gerada com Sucesso: '{prompt[:40]}...'")
                return True
    except Exception:
        pass
    return False


def create_epic_custom_canvas(scene_id: int, out_path: Path):
    """Garante 100% que uma imagem procedural texturizada HD 9:16 exista se todas as APIs externas falharem."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (30, 20, 15))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        r = int(60 - y/h * 40)
        g = int(35 - y/h * 25)
        b = int(20 - y/h * 15)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")


def apply_dynamic_subtitles_and_borders(in_mp4_path: Path, scene_id: int, narration_text: str, subtitle_label: str, out_mp4_path: Path):
    """
    Acopla Legendas Dinâmicas de Alto Impacto e Moldura Dourada em cima do Clipe de Vídeo em Movimento 3D.
    """
    cap = cv2.VideoCapture(str(in_mp4_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (w, h))

    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
        font_banner = ImageFont.truetype("arialbd.ttf", 28)
    except Exception:
        font_sub = ImageFont.load_default()
        font_banner = ImageFont.load_default()

    words = narration_text.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(frame_pil)

        # Banner Superior de Título
        draw.rectangle([(50, 60), (w - 50, 160)], fill=(0, 0, 0, 210))
        draw.rectangle([(50, 60), (65, 160)], fill=(255, 215, 0))
        draw.text((85, 110), subtitle_label.upper(), fill=(255, 215, 0), font=font_banner, anchor="lm")

        # Legenda da Narração com Fundo Escuro Semi-Transparente
        draw.rectangle([(60, h - 340), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 280), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 200), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    cap.release()
    out_v.release()


SCENES_CALDEIRAO_V4 = [
    {
        "scene_id": 1,
        "type": "real_photo",
        "label": "A SERRA DO ARARIPE NO CEARÁ",
        "narration": "Anos após a destruição de Canudos, o sertão do Ceará viveu um novo império de fé e tragédia esquecido.",
        "duration": 8.5,
        "query": "Serra do Araripe Crato Ceara",
        "fallback": "Caatinga Ceara Brazil landscape",
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 photograph, Serra do Araripe mountains sunrise Ceara sertao, dramatic golden lighting, fine art"
    },
    {
        "scene_id": 2,
        "type": "real_photo",
        "label": "PADRE CÍCERO EM JUAZEIRO DO NORTE",
        "narration": "O Beato José Lourenço fundou a comunidade do Caldeirão de Santa Cruz sob a benção direta do Padre Cícero.",
        "duration": 9.0,
        "query": "Statue of Padre Cicero in Juazeiro do Norte",
        "fallback": "Estatua de Padre Cicero Horto Juazeiro",
        "prompt": "Monument statue of Padre Cicero in Juazeiro do Norte Ceara, golden hour sunset, 8k"
    },
    {
        "scene_id": 3,
        "type": "ai_art",
        "label": "UMA SOCIEDADE COMUNITÁRIA FARTURA",
        "narration": "Milhares de sertanejos miseráveis migraram para lá, construindo uma sociedade sem dinheiro e com lavouras fartas.",
        "duration": 8.5,
        "prompt": "Cinematic historical 8k painting 9:16 vertical, 1930s Brazilian sertanejo farmers harvesting green crops together in dry Ceara sertao, volumetric lighting"
    },
    {
        "scene_id": 4,
        "type": "ai_art",
        "label": "A FÚRIA DOS CORONÉIS DO SERTÃO",
        "narration": "Assustados com o poder daquela comunidade, fazendeiros e coronéis acusaram o povo de fanatismo e comunismo.",
        "duration": 9.0,
        "prompt": "Cinematic historical 8k masterpiece 9:16 vertical, 1930s Brazilian sertao land barons on horseback looking down at village under dark stormy sky"
    },
    {
        "scene_id": 5,
        "type": "ai_art",
        "label": "O BOMBARDEIO AÉREO DE 1937",
        "narration": "Em 1937, aviões de guerra da Força Aérea bombardearam o Caldeirão, destruindo o arraial e sepultando o povo.",
        "duration": 9.5,
        "prompt": "Cinematic historical 8k battle 9:16 vertical, 1930s military biplanes dropping bombs over burning Brazilian sertao village, smoke and fire explosion"
    },
    {
        "scene_id": 6,
        "type": "real_photo",
        "label": "RESGATE DA MEMÓRIA HISTÓRICA",
        "narration": "Conhecia a incrível história do Caldeirão do Ceará? Deixe seu comentário e siga o canal para mais histórias épicas!",
        "duration": 8.0,
        "query": "Chapada do Araripe sunset Ceara",
        "fallback": "Serra do Araripe sunset landscape",
        "prompt": "Golden sunset over Chapada do Araripe mountains Ceara Brazil, dramatic clouds, 8k"
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


def produce_true_ai_video_caldeirao():
    topic_id = "caldeirao_true_ai_video_v4"
    t1 = "O CALDEIRÃO DE SANTA CRUZ"

    print(f"\n==========================================")
    print(f"[MOTOR DE VÍDEO IA REAL - SEM ZOOM ESTÁTICO] O Caldeirão do Ceará (Com Animação 3D de Fluidos & Legendas)")
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

    for sc in SCENES_CALDEIRAO_V4:
        scene_id = sc["scene_id"]
        img_type = sc["type"]
        narration = sc["narration"]
        dur = sc["duration"]
        label = sc["label"]
        prompt_txt = sc["prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        raw_video_mp4 = output_dir / f"raw_scene_{scene_id}.mp4"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Obtenção do Quadro-Chave Base
        img_obtained = False
        if img_type == "real_photo":
            query_txt = sc["query"]
            fallback_txt = sc["fallback"]
            img_obtained = fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
        else:
            img_obtained = fetch_ultra_hd_ai_image(prompt_txt, scene_id, raw_img_path)

        if not img_obtained or not raw_img_path.exists():
            create_epic_custom_canvas(scene_id, raw_img_path)

        # 2. GERAÇÃO DO VÍDEO IA REAL (Deslocamento de Malha 3D + Animação de Fluidos)
        video_ai_engine.generate_true_ai_video(prompt_txt, str(raw_img_path), dur, str(raw_video_mp4))

        # 3. Estampar Legendas Dinâmicas e Moldura Dourada sobre o Vídeo IA em Movimento
        apply_dynamic_subtitles_and_borders(raw_video_mp4, scene_id, narration, label, scene_mp4)

        # 4. Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # 5. Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += voice_dur
        print(f"    [AI VIDEO SCENE OK] Cena {scene_id}/6 ({img_type}) em Movimento 3D concluída ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # 6. Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 7. Exportar Vídeo Master V4
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_v4_ai.m4a")

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

    print(f"  [OK] VÍDEO EM MOVIMENTO IA REAL CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_true_ai_video_caldeirao()


if __name__ == "__main__":
    main()
