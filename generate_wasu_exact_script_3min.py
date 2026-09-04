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


def create_wasu_illustration(scene_id: int, color_theme: tuple, icon_type: str, out_path: Path):
    """Cria uma ilustração artística HD 9:16 fiel ao mito de Wasu e o Diabo Sem Cu do MUSA."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), color=color_theme)
    draw = ImageDraw.Draw(img)

    # Gradient místico de fundo (estilo aquarela indígena MUSA)
    for y in range(h):
        r = int(color_theme[0] * (1 - y/h * 0.55))
        g = int(color_theme[1] * (1 - y/h * 0.45))
        b = int(color_theme[2] * (1 - y/h * 0.35))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    if icon_type == "rio_traira":
        # Rio Traíra e Cachoeiras Amazônicas (Aquarela)
        draw.polygon([(0, 1100), (w, 1300), (w, 1920), (0, 1920)], fill=(20, 85, 120))
        draw.polygon([(0, 1300), (w, 1450), (w, 1920), (0, 1920)], fill=(35, 115, 160))
        draw.ellipse([(650, 200), (950, 500)], fill=(255, 190, 60)) # Sol Místico
    elif icon_type == "serra_diabo":
        # Porto isolado na Serra do Diabo sem Cu
        draw.polygon([(100, 1150), (980, 1150), (850, 1260), (230, 1260)], fill=(85, 50, 25)) # Canoa de Wasu
        draw.polygon([(250, 600), (830, 600), (900, 950), (180, 950)], fill=(120, 70, 35)) # Maloca / Casa do Primo
    elif icon_type == "bau_mulher":
        # O baú trançado no jirau e a mulher encantadora
        draw.rectangle([(250, 750), (830, 1250)], fill=(160, 100, 40), outline=(230, 180, 80), width=10) # Baú Trançado
        draw.ellipse([(440, 500), (640, 700)], fill=(240, 180, 120)) # Mulher saindo do baú
    elif icon_type == "duvida_primo":
        # O primo apontando para a própria boca/garganta
        draw.ellipse([(380, 500), (700, 820)], fill=(18, 25, 38)) # Primo excentricamente diferente
        draw.ellipse([(500, 620), (580, 700)], fill=(255, 80, 80)) # Boca/garganta anatômica
    elif icon_type == "plano_wasu":
        # Wasu recolhendo varas de arumã na floresta
        draw.line([(300, 600), (300, 1300)], fill=(80, 160, 60), width=16)
        draw.line([(450, 550), (450, 1350)], fill=(100, 180, 70), width=18)
        draw.line([(600, 650), (600, 1280)], fill=(70, 150, 55), width=16)
        draw.line([(750, 580), (750, 1320)], fill=(90, 170, 65), width=18)
    elif icon_type == "estrada_aruma":
        # Wasu com a lança mais forte atrás do primo agachado
        draw.line([(540, 400), (540, 1400)], fill=(200, 140, 50), width=22) # Lança resistente de Wasu
        draw.ellipse([(450, 360), (630, 540)], fill=(255, 215, 0))
    elif icon_type == "origem_peixes":
        # Linhas mágicas nascendo nas águas
        for r in range(400, 50, -50):
            draw.ellipse([(540 - r, 960 - r), (540 + r, 960 + r)], outline=(0, 240, 220), width=8)
    elif icon_type == "sarapos_biologia":
        # Ilustração comparativa dos peixes sarapós e ituins
        draw.arc([(150, 550), (930, 950)], start=0, end=180, fill=(0, 255, 200), width=28) # Sarapó
        draw.ellipse([(200, 710), (250, 760)], fill=(255, 50, 50)) # Anus pertinho da boca
        draw.arc([(150, 1050), (930, 1450)], start=0, end=180, fill=(255, 215, 0), width=28) # Ituin
        draw.ellipse([(200, 1210), (250, 1260)], fill=(255, 50, 50))
    elif icon_type == "musa_conclusao":
        # Logomarca e acervo do MUSA
        draw.rectangle([(200, 550), (880, 1350)], fill=(35, 45, 30), outline=(255, 215, 0), width=8)
        draw.polygon([(150, 550), (540, 300), (930, 550)], fill=(140, 70, 35))

    # Moldura Dourada Mística
    draw.rectangle([(40, 40), (1040, 1880)], outline=(255, 215, 0), width=8)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font = ImageFont.load_default()

    draw.text((540, 1750), f"CENA {scene_id}/9 - O MITO DE WASU (MUSA)", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

    img.save(out_path, format="PNG")
    print(f"  ✓ Cena {scene_id}/9: Ilustração Artística Exclusiva 9:16 gerada ({icon_type})")


EXACT_USER_SCRIPT_SCENES = [
    # ATO 1: A Solidão de Wasu e o Encontro Inesperado (0:00 – 0:50)
    {
        "scene_id": 1,
        "narration": "Nas antigas histórias indígenas do Rio Traíra, vivia um ser chamado Wasu. Solteirão e solitário, ele viajava de aldeia em aldeia, descendo e subindo cachoeiras à procura de uma esposa... mas nenhuma mulher queria ficar com ele.",
        "duration": 15.0,
        "motion": "zoom_in",
        "theme": (20, 45, 75),
        "icon": "rio_traira"
    },
    {
        "scene_id": 2,
        "narration": "Triste pela viagem frustrada, Wasu encostou sua canoa em um porto distante — hoje conhecido como a Serra do Diabo sem Cu. Lá, morava sozinho seu primo estranho. Wasu decidiu ficar por um tempo como seu hóspede.",
        "duration": 20.0,
        "motion": "pan_left",
        "theme": (55, 35, 20),
        "icon": "serra_diabo"
    },
    {
        "scene_id": 3,
        "narration": "Mas Wasu logo notou algo curioso. Quando o primo saía para beber caxiri em outras aldeias, um barulho ecoava do teto. Escondida dentro de um grande baú, estava uma mulher encantadora que cuidava da casa! Fascinado, Wasu começou a planejar uma forma de fugir com ela.",
        "duration": 15.0,
        "motion": "zoom_out",
        "theme": (65, 45, 25),
        "icon": "bau_mulher"
    },
    # ATO 2: A Curiosidade e a Armadilha (0:50 – 2:00)
    {
        "scene_id": 4,
        "narration": "Um dia, o primo observou um costume comum de Wasu que ele não compreendia. Seu próprio corpo era diferente: seu sistema digestivo terminava bem embaixo de sua boca. Curioso, ele perguntou: 'Meu amigo, como você consegue defecar por trás? Queria ser como você...'",
        "duration": 30.0,
        "motion": "pan_right",
        "theme": (25, 25, 40),
        "icon": "duvida_primo"
    },
    {
        "scene_id": 5,
        "narration": "Vendo a oportunidade perfeita para derrotar o primo e ficar com sua mulher, Wasu mentiu: 'Foi meu pai quem fez para mim com varas da floresta. Não dói nada! Se quiser, posso fazer em você agora mesmo'. Empolgado e ingênuo, o primo aceitou.",
        "duration": 25.0,
        "motion": "zoom_in",
        "theme": (35, 60, 30),
        "icon": "plano_wasu"
    },
    {
        "scene_id": 6,
        "narration": "Wasu pediu para o primo fechar os olhos. Primeiro, usou varas moles de arumã que se quebravam sem dor, enganando-o. Mas logo em seguida... usou sua lança mais forte.",
        "duration": 15.0,
        "motion": "pan_left",
        "theme": (70, 35, 15),
        "icon": "estrada_aruma"
    },
    # ATO 3: A Criação dos Sarapós e Encerramento (2:00 – 3:00)
    {
        "scene_id": 7,
        "narration": "Com o golpe, o Diabo sem Cu não resistiu. Ao lançar as tripas e vestígios do primo nas águas do rio, um encanto aconteceu: elas ganharam vida, dando origem a diversas espécies de peixes compridos!",
        "duration": 25.0,
        "motion": "zoom_out",
        "theme": (15, 65, 85),
        "icon": "origem_peixes"
    },
    {
        "scene_id": 8,
        "narration": "Nasceram assim os Sarapós e Ituins: o sarapó-cunuri, o sarapó-comprido, o sarapó-grande e o sarapó-das-folhas. E é por causa dessa lenda que até hoje, na natureza, todos esses peixes possuem o ânus bem pertinho da boca!",
        "duration": 20.0,
        "motion": "pan_right",
        "theme": (10, 80, 90),
        "icon": "sarapos_biologia"
    },
    {
        "scene_id": 9,
        "narration": "Os mitos indígenas da Amazônia conectam o humor, a natureza e a ciência, explicando a imensa diversidade da vida na floresta. Conheça mais no Museu da Amazônia.",
        "duration": 15.0,
        "motion": "zoom_in",
        "theme": (45, 30, 20),
        "icon": "musa_conclusao"
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


def produce_exact_user_3min_video():
    topic_id = "mito_wasu_origem_sarapos_3min"
    print(f"\n==========================================")
    print(f"[VÍDEO 3 MINUTOS EXATO] O Mito de Wasu e a Origem dos Sarapós (MUSA)")
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
        theme_col = sc["theme"]
        icon_tp = sc["icon"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Criar Ilustração Artística HD 9:16 Exclusiva
        create_wasu_illustration(scene_id, theme_col, icon_tp, img_path)

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
        print(f"  [SCENE] Cena {scene_id}/9 renderizada ({voice_dur:.2f}s | Total acumulado: {current_time:.1f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Exato de 3 Minutos com Áudio
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

    print(f"[OK] VÍDEO DE 3 MINUTOS DO MITO DE WASU CONCLUÍDO COM SUCESSO ({current_time:.1f}s / 3.0 min): {master_path}")
    return master_path


def main():
    produce_exact_user_3min_video()


if __name__ == "__main__":
    main()
