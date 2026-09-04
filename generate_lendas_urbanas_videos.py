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
    """Busca 6 fotos REAIS únicas via Wikimedia Commons Thumbnail API."""
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


URBAN_LEGENDS_TOPICS = [
    # 1. A Lenda da Loira do Banheiro
    {
        "id": "loira_do_banheiro",
        "title": "A LENDA DA LOIRA DO BANHEIRO",
        "search_query": "Escola Historica Brasil",
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "Presente na memória de gerações de estudantes em todo o Brasil, a lenda da Loira do Banheiro esconde uma origem histórica real.",
                "duration": 5.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "A história é inspirada em Maria Augusta de Oliveira, jovem da alta sociedade de Guaratinguetá no século dezenove.",
                "duration": 5.2,
                "motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Forçada a se casar aos catorze anos, Maria fugiu para Paris e faleceu misteriosamente aos vinte e seis anos.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Após sua morte, seu corpo permaneceu mumificado em um relicário de vidro na mansão da família, que mais tarde virou escola.",
                "duration": 5.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 5,
                "narration": "Alunos assustados diziam ver o espírito da jovem loira rondando os espelhos e banheiros do casarão histórico.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Você já ouviu essa lenda nos tempos de escola? Deixe seu comentário e compartilhe com os amigos!",
                "duration": 5.0,
                "motion": "zoom_out"
            }
        ]
    },
    # 2. O Mistério do Edifício Martinelli
    {
        "id": "edificio_martinelli_sp",
        "title": "O MISTÉRIO DO EDIFÍCIO MARTINELLI",
        "search_query": "Edificio Martinelli Sao Paulo",
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "Inaugurado nos anos vinte no centro de São Paulo, o Edifício Martinelli foi o primeiro arranha-céu da América Latina.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "Construído pelo comendador Giuseppe Martinelli, o prédio luxuoso atraiu a elite e abrigou o prestigiado Cine Rosário.",
                "duration": 5.2,
                "motion": "pan_right"
            },
            {
                "scene_id": 3,
                "narration": "Porém, nas décadas seguintes, o edifício enfrentou o abandono e tornou-se palco de crimes misteriosos sem solução.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Relatos de moradores e vigias urbanos descrevem passos no terraço de mansão e aparições no fosso do elevador.",
                "duration": 5.0,
                "motion": "pan_left"
            },
            {
                "scene_id": 5,
                "narration": "Restaurado e tombado pelo patrimônio histórico, o terraço panorâmico do Martinelli atrai curiosos por sua arquitetura e mistérios.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Você teria coragem de subir ao topo do Edifício Martinelli à noite? Comente sua opinião!",
                "duration": 5.0,
                "motion": "zoom_out"
            }
        ]
    },
    # 3. A Lenda da Cobra Grande da Sé (Belém do Pará)
    {
        "id": "cobra_grande_da_se_belem",
        "title": "A COBRA GRANDE DA SÉ EM BELÉM",
        "search_query": "Catedral da Se Belem Para",
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "No coração de Belém do Pará, uma das lendas urbanas mais famosas do Norte envolve a imponente Catedral da Sé.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "Segundo a tradição popular amazonense, uma serpente gigante repousa adormecida sob os alicerces coloniais da catedral.",
                "duration": 5.2,
                "motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Diz a lenda que a cabeça da grande cobra repousa sob o altar-mor, enquanto sua cauda alcança a Basílica de Nazaré.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Moradores antigos acreditavam que se a serpente desperta, o solo da cidade afunda sob as águas da Baía do Guajará.",
                "duration": 5.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 5,
                "narration": "Um fascinante mito amazônico que une arquitetura colonial e a rica mitologia indígena do Pará.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Já conhecia a lenda da Cobra Grande sob a Catedral de Belém? Deixe seu comentário e siga o canal!",
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
    print(f"[LENDAS URBANAS - FOTOS REAIS HD] Gerando Vídeo: {topic_data['title']}")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_data["id"]
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_data["id"]
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_data["id"]

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 1. Buscar 6 Fotos REAIS Únicas na API
    real_photos = fetch_real_photo_thumbnails(topic_data["search_query"], count=6)
    print(f"Encontradas {len(real_photos)} fotos REAIS para '{topic_data['search_query']}'")

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
                print(f"  ✓ Cena {scene_id}: Foto REAL HD 9:16 da Lenda Urbana salva")
            except Exception as e:
                print(f"  ⚠️ Erro na cena {scene_id} ({e})")

        if not download_ok:
            img = Image.new("RGB", (1080, 1920), (30, 20, 35))
            img.save(img_path)

        # 2. Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 420)], fill=(0, 0, 0, 195))
            try:
                font = ImageFont.truetype("arialbd.ttf", 40)
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
        print(f"  [SCENE] Cena {scene_id} renderizada com foto real da lenda urbana ({voice_dur:.2f}s)")

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

    print(f"[OK] VÍDEO DE LENDA URBANA CONCLUÍDO COM SUCESSO: {master_path}")
    return master_path


def main():
    print("[INIT] PRODUÇÃO DE 3 VÍDEOS DE LENDAS URBANAS E MISTÉRIOS HISTÓRICOS")
    for t_data in URBAN_LEGENDS_TOPICS:
        produce_video(t_data)
    print("\n[SUCCESS] TODOS OS VÍDEOS DE LENDAS URBANAS FORAM GERADOS COM SUCESSO!")


if __name__ == "__main__":
    main()
