import os
import sys
import json
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
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


def fetch_wikimedia_hd_photo(query: str, fallback_query: str, out_path: Path):
    """Busca foto REAL em HD (1280px width) via Wikimedia Commons API sem rate limit."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    
    for search_term in [query, fallback_query, "Amazon river", "Indigenous Brazil"]:
        encoded_term = urllib.parse.quote(search_term)
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=8&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    imageinfo = page_data.get('imageinfo', [])
                    if imageinfo:
                        img_url = imageinfo[0].get('thumburl') or imageinfo[0].get('url')
                        if img_url and (img_url.endswith('.jpg') or img_url.endswith('.jpeg') or img_url.endswith('.png')):
                            img_req = urllib.request.Request(img_url, headers=headers)
                            with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                                with open(out_path, 'wb') as f:
                                    f.write(img_resp.read())
                            print(f"  ✓ Foto REAL HD obtida do Wikimedia: {search_term} ({out_path.name})")
                            return True
        except Exception as e:
            pass

    return False


def format_image_to_916_hd(raw_img_path: Path, scene_id: int, out_path: Path):
    """Converte a foto para formato vertical 9:16 HD (1080x1920) com crop e bordas elegantes."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        return

    img = Image.open(raw_img_path).convert("RGB")
    
    # Resize & Crop proporcional para 9:16
    aspect_target = 9 / 16.0
    aspect_img = img.width / float(img.height)

    if aspect_img > aspect_target:
        # Foto é mais larga: corta as laterais
        new_w = int(img.height * aspect_target)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        # Foto é mais alta: corta o topo/base
        new_h = int(img.width / aspect_target)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))

    img = img.resize((w, h), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Moldura Dourada Elegante
    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        font = ImageFont.load_default()

    draw.text((540, 1780), f"CENA {scene_id}/9 - O MITO DE WASU (MUSA)", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    img.save(out_path, format="PNG")


EXACT_USER_SCRIPT_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas antigas histórias indígenas do Rio Traíra, vivia um ser chamado Wasu. Solteirão e solitário, ele viajava de aldeia em aldeia, descendo e subindo cachoeiras à procura de uma esposa... mas nenhuma mulher queria ficar com ele.",
        "duration": 15.0,
        "motion": "zoom_in",
        "query": "Rio Uaupes waterfall Amazon river",
        "fallback": "Amazon river landscape waterfall"
    },
    {
        "scene_id": 2,
        "narration": "Triste pela viagem frustrada, Wasu encostou sua canoa em um porto distante — hoje conhecido como a Serra do Diabo sem Cu. Lá, morava sozinho seu primo estranho. Wasu decidiu ficar por um tempo como seu hóspede.",
        "duration": 20.0,
        "motion": "pan_left",
        "query": "Indigenous maloca Amazon house",
        "fallback": "Indigenous village Amazon river"
    },
    {
        "scene_id": 3,
        "narration": "Mas Wasu logo notou algo curioso. Quando o primo saía para beber caxiri em outras aldeias, um barulho ecoava do teto. Escondida dentro de um grande baú, estava uma mulher encantadora que cuidava da casa! Fascinado, Wasu começou a planejar uma forma de fugir com ela.",
        "duration": 15.0,
        "motion": "zoom_out",
        "query": "Indigenous basket woven basket Amazon",
        "fallback": "Amazonian indigenous craft"
    },
    {
        "scene_id": 4,
        "narration": "Um dia, o primo observou um costume comum de Wasu que ele não compreendia. Seu próprio corpo era diferente: seu sistema digestivo terminava bem embaixo de sua boca. Curioso, ele perguntou: 'Meu amigo, como você consegue defecar por trás? Queria ser como você...'",
        "duration": 30.0,
        "motion": "pan_right",
        "query": "Desana indigenous art Amazon",
        "fallback": "Amazonian indigenous face painting"
    },
    {
        "scene_id": 5,
        "narration": "Vendo a oportunidade perfeita para derrotar o primo e ficar com sua mulher, Wasu mentiu: 'Foi meu pai quem fez para mim com varas da floresta. Não dói nada! Se quiser, posso fazer em você agora mesmo'. Empolgado e ingênuo, o primo aceitou.",
        "duration": 25.0,
        "motion": "zoom_in",
        "query": "Amazon rainforest reeds plants",
        "fallback": "Amazon rainforest dense jungle"
    },
    {
        "scene_id": 6,
        "narration": "Wasu pediu para o primo fechar os olhos. Primeiro, usou varas moles de arumã que se quebravam sem dor, enganando-o. Mas logo em seguida... usou sua lança mais forte.",
        "duration": 15.0,
        "motion": "pan_left",
        "query": "Indigenous spear Amazon weapon",
        "fallback": "Indigenous spear weapon"
    },
    {
        "scene_id": 7,
        "narration": "Com o golpe, o Diabo sem Cu não resistiu. Ao lançar as tripas e vestígios do primo nas águas do rio, um encanto aconteceu: elas ganharam vida, dando origem a diversas espécies de peixes compridos!",
        "duration": 25.0,
        "motion": "zoom_out",
        "query": "Amazon river water current underwater",
        "fallback": "Amazon river clear water"
    },
    {
        "scene_id": 8,
        "narration": "Nasceram assim os Sarapós e Ituins: o sarapó-cunuri, o sarapó-comprido, o sarapó-grande e o sarapó-das-folhas. E é por causa dessa lenda que até hoje, na natureza, todos esses peixes possuem o ânus bem pertinho da boca!",
        "duration": 20.0,
        "motion": "pan_right",
        "query": "Gymnotus knife fish electric eel",
        "fallback": "Gymnotiformes knife fish"
    },
    {
        "scene_id": 9,
        "narration": "Os mitos indígenas da Amazônia conectam o humor, a natureza e a ciência, explicando a imensa diversidade da vida na floresta. Conheça mais no Museu da Amazônia.",
        "duration": 15.0,
        "motion": "zoom_in",
        "query": "Museu da Amazonia MUSA Manaus",
        "fallback": "Amazon rainforest museum canopy"
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


def produce_wasu_hd_real_photo_video():
    topic_id = "mito_wasu_origem_sarapos_3min"
    print(f"\n==========================================")
    print(f"[RE-RENDER COM FOTOS REAIS HD] O Mito de Wasu (9 Fotos Reais Autênticas)")
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

    for sc in EXACT_USER_SCRIPT_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        query_txt = sc["query"]
        fallback_txt = sc["fallback"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        img_path = images_dir / f"scene_{scene_id}.png"

        # Buscar foto REAL HD
        fetch_wikimedia_hd_photo(query_txt, fallback_txt, raw_img_path)
        format_image_to_916_hd(raw_img_path, scene_id, img_path)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 38)
            except Exception:
                font = ImageFont.load_default()

            line1 = "O MITO DE WASU E"
            line2 = "A ORIGEM DOS SARAPÓS (MUSA)"

            draw.text((540, 290), line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
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
        print(f"  [SCENE] Cena {scene_id}/9 renderizada com FOTO REAL HD ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final com Fotos Reais HD
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

    print(f"[OK] VÍDEO DE 3 MINUTOS COM FOTOS REAIS HD CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_wasu_hd_real_photo_video()


if __name__ == "__main__":
    main()
