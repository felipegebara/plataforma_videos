import os
import sys
import asyncio
import json
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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


def fetch_real_photo_thumbnails(query: str, count: int = 6):
    """Busca fotos REAIS únicas via Wikimedia Commons Thumbnail API."""
    photos = []
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
        f"&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={count*4}"
        f"&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    )
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "AntigravityBot/1.0 (contact@antigravity.ai)"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        pages = data.get("query", {}).get("pages", {})
        for pid, pinfo in pages.items():
            imageinfo = pinfo.get("imageinfo", [])
            if imageinfo:
                thumb_url = imageinfo[0].get("thumburl")
                if thumb_url and (thumb_url.endswith(".jpg") or thumb_url.endswith(".JPG") or thumb_url.endswith(".png")):
                    if thumb_url not in photos:
                        photos.append(thumb_url)
                        if len(photos) >= count:
                            break
    except Exception as err:
        print(f"Erro na busca de fotos reais para '{query}': {err}")
    return photos


FOLKLORE_TOPIC = {
    "id": "diabo_sem_cu_origem_sarapos",
    "title": "DIABO SEM CÚ E A ORIGEM DOS SARAPÓS",
    "search_queries": [
        "Rio Uaupes Amazonas",
        "Alto Rio Negro Amazonas",
        "Floresta Amazonica Rio",
        "Peixe Sarapo Amazonas",
        "Arte Indigena Amazonas",
        "Museu da Amazonia MUSA"
    ],
    "script_scenes": [
        {
            "scene_id": 1,
            "narration": "Na tradição ancestral dos povos indígenas Desana e Tuyuka do Alto Rio Negro, preservada pelo Museu da Amazônia, existe um mito cosmogônico singular.",
            "duration": 5.2,
            "motion": "zoom_in"
        },
        {
            "scene_id": 2,
            "narration": "Registrado pelo mestre e artista indígena Feliciano Lana, o conto relata a lenda da entidade conhecida como Diabo Sem Cú.",
            "duration": 5.0,
            "motion": "pan_left"
        },
        {
            "scene_id": 3,
            "narration": "Segundo a narrativa dos pajés do Rio Uaupés, o ser mitológico vagava pelas matas sem conseguir expelir resíduos de seu corpo.",
            "duration": 5.5,
            "motion": "zoom_out"
        },
        {
            "scene_id": 4,
            "narration": "Ao ser confrontado nas margens dos rios sagrados, a entidade deu origem aos peixes sarapós, as conhecidas enguias elétricas da Amazônia.",
            "duration": 5.3,
            "motion": "pan_right"
        },
        {
            "scene_id": 5,
            "narration": "Uma narrativa cosmogônica fascinante que explica a criação da fauna aquática e a relação sagrada dos povos originários com a natureza.",
            "duration": 5.0,
            "motion": "zoom_in"
        },
        {
            "scene_id": 6,
            "narration": "Conhecia a ancestral origem dos peixes sarapós no acervo do Museu da Amazônia? Comente e siga para mais mitologias!",
            "duration": 5.0,
            "motion": "zoom_out"
        }
    ]
}


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


def produce_video(topic_data: dict):
    print(f"\n==========================================")
    print(f"[MITOLOGIA AMAZÔNICA MUSA] Gerando Vídeo: {topic_data['title']}")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_data["id"]
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_data["id"]
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_data["id"]

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 1. Buscar 6 Fotos REAIS Únicas na API da Amazônia e MUSA
    real_photos = []
    for q in topic_data["search_queries"]:
        fetched = fetch_real_photo_thumbnails(q, count=1)
        if fetched:
            real_photos.append(fetched[0])

    print(f"Encontradas {len(real_photos)} fotos REAIS para a mitologia amazônica")

    scenes = topic_data["script_scenes"]
    video_clips = []
    audio_clips = []
    current_time = 0.0

    for idx, sc in enumerate(scenes):
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Download e Enquadramento 9:16 HD da Foto REAL
        download_ok = False
        if idx < len(real_photos):
            photo_url = real_photos[idx]
            try:
                req = urllib.request.Request(photo_url, headers={"User-Agent": "AntigravityBot/1.0 (contact@antigravity.ai)"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    temp_f = images_dir / f"temp_{scene_id}.jpg"
                    with open(temp_f, "wb") as f:
                        f.write(resp.read())

                img = Image.open(temp_f).convert("RGB")
                w, h = img.size
                target_ratio = 1080 / 1920
                if w / h > target_ratio:
                    new_w = int(h * target_ratio)
                    left = (w - new_w) // 2
                    img_c = img.crop((left, 0, left + new_w, h))
                else:
                    new_h = int(w / target_ratio)
                    top = (h - new_h) // 2
                    img_c = img.crop((0, top, w, top + new_h))

                img_final = img_c.resize((1080, 1920), Image.Resampling.LANCZOS)
                img_final.save(img_path)
                if temp_f.exists():
                    temp_f.unlink()
                download_ok = True
                print(f"  ✓ Cena {scene_id}: Foto REAL HD 9:16 da Amazônia salva")
            except Exception as e:
                print(f"  ⚠️ Erro na cena {scene_id} ({e})")

        if not download_ok:
            img = Image.new("RGB", (1080, 1920), (20, 35, 25))
            img.save(img_path)

        # 2. Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 420)], fill=(0, 0, 0, 195))
            try:
                font = ImageFont.truetype("arialbd.ttf", 38)
            except Exception:
                font = ImageFont.load_default()

            line1 = "DIABO SEM CÚ"
            line2 = "A ORIGEM DOS SARAPÓS (MUSA)"

            draw.text((540, 290), line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            img.convert("RGB").save(img_path)

        # 3. Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # 4. Renderizar Vídeo MP4 com Movimento OpenCV
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

        # 5. Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.5))

        current_time += voice_dur
        print(f"  [SCENE] Cena {scene_id} renderizada com foto real amazônica ({voice_dur:.2f}s)")

    # 6. Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 7. Exportar Vídeo Master Final com Áudio
    master_path = output_dir / f"{topic_data['id']}_FINAL_MOVIE.mp4"
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

    print(f"[OK] VÍDEO MITOLÓGICO DO MUSA CONCLUÍDO COM SUCESSO: {master_path}")
    return master_path


def main():
    produce_video(FOLKLORE_TOPIC)


if __name__ == "__main__":
    main()
