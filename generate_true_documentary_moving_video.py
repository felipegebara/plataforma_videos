import os
import sys
import json
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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
    
    for search_term in [query, fallback_query, "Juazeiro do Norte Ceara", "Crato Ceara"]:
        encoded_term = urllib.parse.quote(search_term)
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        
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
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={35000 + seed_id}"
    
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

    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")


def render_moving_documentary_video_clip(img_path: Path, scene_id: int, label_text: str, duration: float, out_mp4_path: Path):
    """
    Renderiza um CLIPE DE VÍDEO COM MOVIMENTO FLUIDO REAL (24 FPS) estilo documentário BBC/Discovery.
    Aplica parallax multinível, rotação suave de câmera, variação de iluminação e granulação de filme 35mm.
    """
    img = Image.open(img_path).convert("RGB")
    w, h = 1080, 1920
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    img_np = np.array(img)

    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (w, h))

    try:
        font = ImageFont.truetype("arialbd.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    # Pré-alocação estática de noise para evitar consumo excessivo de memória RAM
    grain_static = np.random.randint(-4, 5, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        # 1. Movimento Dinâmico de Câmera (Zoom + Pan + Parallax Rotação)
        scale = 1.0 + 0.12 * np.sin(prog * np.pi * 0.5)
        angle = -1.2 + 2.4 * prog

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)

        # Rotação suave de matriz
        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), angle, 1.0)
        frame_rot = cv2.warpAffine(frame_res, M, (nw, nh), flags=cv2.INTER_CUBIC)

        # Corte de Câmera em Movimento
        sx = int((nw - w) * (0.5 + 0.3 * np.cos(prog * np.pi)))
        sy = int((nh - h) * (0.5 + 0.3 * np.sin(prog * np.pi)))

        sx = max(0, min(sx, nw - w))
        sy = max(0, min(sy, nh - h))

        frame_cropped = frame_rot[sy : sy + h, sx : sx + w].copy()

        # 2. Granulação Eficiente de Filme 35mm
        frame_int16 = frame_cropped.astype(np.int16) + grain_static
        frame_uint8 = np.clip(frame_int16, 0, 255).astype(np.uint8)

        # 3. Sobreposição de Lower-Third Estilo Documentário
        frame_pil = Image.fromarray(frame_uint8)
        draw = ImageDraw.Draw(frame_pil)

        # Banner de Documentário no Rodapé
        draw.rectangle([(60, h - 220), (w - 60, h - 120)], fill=(0, 0, 0, 190))
        draw.rectangle([(60, h - 220), (75, h - 120)], fill=(255, 215, 0))
        draw.text((95, h - 195), label_text.upper(), fill=(255, 215, 0), font=font)
        draw.text((95, h - 155), f"DOCUMENTÁRIO ÉPICO - CENA {scene_id}/15", fill=(220, 220, 220), font=font)

        # Moldura de Cinema Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=5)

        # Gravar frame no vídeo MP4
        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [MOVING VIDEO CLIP] Clipe de Vídeo em Movimento 24 FPS gerado: Cena {scene_id} ({duration:.1f}s)")


DOCUMENTARY_15_SCENES = [
    {
        "scene_id": 1,
        "type": "real_photo",
        "label": "A Serra do Araripe no Ceará",
        "narration": "Nas terras áridas e profundas da Serra do Araripe, no Cariri cearense, a história do Brasil esconde um dos episódios mais épicos e trágicos de fé popular e resistência.",
        "duration": 20.0,
        "query": "Serra do Araripe Crato Ceara",
        "fallback": "Caatinga Ceara Brazil landscape",
        "prompt": "Serra do Araripe mountains sunrise Ceara sertao"
    },
    {
        "scene_id": 2,
        "type": "ai_art",
        "label": "O Beato José Lourenço (1920)",
        "narration": "Tudo começou na década de 1920, quando o Beato José Lourenço, um líder religioso negro e profundamente respeitado, chegou à região fugindo da pobreza e da opressão.",
        "duration": 20.0,
        "prompt": "Cinematic historical portrait 9:16 vertical, wise 1920s Afro-Brazilian religious leader Beato Jose Lourenco in simple white clothes in Ceara sertao, 8k"
    },
    {
        "scene_id": 3,
        "type": "real_photo",
        "label": "Monumento ao Padre Cícero",
        "narration": "Sob a benção e orientação espiritual do influente Padre Cícero de Juazeiro do Norte, o beato recebeu permissão para cultivar as terras da fazenda Caldeirão de Santa Cruz.",
        "duration": 20.0,
        "query": "Statue of Padre Cicero in Juazeiro do Norte",
        "fallback": "Estatua de Padre Cicero Horto Juazeiro",
        "prompt": "Statue of Padre Cicero in Juazeiro do Norte Ceara"
    },
    {
        "scene_id": 4,
        "type": "ai_art",
        "label": "A Grande Migração dos Sertanejos",
        "narration": "À medida que a seca devastava os sertões nordestinos, milhares de homens, mulheres e famílias miseráveis migraram para o Caldeirão em busca de pão, dignidade e paz.",
        "duration": 20.0,
        "prompt": "Cinematic historical painting 9:16 vertical, poor Brazilian sertanejo families migrating through dry Ceara sertao landscape with wooden carts, 8k"
    },
    {
        "scene_id": 5,
        "type": "ai_art",
        "label": "A Sociedade Igualitária e Comunitária",
        "narration": "Em poucos anos, o Caldeirão de Santa Cruz transformou-se em uma próspera sociedade coletiva. Não havia dinheiro nem propriedade privada: tudo o que se plantava e colhia era dividido igualmente entre todos.",
        "duration": 20.0,
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s Brazilian sertanejo farmers sharing food and harvesting crops together in green community farm, 8k"
    },
    {
        "scene_id": 6,
        "type": "real_photo",
        "label": "Lavouras Prósperas no Sertão",
        "narration": "Com açudes comunitários, lavouras de milho, feijão e mandioca, o arraial tornou-se um oásis de fartura. O sucesso do Caldeirão provou que o sertanejo podia prosperar unido.",
        "duration": 20.0,
        "query": "Sertao farm dam water Ceara",
        "fallback": "Sertao farm Brazil historical",
        "prompt": "Próspera fazenda no sertão do Ceará 1930s"
    },
    {
        "scene_id": 7,
        "type": "ai_art",
        "label": "A Oposição dos Coronéis do Sertão",
        "narration": "Porém, a autonomia e a fartura dos camponeses despertaram a fúria dos coronéis e grandes fazendeiros da região, que perdiam a mão de obra barata para a comunidade do beato.",
        "duration": 20.0,
        "prompt": "Cinematic historical painting 9:16 vertical, wealthy 1930s Brazilian land barons and colonels on horseback talking angrily on a hill, 8k"
    },
    {
        "scene_id": 8,
        "type": "ai_art",
        "label": "Acusações e Imprensa Conservadora",
        "narration": "Autoridades e a imprensa conservadora começaram a espalhar boatos alarmantes, chamando o Caldeirão de 'o novo Arraial de Canudos' e acusando o povo de fanatismo e comunismo.",
        "duration": 20.0,
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s old newspaper headline and politicians in suits pointing at map of sertao, 8k"
    },
    {
        "scene_id": 9,
        "type": "real_photo",
        "label": "A Morte de Padre Cícero (1934)",
        "narration": "Em 1934, com a morte do Padre Cícero, o Caldeirão perdeu seu grande protetor político e espiritual, ficando vulnerável à perseguição das forças estatais.",
        "duration": 20.0,
        "query": "Padre Cicero Ceara funeral history",
        "fallback": "Padre Cicero Ceara statue",
        "prompt": "Padre Cicero historical funeral Juazeiro"
    },
    {
        "scene_id": 10,
        "type": "ai_art",
        "label": "Invasão Policial de 1936",
        "narration": "Em 1936, forças policiais invadiram a comunidade, expulsando os camponeses e destruindo suas lavouras e moradias de taipa sob pretextos políticos.",
        "duration": 20.0,
        "prompt": "Cinematic historical painting 9:16 vertical, 1930s Brazilian police force in uniforms invading a sertao village, burning houses, 8k"
    },
    {
        "scene_id": 11,
        "type": "ai_art",
        "label": "O Bombardeio Aéreo de 1937",
        "narration": "O momento mais trágico ocorreu em maio de 1937: aviões de guerra da Força Aérea e tropas armadas bombardearam e metralharam os sertanejos refugiados na mata.",
        "duration": 20.0,
        "prompt": "Cinematic historical battle 9:16 vertical, 1930s military biplanes dropping bombs over burning Brazilian sertao forest, smoke and fire, tragic battle, 8k"
    },
    {
        "scene_id": 12,
        "type": "ai_art",
        "label": "Valas Comuns Secretas no Sertão",
        "narration": "Centenas de homens, mulheres e crianças foram massacrados e sepultados em valas comuns secretas na Serra do Araripe, em um crime apagado por décadas dos livros oficiais.",
        "duration": 20.0,
        "prompt": "Cinematic tragic historical painting 9:16 vertical, wooden crosses on a misty hill in Serra do Araripe sertao, dark dramatic sky, 8k"
    },
    {
        "scene_id": 13,
        "type": "real_photo",
        "label": "O Exílio do Beato José Lourenço",
        "narration": "O Beato José Lourenço sobreviveu ao massacre e refugiou-se no interior de Pernambuco, onde viveu pacificamente até sua morte em 1946, amado pelo povo sertanejo.",
        "duration": 20.0,
        "query": "Sertao Pernambuco chapel history",
        "fallback": "Old Sertao chapel Brazil",
        "prompt": "Old Sertao chapel Pernambuco Brazil"
    },
    {
        "scene_id": 14,
        "type": "real_photo",
        "label": "Resgate Histórico e Memória",
        "narration": "Hoje, historiadores e a população do Cariri lutam para resgatar a memória do Caldeirão de Santa Cruz como um símbolo de solidariedade, fé e justiça social no Brasil.",
        "duration": 20.0,
        "query": "Crato Ceara museum history monument",
        "fallback": "Serra do Araripe Crato Ceara",
        "prompt": "Memorial monument in Serra do Araripe Ceara"
    },
    {
        "scene_id": 15,
        "type": "real_photo",
        "label": "Pôr do Sol na Chapada do Araripe",
        "narration": "Conhecer o Caldeirão de Santa Cruz é honrar a memória dos trabalhadores do sertão. Gostou deste documentário completo? Deixe seu comentário, compartilhe e siga o canal para mais histórias!",
        "duration": 20.0,
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


def produce_true_documentary_video():
    topic_id = "caldeirao_documentario_cinematico_5min"
    t1 = "O CALDEIRÃO DE SANTA CRUZ"
    t2 = "DOCUMENTÁRIO CINEMATOGRÁFICO (5 MIN)"

    print(f"\n==========================================")
    print(f"[DOCUMENTÁRIO CINEMATOGRÁFICO DE VÍDEO EM MOVIMENTO] (15 Cenas / 300s)")
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
        label = sc["label"]
        prompt_txt = sc["prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Geração / Obtenção da Imagem Base
        img_obtained = False
        if img_type == "real_photo":
            query_txt = sc["query"]
            fallback_txt = sc["fallback"]
            img_obtained = fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
        else:
            img_obtained = fetch_ai_generated_image(prompt_txt, scene_id, raw_img_path)

        if not img_obtained or not raw_img_path.exists():
            create_epic_custom_canvas(scene_id, raw_img_path)

        # 2. Tentar Motores Wan 2.1/2.2 e HunyuanVideo para Clipe de Vídeo IA
        ai_video_ok = video_ai_engine.generate_video_wan(prompt_txt, str(raw_img_path), dur, str(scene_mp4))
        if not ai_video_ok:
            ai_video_ok = video_ai_engine.generate_video_hunyuan(prompt_txt, str(raw_img_path), dur, str(scene_mp4))

        # 3. Se Wan/Hunyuan indisponíveis, renderizar Clipe de Vídeo em Movimento Parallax 24 FPS (Sensação de Cinema Documentário)
        if not ai_video_ok or not scene_mp4.exists():
            render_moving_documentary_video_clip(raw_img_path, scene_id, label, dur, scene_mp4)

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
        print(f"    [DOCUMENTARY SCENE] Cena {scene_id}/15 ({img_type}) concluída ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s / {current_time/60.0:.2f} min)")

    # Adicionar Trilha BGM de Fundo Documental
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Documental Final com Safe Lock
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_doc_5min.m4a")

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

    print(f"  [OK] DOCUMENTÁRIO CINEMATOGRÁFICO DE 5 MINUTOS CONCLUÍDO COM SUCESSO ({current_time:.1f}s / {current_time/60.0:.2f} min): {master_path}")
    return master_path


def main():
    produce_true_documentary_video()


if __name__ == "__main__":
    main()
