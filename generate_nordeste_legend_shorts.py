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
    
    for search_term in [query, fallback_query, "Sertao Brazil", "Northeast Brazil nature"]:
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

        draw.text((540, 1780), f"CENA {scene_id}/6 - LENDAS DO NORDESTE", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        pass


NORDESTE_SHORTS_DATA = [
    # SHORT 1: COMADRE FULOZINHA
    {
        "topic_id": "short_comadre_fulozinha",
        "title_line1": "A LENDA DA COMADRE FULOZINHA",
        "title_line2": "A PROTETORA DAS MATAS DO NORDESTE",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Você sabia que nas matas do Agreste e Sertão nordestino habita uma entidade protetora capaz de confundir qualquer caçador?",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Sertao forest Caatinga Brazil",
                "fallback": "Caatinga forest Nordeste Brazil"
            },
            {
                "scene_id": 2,
                "narration": "Conhecida como Comadre Fulozinha, esta entidade tem cabelos longos que cobrem o corpo e emite um assobio misterioso para desorientar quem invade seu território.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Caatinga vegetation trees Nordeste",
                "fallback": "Sertao trees forest Brazil"
            },
            {
                "scene_id": 3,
                "narration": "Diz a lenda que quando o assobio parece vir de longe, ela está bem perto! E quando parece perto, ela já se afastou.",
                "duration": 8.0,
                "motion": "zoom_out",
                "query": "Mysterious forest mist Sertao",
                "fallback": "Caatinga forest mist night"
            },
            {
                "scene_id": 4,
                "narration": "Caçadores experientes deixam oferendas de fumo de rolo e mel nos troncos das árvores para conseguir permissão de travessia sem levar chicotadas de cipó.",
                "duration": 8.5,
                "motion": "pan_right",
                "query": "Tobacco pipe honey forest tree trunk",
                "fallback": "Tree trunk forest offering"
            },
            {
                "scene_id": 5,
                "narration": "Além de proteger a fauna, Comadre Fulozinha adora trançar as crinas dos cavalos nas fazendas durante as madrugadas de luar.",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Horse mane farm Sertao Brazil",
                "fallback": "Sertanejo horse farm night"
            },
            {
                "scene_id": 6,
                "narration": "Já ouviu o assobio da Comadre Fulozinha no sertão? Comente aqui e siga o canal para mais mitos do Nordeste!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Sertao sunset Caatinga landscape",
                "fallback": "Nordeste Brazil sunset landscape"
            }
        ]
    },
    # SHORT 2: CABEÇA DE CUIA
    {
        "topic_id": "short_cabeca_de_cuia",
        "title_line1": "A TERRORÍFICA LENDA DO",
        "title_line2": "CABEÇA DE CUIA (PIAUÍ)",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Nas margens do Rio Parnaíba, no Piauí, circula a aterrorizante lenda de Crispim, um jovem que recebeu uma maldição eterna.",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Rio Parnaiba Piaui Brazil",
                "fallback": "Parnaiba river Piaui landscape"
            },
            {
                "scene_id": 2,
                "narration": "Após uma discussão em família, Crispim agrediu a própria mãe. Antes de falecer, ela lançou uma praga transformando-o em um monstro aquático.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Old wooden house river Piaui",
                "fallback": "Sertao wooden house old"
            },
            {
                "scene_id": 3,
                "narration": "Com o corpo franzino e uma cabeça gigante em formato de cuia, a criatura foi condenada a vagar pelas águas do rio até devorar 7 Marias de virgem.",
                "duration": 8.5,
                "motion": "zoom_out",
                "query": "Rio Parnaiba water mist river night",
                "fallback": "River water night mist Piaui"
            },
            {
                "scene_id": 4,
                "narration": "Pescadores e banhistas contam que durante as cheias do rio, o Cabeça de Cuia faz virar canoas e assusta quem se aproxima dos trechos mais fundos.",
                "duration": 8.0,
                "motion": "pan_right",
                "query": "Fisherman canoe river Piaui Brazil",
                "fallback": "Canoe river fisherman Brazil"
            },
            {
                "scene_id": 5,
                "narration": "Até hoje o mito é tão forte que existe uma estátua do Cabeça de Cuia no Parque Encontro dos Rios, em Teresina.",
                "duration": 7.5,
                "motion": "zoom_in",
                "query": "Encontro dos Rios Teresina Piaui statue",
                "fallback": "Teresina Piaui river park"
            },
            {
                "scene_id": 6,
                "narration": "Conhecia a trágica lenda do Piauí? Deixe seu comentário e siga para mais segredos do folclore nordestino!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Rio Parnaiba sunset Piaui Brazil",
                "fallback": "Piaui Brazil sunset river"
            }
        ]
    },
    # SHORT 3: A MULHER DA GAMELEIRA
    {
        "topic_id": "short_mulher_da_gameleira",
        "title_line1": "A ASSOMBRAÇÃO DA GAMELEIRA",
        "title_line2": "NOS SERTÕES DO NORDESTE",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Por que os antigos sertanejos tinham verdadeiro pavor de passar perto de grandes árvores de gameleira depois da meia-noite?",
                "duration": 8.0,
                "motion": "zoom_in",
                "query": "Big Ficus tree Gameleira Sertao",
                "fallback": "Giant tree Sertao Brazil night"
            },
            {
                "scene_id": 2,
                "narration": "Na mitologia nordestina, a gameleira é considerada uma árvore sagrada e misteriosa, ponto de encontro de espíritos e assombrações.",
                "duration": 8.5,
                "motion": "pan_left",
                "query": "Giant Gameleira tree roots night",
                "fallback": "Sertao giant tree roots"
            },
            {
                "scene_id": 3,
                "narration": "Contam os vaqueiros que uma misteriosa Mulher de Branco costuma surgir sentada nas raízes seculares, chorando e pedindo orações aos viajantes.",
                "duration": 8.5,
                "motion": "zoom_out",
                "query": "White figure in night forest Sertao",
                "fallback": "Full moon night Sertao tree"
            },
            {
                "scene_id": 4,
                "narration": "Quem se aproxima para ajudar vê a mulher se transformar em névoa e escuta gargalhadas ecoando pelas galhadas da grande árvore.",
                "duration": 8.0,
                "motion": "pan_right",
                "query": "Mist fog night forest tree branches",
                "fallback": "Caatinga night fog tree"
            },
            {
                "scene_id": 5,
                "narration": "Por respeito e temor, as pessoas costumam acender velas no pé das gameleiras antigas para acalmar as almas que ali descansam.",
                "duration": 7.5,
                "motion": "zoom_in",
                "query": "Candles lighted at tree trunk night",
                "fallback": "Candles lighted night Sertao"
            },
            {
                "scene_id": 6,
                "narration": "Você teria coragem de passar perto de uma gameleira na calada da noite? Comente aqui e siga para mais histórias nordestinas!",
                "duration": 7.5,
                "motion": "zoom_out",
                "query": "Sertao night full moon landscape",
                "fallback": "Northeast Brazil night landscape"
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


def produce_nordeste_shorts():
    print(f"\n==========================================")
    print(f"[SHORTS LENDAS DO NORDESTE - BATCH DE 3 VÍDEOS] Produzindo Shorts Virais HD (9:16)")
    print(f"==========================================")

    for item in NORDESTE_SHORTS_DATA:
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

        # Exportar Vídeo Master Final do Short Nordestino
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

        print(f"  [OK] SHORT NORDESTINO CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")


def main():
    produce_nordeste_shorts()


if __name__ == "__main__":
    main()
