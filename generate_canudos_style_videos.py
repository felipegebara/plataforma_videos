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
    
    for search_term in [query, fallback_query, "Sertao Brazil history", "Northeast Brazil"]:
        encoded_term = urllib.parse.quote(search_term)
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

        draw.text((540, 1780), f"CENA {scene_id}/6 - HISTÓRIA ÉPICA DO SERTÃO", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        pass


CANUDOS_STYLE_DATA = [
    # 1. CALDEIRÃO DE SANTA CRUZ DO DESERTO (CEARÁ) - O NOVO CANUDOS
    {
        "topic_id": "misterio_caldeirao_do_deserto",
        "title_line1": "O CALDEIRÃO DE SANTA CRUZ",
        "title_line2": "O SEGUNDO CANUDOS DO SERTÃO",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Você sabia que anos após a destruição de Canudos, o sertão viveu outro império de fé e tragédia esquecido pela história?",
                "duration": 8.5,
                "motion": "zoom_in",
                "query": "Sertao Ceara Crato Araripe landscape",
                "fallback": "Caatinga Ceara Brazil landscape"
            },
            {
                "scene_id": 2,
                "narration": "Na década de 1920, o Beato José Lourenço fundou na Serra do Araripe a comunidade do Caldeirão de Santa Cruz, sob benção do Padre Cícero.",
                "duration": 9.0,
                "motion": "pan_left",
                "query": "Padre Cicero Juazeiro do Norte Ceara",
                "fallback": "Padre Cicero statue Ceara"
            },
            {
                "scene_id": 3,
                "narration": "Milhares de sertanejos miseráveis migraram para lá, criando uma sociedade igualitária com lavouras prósperas no meio da seca.",
                "duration": 8.5,
                "motion": "zoom_out",
                "query": "Sertanejo farmers Ceara Sertao",
                "fallback": "Sertao farm Brazil historical"
            },
            {
                "scene_id": 4,
                "narration": "Assustados com o poder daquela comunidade que lembrava o Arraial de Canudos, autoridades e fazendeiros acusaram o povo de fanatismo.",
                "duration": 9.0,
                "motion": "pan_right",
                "query": "Sertao Ceara historical 1930s",
                "fallback": "Old Sertao Brazil village"
            },
            {
                "scene_id": 5,
                "narration": "Em 1937, a Força Pública e aviões militares bombardearam o Caldeirão, destruindo o arraial e sepultando uma das maiores utopias do sertão.",
                "duration": 9.5,
                "motion": "zoom_in",
                "query": "Military Sertao Brazil historical",
                "fallback": "Sertao Brazil ruins historical"
            },
            {
                "scene_id": 6,
                "narration": "Conhecia a impressionante história do Caldeirão do Ceará? Deixe seu comentário e siga o canal para mais histórias épicas!",
                "duration": 8.0,
                "motion": "zoom_out",
                "query": "Serra do Araripe sunset Ceara",
                "fallback": "Sertao Ceara sunset landscape"
            }
        ]
    },
    # 2. PETROLÂNDIA: A CIDADE SUBMERSA DO VELHO CHICO
    {
        "topic_id": "misterio_petrolandia_submersa",
        "title_line1": "PETROLÂNDIA: A CIDADE SUBMERSA",
        "title_line2": "DO RIO SÃO FRANCISCO",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Assim como Canudos submergiu nas águas do açude, existe no interior de Pernambuco uma verdadeira Atlântida do sertão brasileiro.",
                "duration": 8.5,
                "motion": "zoom_in",
                "query": "Petrolandia submersa igreja Pernambuco",
                "fallback": "Petrolandia igreja Sao Francisco"
            },
            {
                "scene_id": 2,
                "narration": "Na década de 1980, a construção da Usina Hidrelétrica de Luiz Gonzaga forçou a desocupação e inundação da antiga cidade de Petrolândia.",
                "duration": 9.0,
                "motion": "pan_left",
                "query": "Rio Sao Francisco Pernambuco dam",
                "fallback": "Rio Sao Francisco Pernambuco water"
            },
            {
                "scene_id": 3,
                "narration": "Moradores viram suas casas, praças e memórias serem cobertas pelas águas do Rio São Francisco em uma despedida emocionante.",
                "duration": 8.5,
                "motion": "zoom_out",
                "query": "Rio Sao Francisco old town Pernambuco",
                "fallback": "Rio Sao Francisco river bank Pernambuco"
            },
            {
                "scene_id": 4,
                "narration": "Hoje, o monumento mais impressionante que restou é a topo da Igreja de São Francisco de Assis, emergindo das águas profundas do lago.",
                "duration": 9.0,
                "motion": "pan_right",
                "query": "Igreja de Sao Francisco Petrolandia submersa",
                "fallback": "Petrolandia submerged church Pernambuco"
            },
            {
                "scene_id": 5,
                "narration": "Mergulhadores de todo o mundo exploram as ruínas submersas da igreja e dos casarões, cercados por peixes nas profundezas do rio.",
                "duration": 8.5,
                "motion": "zoom_in",
                "query": "Scuba diving Petrolandia submerged church",
                "fallback": "Rio Sao Francisco underwater ruin"
            },
            {
                "scene_id": 6,
                "narration": "Gostou de conhecer a incrível história da cidade submersa de Petrolândia? Deixe seu comentário e siga para mais mistérios!",
                "duration": 8.0,
                "motion": "zoom_out",
                "query": "Petrolandia sunset Rio Sao Francisco",
                "fallback": "Rio Sao Francisco sunset Pernambuco"
            }
        ]
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


def produce_canudos_style_videos():
    print(f"\n==========================================")
    print(f"[ESTILO CANUDOS - HISTÓRIA ÉPICA DO SERTÃO] Produzindo 2 Novos Vídeos Épicos")
    print(f"==========================================")

    for item in CANUDOS_STYLE_DATA:
        topic_id = item["topic_id"]
        t1 = item["title_line1"]
        t2 = item["title_line2"]
        scenes = item["scenes"]

        print(f"\n🎬 Processando Vídeo Épico: {t1} - {t2}")

        output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
        images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
        audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)

        video_clips = []
        audio_clips = []
        current_time = 0.0

        for sc in scenes:
            scene_id = sc["scene_id"]
            narration = sc["narration"]
            dur = sc["duration"]
            motion = sc["motion"]
            query_txt = sc["query"]
            fallback_txt = sc["fallback"]

            raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
            img_path = images_dir / f"scene_{scene_id}.png"

            # Buscar Foto REAL HD
            fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
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

            # Gerar Voz Humana Neural em Português
            voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
            asyncio.run(generate_voice(narration, str(voice_path)))

            # Renderizar Vídeo MP4 com Movimento OpenCV
            scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
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

            # Acoplar Clipes de Áudio e Vídeo
            v_clip = VideoFileClip(str(scene_mp4))
            voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
            voice_dur = voice_clip.duration + 0.1

            v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
            video_clips.append(v_clip)
            audio_clips.append(voice_clip.with_volume_scaled(1.5))

            current_time += voice_dur
            print(f"    [SCENE] Cena {scene_id}/6 renderizada ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

        # Adicionar Trilha BGM de Fundo
        bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        if bgm_path.exists():
            raw_bgm = AudioFileClip(str(bgm_path))
            bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
            audio_clips.append(bgm_clip)

        # Exportar Vídeo Master Final Estilo Canudos
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

        print(f"  [OK] VÍDEO ÉPICO CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")


def main():
    produce_canudos_style_videos()


if __name__ == "__main__":
    main()
