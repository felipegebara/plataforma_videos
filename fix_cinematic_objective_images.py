import os
import sys
import asyncio
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


def create_cinematic_illustration(scene_id: int, color_theme: tuple, icon_type: str, out_path: Path):
    """Cria uma ilustração cinematográfica vibrante HD 9:16 exclusiva para cada cena do vídeo direto."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), color=color_theme)
    draw = ImageDraw.Draw(img)

    # Gradient de fundo cinemático
    for y in range(h):
        r = int(color_theme[0] * (1 - y/h * 0.55))
        g = int(color_theme[1] * (1 - y/h * 0.45))
        b = int(color_theme[2] * (1 - y/h * 0.35))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Desenho de Elementos Cinematográficos (Entidade, Magia, Pajé, Sarapós)
    if icon_type == "entity_intro":
        # Entidade Mística surgindo na névoa da Amazônia
        draw.ellipse([(240, 450), (840, 1050)], fill=(12, 18, 28))
        draw.ellipse([(410, 620), (470, 680)], fill=(255, 40, 40)) # Olho 1
        draw.ellipse([(610, 620), (670, 680)], fill=(255, 40, 40)) # Olho 2
        draw.ellipse([(430, 640), (450, 660)], fill=(255, 255, 255))
        draw.ellipse([(630, 640), (650, 660)], fill=(255, 255, 255))
    elif icon_type == "mystic_trail":
        # Trilha Noturna na Selva com Aura Bioluminescente
        draw.polygon([(400, 1920), (500, 1000), (580, 1000), (680, 1920)], fill=(45, 95, 65))
        draw.ellipse([(350, 500), (730, 880)], outline=(0, 240, 255), width=8)
    elif icon_type == "shaman_ritual":
        # Pajé Indígena Lançando Magia no Igarapé
        draw.polygon([(480, 600), (600, 600), (650, 1200), (430, 1200)], fill=(140, 70, 30))
        draw.ellipse([(450, 420), (630, 600)], fill=(255, 140, 0)) # Cocar Místico
        draw.ellipse([(200, 800), (880, 1200)], outline=(255, 215, 0), width=10) # Feitiço
    elif icon_type == "transformation_burst":
        # Explosão Mística no Leito do Rio
        for r in range(450, 60, -60):
            draw.ellipse([(540 - r, 960 - r), (540 + r, 960 + r)], outline=(0, 240, 220), width=8)
        draw.ellipse([(440, 860), (640, 1060)], fill=(255, 255, 200))
    elif icon_type == "sarapo_electric":
        # Peixes Sarapós (Enguias Elétricas) Bioluminescentes
        draw.arc([(150, 550), (930, 950)], start=0, end=180, fill=(0, 255, 200), width=28)
        draw.arc([(150, 850), (930, 1250)], start=180, end=360, fill=(255, 215, 0), width=28)
        draw.arc([(150, 1150), (930, 1550)], start=0, end=180, fill=(0, 220, 255), width=28)
    elif icon_type == "amazon_sunset":
        # Pôr do sol amazônico majestoso
        draw.ellipse([(340, 650), (740, 1050)], fill=(255, 120, 30))
        draw.polygon([(0, 1050), (w, 1050), (w, 1920), (0, 1920)], fill=(10, 20, 40))

    # Moldura Cinematográfica Elegante Dourada
    draw.rectangle([(40, 40), (1040, 1880)], outline=(255, 215, 0), width=8)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    draw.text((540, 1750), f"CENA {scene_id} - A ORIGEM DOS SARAPÓS", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

    img.save(out_path, format="PNG")
    print(f"  ✓ Cena {scene_id}: Ilustração Cinematográfica Exclusiva HD 9:16 gerada ({icon_type})")


OBJECTIVE_CINEMATIC_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas brenhas profundas da floresta amazônica, a mitologia indígena dos povos Desana e Tuyuka relata a história da entidade conhecida como Diabo Sem Cú.",
        "duration": 6.8,
        "motion": "zoom_in",
        "theme": (15, 25, 40),
        "icon": "entity_intro"
    },
    {
        "scene_id": 2,
        "narration": "Sem orifício de saída em seu corpo, o ser acumulava uma força interna descomunal e perambulava soltando grunhidos pelas trilhas noturnas.",
        "duration": 6.5,
        "motion": "pan_left",
        "theme": (20, 40, 30),
        "icon": "mystic_trail"
    },
    {
        "scene_id": 3,
        "narration": "Nas margens do igarapé, pajés e guerreiros indígenas confrontaram a criatura com rezas e rituais mágicos ancestrais.",
        "duration": 6.2,
        "motion": "zoom_out",
        "theme": (65, 35, 15),
        "icon": "shaman_ritual"
    },
    {
        "scene_id": 4,
        "narration": "Encurralada, a entidade caiu nas águas profundas do rio, onde sua energia represada explodiu e se dissipou na água.",
        "duration": 6.5,
        "motion": "pan_right",
        "theme": (10, 50, 70),
        "icon": "transformation_burst"
    },
    {
        "scene_id": 5,
        "narration": "Dessa transformação nasceram os sarapós, as famosas enguias elétricas que habitam os rios e emitem impulsos de energia.",
        "duration": 6.8,
        "motion": "zoom_in",
        "theme": (10, 70, 80),
        "icon": "sarapo_electric"
    },
    {
        "scene_id": 6,
        "narration": "Gostou de conhecer a fascinante lenda da origem dos sarapós? Deixe seu comentário e siga o canal para mais mitologias!",
        "duration": 6.0,
        "motion": "zoom_out",
        "theme": (70, 30, 15),
        "icon": "amazon_sunset"
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


def produce_objective_cinematic_video():
    topic_id = "diabo_sem_cu_direto_cinematico"
    print(f"\n==========================================")
    print(f"[RE-RENDER DIRETO & CINEMÁTICO] Produzindo 6 Ilustrações HD Exclusivas")
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

    for sc in OBJECTIVE_CINEMATIC_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        theme_col = sc["theme"]
        icon_tp = sc["icon"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Criar Ilustração Cinematográfica Exclusiva
        create_cinematic_illustration(scene_id, theme_col, icon_tp, img_path)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 42)
            except Exception:
                font = ImageFont.load_default()

            line1 = "DIABO SEM CÚ"
            line2 = "A ORIGEM DOS SARAPÓS"

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
        print(f"  [SCENE] Cena {scene_id} renderizada com ilustração cinematográfica ({voice_dur:.2f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Direto e Cinematográfico
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

    print(f"[OK] VÍDEO DIRETO E CINEMATOGRÁFICO RE-RENDERIZADO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_objective_cinematic_video()


if __name__ == "__main__":
    main()
