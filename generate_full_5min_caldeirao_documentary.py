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


def fetch_ai_generated_image(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera ilustração cinematográfica em HD via Pollinations AI Engine."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={25000 + seed_id}"
    
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
    img = Image.new("RGB", (w, h), (40, 25, 20))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        r = int(50 - y/h * 30)
        g = int(30 - y/h * 20)
        b = int(20 - y/h * 10)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Moldura Dourada
    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")
    print(f"    ✓ [CANVAS FALLBACK] Imagem HD gerada com segurança para cena {scene_id}")


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

        draw.text((540, 1780), f"CENA {scene_id}/15 - DOCUMENTÁRIO COMPLETO (5 MIN)", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception:
        create_epic_custom_canvas(scene_id, out_path)


DOCUMENTARY_15_SCENES = [
    {
        "scene_id": 1,
        "type": "real_photo",
        "narration": "Nas terras áridas e profundas da Serra do Araripe, no Cariri cearense, a história do Brasil esconde um dos episódios mais épicos e trágicos de fé popular e resistência.",
        "duration": 20.0,
        "motion": "zoom_in",
        "query": "Serra do Araripe Crato Ceara",
        "fallback": "Caatinga Ceara Brazil landscape",
        "prompt": "Serra do Araripe mountains sunrise Ceara sertao"
    },
    {
        "scene_id": 2,
        "type": "ai_art",
        "narration": "Tudo começou na década de 1920, quando o Beato José Lourenço, um líder religioso negro e profundamente respeitado, chegou à região fugindo da pobreza e da opressão.",
        "duration": 20.0,
        "motion": "pan_left",
        "prompt": "Cinematic historical portrait 9:16 vertical, wise 1920s Afro-Brazilian religious leader Beato Jose Lourenco in simple white clothes in Ceara sertao, 8k"
    },
    {
        "scene_id": 3,
        "type": "real_photo",
        "narration": "Sob a benção e orientação espiritual do influente Padre Cícero de Juazeiro do Norte, o beato recebeu permissão para cultivar as terras da fazenda Caldeirão de Santa Cruz.",
        "duration": 20.0,
        "motion": "zoom_out",
        "query": "Statue of Padre Cicero in Juazeiro do Norte",
        "fallback": "Estatua de Padre Cicero Horto Juazeiro",
        "prompt": "Statue of Padre Cicero in Juazeiro do Norte Ceara"
    },
    {
        "scene_id": 4,
        "type": "ai_art",
        "narration": "À medida que a seca devastava os sertões nordestinos, milhares de homens, mulheres e famílias miseráveis migraram para o Caldeirão em busca de pão, dignidade e paz.",
        "duration": 20.0,
        "motion": "pan_right",
        "prompt": "Cinematic historical painting 9:16 vertical, poor Brazilian sertanejo families migrating through dry Ceara sertao landscape with wooden carts, 8k"
    },
    {
        "scene_id": 5,
        "type": "ai_art",
        "narration": "Em poucos anos, o Caldeirão de Santa Cruz transformou-se em uma próspera sociedade coletiva. Não havia dinheiro nem propriedade privada: tudo o que se plantava e colhia era dividido igualmente entre todos.",
        "duration": 20.0,
        "motion": "zoom_in",
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s Brazilian sertanejo farmers sharing food and harvesting crops together in green community farm, 8k"
    },
    {
        "scene_id": 6,
        "type": "real_photo",
        "narration": "Com açudes comunitários, lavouras de milho, feijão e mandioca, o arraial tornou-se um oásis de fartura. O sucesso do Caldeirão provou que o sertanejo podia prosperar unido.",
        "duration": 20.0,
        "motion": "pan_left",
        "query": "Sertao farm dam water Ceara",
        "fallback": "Sertao farm Brazil historical",
        "prompt": "Próspera fazenda no sertão do Ceará 1930s"
    },
    {
        "scene_id": 7,
        "type": "ai_art",
        "narration": "Porém, a autonomia e a fartura dos camponeses despertaram a fúria dos coronéis e grandes fazendeiros da região, que perdiam a mão de obra barata para a comunidade do beato.",
        "duration": 20.0,
        "motion": "zoom_out",
        "prompt": "Cinematic historical painting 9:16 vertical, wealthy 1930s Brazilian land barons and colonels on horseback talking angrily on a hill, 8k"
    },
    {
        "scene_id": 8,
        "type": "ai_art",
        "narration": "Autoridades e a imprensa conservadora começaram a espalhar boatos alarmantes, chamando o Caldeirão de 'o novo Arraial de Canudos' e acusando o povo de fanatismo e comunismo.",
        "duration": 20.0,
        "motion": "pan_right",
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s old newspaper headline and politicians in suits pointing at map of sertao, 8k"
    },
    {
        "scene_id": 9,
        "type": "real_photo",
        "narration": "Em 1934, com a morte do Padre Cícero, o Caldeirão perdeu seu grande protetor político e espiritual, ficando vulnerável à perseguição das forças estatais.",
        "duration": 20.0,
        "motion": "zoom_in",
        "query": "Padre Cicero Ceara funeral history",
        "fallback": "Padre Cicero Ceara statue",
        "prompt": "Padre Cicero historical funeral Juazeiro"
    },
    {
        "scene_id": 10,
        "type": "ai_art",
        "narration": "Em 1936, forças policiais invadiram a comunidade, expulsando os camponeses e destruindo suas lavouras e moradias de taipa sob pretextos políticos.",
        "duration": 20.0,
        "motion": "pan_left",
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s Brazilian police force in uniforms invading a sertao village, burning houses, 8k"
    },
    {
        "scene_id": 11,
        "type": "ai_art",
        "narration": "O momento mais trágico ocorreu em maio de 1937: aviões de guerra da Força Aérea e tropas armadas bombardearam e metralharam os sertanejos refugiados na mata.",
        "duration": 20.0,
        "motion": "zoom_out",
        "prompt": "Cinematic historical battle 9:16 vertical, 1930s military biplanes dropping bombs over burning Brazilian sertao forest, smoke and fire, tragic battle, 8k"
    },
    {
        "scene_id": 12,
        "type": "ai_art",
        "narration": "Centenas de homens, mulheres e crianças foram massacrados e sepultados em valas comuns secretas na Serra do Araripe, em um crime apagado por décadas dos livros oficiais.",
        "duration": 20.0,
        "motion": "pan_right",
        "prompt": "Cinematic tragic historical painting 9:16 vertical, wooden crosses on a misty hill in Serra do Araripe sertao, dark dramatic sky, 8k"
    },
    {
        "scene_id": 13,
        "type": "real_photo",
        "narration": "O Beato José Lourenço sobreviveu ao massacre e refugiou-se no interior de Pernambuco, onde viveu pacificamente até sua morte em 1946, amado pelo povo sertanejo.",
        "duration": 20.0,
        "motion": "zoom_in",
        "query": "Sertao Pernambuco chapel history",
        "fallback": "Old Sertao chapel Brazil",
        "prompt": "Old Sertao chapel Pernambuco Brazil"
    },
    {
        "scene_id": 14,
        "type": "real_photo",
        "narration": "Hoje, historiadores e a população do Cariri lutam para resgatar a memória do Caldeirão de Santa Cruz como um símbolo de solidariedade, fé e justiça social no Brasil.",
        "duration": 20.0,
        "motion": "pan_left",
        "query": "Crato Ceara museum history monument",
        "fallback": "Serra do Araripe Crato Ceara",
        "prompt": "Memorial monument in Serra do Araripe Ceara"
    },
    {
        "scene_id": 15,
        "type": "real_photo",
        "narration": "Conhecer o Caldeirão de Santa Cruz é honrar a memória dos trabalhadores do sertão. Gostou deste documentário completo? Deixe seu comentário, compartilhe e siga o canal para mais histórias!",
        "duration": 20.0,
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


def produce_full_5min_caldeirao_documentary():
    topic_id = "caldeirao_documentario_completo_5min"
    t1 = "O CALDEIRÃO DE SANTA CRUZ"
    t2 = "DOCUMENTÁRIO COMPLETO (5 MIN)"

    print(f"\n==========================================")
    print(f"[DOCUMENTÁRIO COMPLETO DE 5 MINUTOS] O Caldeirão de Santa Cruz do Deserto (15 Cenas / 300s)")
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

    for sc in DOCUMENTARY_15_SCENES:
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
        print(f"    [SCENE] Cena {scene_id}/15 ({img_type}) renderizada ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s / {current_time/60.0:.2f} min)")

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

    temp_audio_file = str(output_dir / "temp_audio_caldeirao_5min.m4a")

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

    print(f"  [OK] DOCUMENTÁRIO COMPLETO DE 5 MINUTOS CONCLUÍDO COM SUCESSO ({current_time:.1f}s / {current_time/60.0:.2f} min): {master_path}")
    return master_path


def main():
    produce_full_5min_caldeirao_documentary()


if __name__ == "__main__":
    main()
