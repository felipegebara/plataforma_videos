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
    
    for search_term in [query, fallback_query, "Paraiba Brazil", "Sertao Nordeste"]:
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
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={80000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=16) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ Imagem de IA Ultra-HD Gerada: '{prompt[:40]}...'")
                return True
    except Exception:
        pass
    return False


def create_epic_custom_canvas(scene_id: int, out_path: Path):
    """Garante 100% que uma imagem procedural texturizada HD 9:16 exista se todas as APIs externas falharem."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (25, 20, 35))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        r = int(45 - y/h * 30)
        g = int(25 - y/h * 20)
        b = int(60 - y/h * 40)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")


def render_v4_short_clip(img_path: Path, scene_id: int, narration_text: str, subtitle_label: str, duration: float, out_mp4_path: Path):
    """Renderiza clipe de 24 FPS com legendas dinâmicas amarelas/brancas e efeito visual de cinema."""
    img_pil = Image.open(img_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
    
    # Enhancements
    img_pil = ImageEnhance.Contrast(img_pil).enhance(1.2)
    img_pil = ImageEnhance.Color(img_pil).enhance(1.15)
    img_np = np.array(img_pil)

    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
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

    grain_noise = np.random.randint(-4, 5, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        scale = 1.0 + 0.12 * np.sin(prog * np.pi * 0.5)
        angle = -1.2 + 2.4 * prog

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

        # Banner Superior
        draw.rectangle([(50, 60), (w - 50, 160)], fill=(0, 0, 0, 210))
        draw.rectangle([(50, 60), (65, 160)], fill=(255, 215, 0))
        draw.text((85, 110), subtitle_label.upper(), fill=(255, 215, 0), font=font_banner, anchor="lm")

        # Legendas Dinâmicas
        draw.rectangle([(60, h - 340), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 280), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 200), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()


NORDESTE_SHORTS_BATCH = [
    # SHORT 1: A Lenda do Boto nas Águas do Nordeste
    {
        "topic_id": "short_lenda_do_boto_nordeste",
        "title": "A LENDA DO BOTO DAS ÁGUAS",
        "subtitle": "MISTÉRIOS DOS RIOS DO NORDESTE",
        "scenes": [
            {
                "scene_id": 1,
                "type": "ai_art",
                "label": "O BOTO COR-DE-ROSA",
                "narration": "Você sabia que nas margens dos rios do Nordeste a lenda do Boto Cor-de-Rosa assombra festas de vilarejos?",
                "duration": 8.5,
                "prompt": "Cinematic art 9:16 vertical, handsome mysterious man in white suit and hat walking out of dark misty river at night, pink dolphin shadow in water, 8k"
            },
            {
                "scene_id": 2,
                "type": "ai_art",
                "label": "O HOMEM DE BRANCO E O MISTÉRIO",
                "narration": "Nas noites de luar, ele se transforma em um homem elegante de chapéu para seduzir mulheres antes de sumir no rio ao amanhecer.",
                "duration": 9.0,
                "prompt": "Cinematic 8k painting 9:16 vertical, handsome man with white hat talking at moonlit village festival near river, mystical atmosphere"
            },
            {
                "scene_id": 3,
                "type": "real_photo",
                "label": "ENCANTO DAS ÁGUAS NORDESTINAS",
                "narration": "Conhecia a misteriosa lenda do Boto? Deixe seu comentário e siga o canal para mais segredos do nosso folclore!",
                "duration": 8.0,
                "query": "Rio Sao Francisco sunset river moon",
                "fallback": "Rio Sao Francisco Pernambuco sunset",
                "prompt": "Golden moon over calm river in Brazilian sertao, 8k"
            }
        ]
    },
    # SHORT 2: O Mistério da Pedra do Ingá (Paraíba)
    {
        "topic_id": "short_misterio_pedra_do_inga",
        "title": "O MISTÉRIO DA PEDRA DO INGÁ",
        "subtitle": "ENIGMA ARQUEOLÓGICO DA PARAÍBA",
        "scenes": [
            {
                "scene_id": 1,
                "type": "real_photo",
                "label": "A PEDRA DO INGÁ NA PARAÍBA",
                "narration": "No interior da Paraíba existe um dos maiores mistérios arqueológicos do mundo: a enigmática Pedra do Ingá.",
                "duration": 8.5,
                "query": "Pedra do Inga Paraiba Brazil petroglyphs",
                "fallback": "Pedra do Inga Paraiba",
                "prompt": "Authentic 8k photograph 9:16 vertical, ancient petroglyphs carved on huge rock wall at Pedra do Inga Paraiba Brazil"
            },
            {
                "scene_id": 2,
                "type": "ai_art",
                "label": "PETRÓGLIFOS INDECIFRÁVEIS",
                "narration": "Um gigantesco paredão coberto de símbolos misteriosos esculpidos há milhares de anos por civilizações desconhecidas.",
                "duration": 9.0,
                "prompt": "Cinematic historical art 9:16 vertical, mysterious ancient astronomical symbols carved on giant rock at dusk, glowing golden light"
            },
            {
                "scene_id": 3,
                "type": "real_photo",
                "label": "SEGREDO DA PARAÍBA",
                "narration": "Seriam mapas estelares ou sinais de povos antigos? Comente o que você acha e siga o canal para mais mistérios!",
                "duration": 8.0,
                "query": "Pedra do Inga Paraiba landscape",
                "fallback": "Paraiba sertao landscape sunset",
                "prompt": "Sunset over ancient rock in Paraiba sertao Brazil"
            }
        ]
    },
    # SHORT 3: O Boitatá: A Serpente de Fogo do Agreste
    {
        "topic_id": "short_boitata_do_agreste",
        "title": "O BOITATÁ DO AGRESTE",
        "subtitle": "A SERPENTE DE FOGO DO SERTÃO",
        "scenes": [
            {
                "scene_id": 1,
                "type": "ai_art",
                "label": "A SERPENTE DE FOGO",
                "narration": "Nas noites escuras da caatinga nordestina, vaqueiros relatam encontrar uma gigantesca serpente de fogo brilhante: o Boitatá.",
                "duration": 8.5,
                "prompt": "Cinematic fantasy art 9:16 vertical, glowing fiery giant serpent Boitata slithering through dark dry caatinga forest at night, glowing eyes, 8k"
            },
            {
                "scene_id": 2,
                "type": "ai_art",
                "label": "PROTETOR DAS MATAS",
                "narration": "Dizem que ele protege a caatinga contra quem incendeia as matas, cegando qualquer um que encare seus olhos de fogo.",
                "duration": 9.0,
                "prompt": "Cinematic art 9:16 vertical, terrified Brazilian vaqueiro cowboy on horse looking at glowing fire serpent in dark forest"
            },
            {
                "scene_id": 3,
                "type": "real_photo",
                "label": "MISTÉRIOS DO AGRESTE",
                "narration": "Já ouviu falar do terrível Boitatá do sertão? Deixe seu comentário e siga o canal para mais assombrações!",
                "duration": 8.0,
                "query": "Caatinga Ceara sunset dry forest",
                "fallback": "Caatinga sertao night sky",
                "prompt": "Night sky over dry Caatinga sertao forest Brazil"
            }
        ]
    },
    # SHORT 4: As Cidades Fantasmas do Sertão
    {
        "topic_id": "short_cidades_fantasmas_sertao",
        "title": "CIDADES FANTASMAS DO SERTÃO",
        "subtitle": "VILAS ABANDONADAS DO NORDESTE",
        "scenes": [
            {
                "scene_id": 1,
                "type": "real_photo",
                "label": "VILAS ABANDONADAS NA CAATINGA",
                "narration": "Espalhadas pelos sertões do Nordeste existem vilas inteiras abandonadas após grandes secas históricas.",
                "duration": 8.5,
                "query": "Sertao ghost town abandoned houses Ceara",
                "fallback": "Abandoned house sertao Brazil",
                "prompt": "Authentic photograph 9:16 vertical, old abandoned clay houses in dry Brazilian sertao, spooky atmosphere"
            },
            {
                "scene_id": 2,
                "type": "ai_art",
                "label": "ASSOMBRAÇÕES DA MEIA-NOITE",
                "narration": "Igrejas vazias e ruínas onde moradores locais juram ouvir passos, sussurros e sinos tocando sozinhos à meia-noite.",
                "duration": 9.0,
                "prompt": "Cinematic horror art 9:16 vertical, abandoned old church in desert ghost town under dark starry night sky, ghost shadows, 8k"
            },
            {
                "scene_id": 3,
                "type": "real_photo",
                "label": "RUÍNAS DO SERTÃO",
                "narration": "Teria coragem de passar uma noite em uma cidade fantasma do sertão? Comente e siga o canal!",
                "duration": 8.0,
                "query": "Abandoned church sertao Pernambuco",
                "fallback": "Old Sertao chapel Brazil",
                "prompt": "Sunset over abandoned old chapel in sertao Brazil"
            }
        ]
    },
    # SHORT 5: As Luzes Misteriosas e a Mãe do Ouro
    {
        "scene_id": 1,
        "topic_id": "short_luzes_misteriosas_sertao",
        "title": "AS LUZES MISTERIOSAS DO SERTÃO",
        "subtitle": "A MÃE DO OURO E OS DISCOS VOADORES",
        "scenes": [
            {
                "scene_id": 1,
                "type": "ai_art",
                "label": "ESFERAS LUMINOSAS NAS SERRAS",
                "narration": "Nos céus isolados do interior nordestino, esferas de luz misteriosas cortam as serras e fascinam moradores há gerações.",
                "duration": 8.5,
                "prompt": "Cinematic sci-fi art 9:16 vertical, glowing golden orb UFO flying over dark mountains of Brazilian sertao at night, starry sky, 8k"
            },
            {
                "scene_id": 2,
                "type": "ai_art",
                "label": "A LENDA DA MÃE DO OURO",
                "narration": "Chamadas de 'Mãe do Ouro' ou 'Aparelhos', essas bolas de fogo sobrevoam os picos e desaparecem sem deixar rastros.",
                "duration": 9.0,
                "prompt": "Cinematic art 9:16 vertical, old Brazilian sertanejo farmer pointing at glowing light ball in dark sky over caatinga"
            },
            {
                "scene_id": 3,
                "type": "real_photo",
                "label": "FENÔMENOS INEXPLICÁVEIS",
                "narration": "Já viu alguma luz estranha no céu do sertão? Deixe seu relato nos comentários e siga o canal para mais mistérios!",
                "duration": 8.0,
                "query": "Serra do Araripe night sky stars",
                "fallback": "Sertao night sky stars Ceara",
                "prompt": "Milky way galaxy night sky over Serra do Araripe mountains Brazil"
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


def produce_5_nordeste_shorts():
    print(f"\n==========================================")
    print(f"[PRODUÇÃO EM LOTE V4] 5 Novos Shorts de Lendas e Mistérios do Nordeste")
    print(f"==========================================")

    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"

    for item in NORDESTE_SHORTS_BATCH:
        topic_id = item["topic_id"]
        t1 = item["title"]
        t2 = item["subtitle"]
        scenes = item["scenes"]

        print(f"\n🎬 Processando Short: {t1} ({topic_id})")

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
            img_type = sc["type"]
            narration = sc["narration"]
            dur = sc["duration"]
            label = sc["label"]
            prompt_txt = sc["prompt"]

            raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
            scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

            img_obtained = False
            if img_type == "real_photo":
                query_txt = sc["query"]
                fallback_txt = sc["fallback"]
                img_obtained = fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
            else:
                img_obtained = fetch_ultra_hd_ai_image(prompt_txt, scene_id, raw_img_path)

            if not img_obtained or not raw_img_path.exists():
                create_epic_custom_canvas(scene_id, raw_img_path)

            render_v4_short_clip(raw_img_path, scene_id, narration, label, dur, scene_mp4)

            voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
            asyncio.run(generate_voice(narration, str(voice_path)))

            v_clip = VideoFileClip(str(scene_mp4))
            voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
            voice_dur = voice_clip.duration + 0.1

            v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
            video_clips.append(v_clip)
            audio_clips.append(voice_clip.with_volume_scaled(1.6))

            current_time += voice_dur

        if bgm_path.exists():
            raw_bgm = AudioFileClip(str(bgm_path))
            bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
            audio_clips.append(bgm_clip)

        master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
        comp_v = CompositeVideoClip(video_clips)
        comp_a = CompositeAudioClip(audio_clips)
        comp_v = comp_v.with_audio(comp_a)

        temp_audio = str(output_dir / "temp_audio_short.m4a")
        comp_v.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_audio, remove_temp=True, fps=24, logger=None)

        comp_v.close()
        comp_a.close()
        for vc in video_clips:
            vc.close()
        for ac in audio_clips:
            ac.close()

        print(f"  ✓ Short Concluído ({current_time:.1f}s): {master_path}")

    print(f"\n  🎉 [LOTE V4 CONCLUÍDO] Todos os 5 Shorts do Nordeste foram gerados com Sucesso!")


def main():
    produce_5_nordeste_shorts()


if __name__ == "__main__":
    main()
