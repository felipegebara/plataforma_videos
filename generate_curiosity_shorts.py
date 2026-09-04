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
    
    for search_term in [query, fallback_query, "Brazil nature", "Brazil history"]:
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

        draw.text((540, 1780), f"CENA {scene_id}/6 - CURIOSIDADES DO BRASIL", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        pass


CURIOSITY_SHORTS_DATA = [
    # SHORT 1: POROROCA E A MÃE-D'ÁGUA
    {
        "topic_id": "short_misterio_pororoca",
        "title_line1": "O MISTÉRIO DA POROROCA",
        "title_line2": "E A LENDÁRIA MÃE-D'ÁGUA",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Você sabia que o encontro das águas doces do Rio Amazonas com o Oceano Atlântico cria o fenômeno mais assustador do planeta?",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Pororoca wave Amazon river",
                "fallback": "Amazon river wave ocean"
            },
            {
                "scene_id": 2,
                "narration": "Conhecida como Pororoca, essa muralha de água salta até 4 metros de altura destruindo árvores e arrastando barcos no norte do Brasil.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Amazon river tidal bore Pororoca",
                "fallback": "Amazon river high wave"
            },
            {
                "scene_id": 3,
                "narration": "Para os antigos povos ribeirinhos, a Pororoca não é só física: é a manifestação da força da Mãe-d'Água irada com a destruição da floresta.",
                "duration": 8.0,
                "motion": "zoom_out",
                "query": "Amazon river night mist myth",
                "fallback": "Amazon river sunset indigenous"
            },
            {
                "scene_id": 4,
                "narration": "Conta a lenda que antes da grande onda surgir, ouve-se o rugido da criatura vindo das profundezas do rio minutos antes da invasão.",
                "duration": 8.5,
                "motion": "pan_right",
                "query": "Amazon river jungle deep water",
                "fallback": "Amazon river dark water"
            },
            {
                "scene_id": 5,
                "narration": "Surfistas de todo o mundo enfrentam a Pororoca, mas os pescadores locais nunca navegam durante a maré cheia por respeito ao mito.",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Amazon river surfers Pororoca",
                "fallback": "Amazon river boat fisherman"
            },
            {
                "scene_id": 6,
                "narration": "Você teria coragem de encarar a onda da Mãe-d'Água? Deixe seu comentário e siga o canal para mais curiosidades do Brasil!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Amazon river sunset majestic",
                "fallback": "Amazon river canopy sunset"
            }
        ]
    },
    # SHORT 2: A ILHA DAS COBRAS DA QUEIMADA GRANDE
    {
        "topic_id": "short_ilha_das_cobras",
        "title_line1": "A ILHA MAIS PERIGOSA",
        "title_line2": "DA QUEIMADA GRANDE (SP)",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Você sabia que a ilha mais perigosa do mundo fica no litoral de São Paulo e é terminantemente proibida para visitantes?",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Ilha da Queimada Grande Snake Island",
                "fallback": "Ilha da Queimada Grande Brazil"
            },
            {
                "scene_id": 2,
                "narration": "Conhecida como Ilha da Queimada Grande, o local abriga a jararaca-ilhoa, a cobra com um dos venenos mais mortais do planeta.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Bothrops insularis snake",
                "fallback": "Jararaca snake Brazil"
            },
            {
                "scene_id": 3,
                "narration": "Estimativas apontam até 5 cobras por metro quadrado! Mas a lenda local diz que as cobras foram colocadas lá por piratas para proteger um tesouro.",
                "duration": 8.5,
                "motion": "zoom_out",
                "query": "Pirate treasure island map legend",
                "fallback": "Queimada Grande island coast"
            },
            {
                "scene_id": 4,
                "narration": "Diz a história que o antigo faroleiro e sua família foram atacados pelas cobras na década de 1920 após répteis invadirem o farol à noite.",
                "duration": 8.0,
                "motion": "pan_right",
                "query": "Queimada Grande lighthouse Brazil",
                "fallback": "Lighthouse ocean island coast"
            },
            {
                "scene_id": 5,
                "narration": "Hoje o farol é 100% automatizado pela Marinha do Brasil e apenas pesquisadores autorizados podem pisar na ilha misteriosa.",
                "duration": 7.5,
                "motion": "zoom_in",
                "query": "Brazilian Navy lighthouse coast",
                "fallback": "Lighthouse sea Brazil coast"
            },
            {
                "scene_id": 6,
                "narration": "Você encararia essa ilha dominada por cobras fatais? Comente aqui e siga o canal para mais segredos do nosso país!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Queimada Grande sunset island",
                "fallback": "Brazil ocean coast sunset"
            }
        ]
    },
    # SHORT 3: O LOBISOMEM DO SERTÃO
    {
        "topic_id": "short_lobisomem_do_sertao",
        "title_line1": "O LOBISOMEM DO SERTÃO",
        "title_line2": "AMULETOS E SEGREDO",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Por que nos vilarejos do interior do Nordeste os moradores deixavam garrafas de cachaça nas encruzilhadas em noites de lua cheia?",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Sertao full moon night Brazil",
                "fallback": "Full moon night caatinga"
            },
            {
                "scene_id": 2,
                "narration": "Na tradição do sertão, o sétimo filho homem de uma família sem filhas carregava a fada do lobisomem, transformando-se à meia-noite de sexta-feira.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Sertanejo vaqueiro night horse",
                "fallback": "Sertao Brazil night landscape"
            },
            {
                "scene_id": 3,
                "narration": "Diz a lenda que o bicho percorria 7 cemitérios e 7 vilas antes do galo cantar, uivando assustadoramente nas portas das fazendas.",
                "duration": 8.0,
                "motion": "zoom_out",
                "query": "Old cemetery Brazil sertao night",
                "fallback": "Sertao night full moon"
            },
            {
                "scene_id": 4,
                "narration": "Para se proteger, os antigos sertanejos usavam amuletos de alho, terços abençoados e colocavam alfinetes de prata nas celas dos cavalos.",
                "duration": 8.5,
                "motion": "pan_right",
                "query": "Garlic rosary amulet wooden cross",
                "fallback": "Sertanejo amulets rosary"
            },
            {
                "scene_id": 5,
                "narration": "Outro truque popular era chamar a criatura pelo nome batismal: se a pessoa acertasse o nome do homem, o encanto se quebrava na hora!",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Sertao moonlight house night",
                "fallback": "Caatinga moonlight night"
            },
            {
                "scene_id": 6,
                "narration": "Já ouviu alguma história de lobisomem contada pelos seus avós? Deixe seu relato nos comentários e siga para mais folclore!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Sertao sunset bonfire night",
                "fallback": "Sertao Brazil sunset landscape"
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


def produce_curiosity_shorts():
    print(f"\n==========================================")
    print(f"[SHORTS DE CURIOSIDADES - BATCH DE 3 VÍDEOS] Produzindo Shorts Virais HD (9:16)")
    print(f"==========================================")

    for item in CURIOSITY_SHORTS_DATA:
        topic_id = item["topic_id"]
        t1 = item["title_line1"]
        t2 = item["title_line2"]
        scenes = item["scenes"]

        print(f"\n🎬 Processando Short: {t1} - {t2}")

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
                    font = ImageFont.truetype("arialbd.ttf", 40)
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

        # Exportar Vídeo Master Final do Short
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

        print(f"  [OK] SHORT CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")


def main():
    produce_curiosity_shorts()


if __name__ == "__main__":
    main()
