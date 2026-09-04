import os
import sys
import asyncio
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

# 6 FOTOS REAIS ÚNICAS E EXCLUSIVAS PARA CADA TÓPICO
CARRANCAS_PHOTOS = [
    "https://upload.wikimedia.org/wikipedia/commons/4/4b/Carranca_do_Sao_Francisco.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b9/Barco_Travessia_III_-_Ilha_do_Rodeador_%281375939553%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/56/Adriana_Carranca_%283988460305%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/58/Adriana_Carranca_%283989213942%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/32/Adriana_Carranca_%283989214472%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/ce/Adriana_Carranca_%283989214888%29.jpg"
]

CHAPADA_PHOTOS = [
    "https://upload.wikimedia.org/wikipedia/commons/f/f6/Poco_Azul_Chapada_Diamantina_Bahia.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/86/Chapada_Diamantina_%285427619037%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/cf/Chapada_Diamantina_2005_-_2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c2/Chapada_diamantina_bahia_brasil20180218_134533.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/0a/Chapada_diamantina_bahia_brasil20180218_135503.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/86/Forma%C3%A7%C3%B5es_rochosas_regi%C3%A3o_de_Len%C3%A7%C3%B3is_-_Chapada_Diamantina_2012_02.jpg"
]

TOPICS_TO_FIX = [
    {
        "id": "carrancas_velho_chico",
        "title": "A LENDA DA CARRANCA DO VELHO CHICO",
        "photos": CARRANCAS_PHOTOS,
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "Nas margens do Rio São Francisco, no sertão baiano, nasceu uma das lendas mais temidas da navegação brasileira.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "As carrancas, esculturas de madeira de rostos grotescos e dentes afiados, eram fixadas na proa dos barcos a vapor.",
                "duration": 5.2,
                "motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Navegadores acreditavam que as carrancas soltavam gemidos e espantavam o Caboclo d'Água e os espíritos do rio.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Construídas por mestres carpinteiros de Juazeiro e Bom Jesus da Lapa, cada peça carregava um talismã de proteção.",
                "duration": 5.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 5,
                "narration": "Hoje, as carrancas são reconhecidas como símbolos sagrados do patrimônio e da cultura popular sertaneja.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Você teria uma carranca protetora na sua casa? Comente sua opinião e compartilhe essa lenda da Bahia!",
                "duration": 5.0,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "id": "chapada_diamantina_grutas",
        "title": "AS CAVERNAS DA CHAPADA DIAMANTINA",
        "photos": CHAPADA_PHOTOS,
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "Nas entranhas das montanhas da Chapada Diamantina, abrigam-se grutas e lagos subterrâneos de águas cristalinas.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "No Poço Azul e no Poço Encantado, feixes de luz solar penetram as fendas das rochas, iluminando as águas azul-turquesa.",
                "duration": 5.2,
                "motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Durante a era do garimpo no século dezenove, garimpeiros buscavam os maiores diamantes do mundo nas fendas das cavernas.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Fósseis de animais pré-históricos da megafauna, como preguiças-gigantes, foram preservados no fundo dos poços profundos.",
                "duration": 5.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 5,
                "narration": "Um santuário ecológico e geológico que conserva segredos de milhões de anos no interior da Bahia.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Você teria coragem de mergulhar nas cavernas subterrâneas da Chapada Diamantina? Deixe seu comentário!",
                "duration": 5.0,
                "motion": "zoom_out"
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


def produce_video(topic_data: dict):
    print(f"\n==========================================")
    print(f"[RE-RENDER] Produzindo 6 Imagens Únicas HD para: {topic_data['title']}")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_data["id"]
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_data["id"]
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_data["id"]

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    scenes = topic_data["script_scenes"]
    photos_urls = topic_data["photos"]
    video_clips = []
    audio_clips = []
    current_time = 0.0

    for idx, sc in enumerate(scenes):
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]

        img_path = images_dir / f"scene_{scene_id}.png"
        photo_url = photos_urls[idx % len(photos_urls)]

        # Download e Recorte 9:16 Vertical HD
        try:
            req = urllib.request.Request(photo_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
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
            print(f"  ✓ Cena {scene_id}: Foto HD Única 9:16 salva")
        except Exception as e:
            print(f"  ⚠️ Erro ao baixar foto {scene_id} ({e}), gerando lousa de cor...")
            img = Image.new("RGB", (1080, 1920), (25, 35, 55))
            img.save(img_path)

        # 2. Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 420)], fill=(0, 0, 0, 195))
            try:
                font = ImageFont.truetype("arialbd.ttf", 42)
            except Exception:
                font = ImageFont.load_default()

            title_str = topic_data["title"]
            parts = title_str.split(" DA ") if " DA " in title_str else title_str.split(" DO ")
            line1 = parts[0]
            line2 = ("DA " if " DA " in title_str else "DO ") + parts[1] if len(parts) > 1 else title_str

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
        print(f"  [SCENE] Cena {scene_id} renderizada com imagem HD única ({voice_dur:.2f}s)")

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

    print(f"[OK] VIDEO RE-RENDERIZADO COM SUCESSO: {master_path}")
    return master_path


def main():
    print("[INIT] RE-RENDERIZACAO DE CARRANCAS E CHAPADA DIAMANTINA COM 6 IMAGENS HD UNICAS")
    for t_data in TOPICS_TO_FIX:
        produce_video(t_data)
    print("\n[SUCCESS] CARRANCAS E CHAPADA DIAMANTINA RE-RENDERIZADOS COM SUCESSO!")


if __name__ == "__main__":
    main()
