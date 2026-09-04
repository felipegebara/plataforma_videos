import os
import sys
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


def create_artistic_illustration(scene_id: int, title_text: str, color_theme: tuple, icon_type: str, out_path: Path):
    """Cria uma ilustração artística HD 9:16 exclusiva para cada cena do mito da Amazônia."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), color=color_theme)
    draw = ImageDraw.Draw(img)

    # Gradient de fundo místico
    for y in range(h):
        r = int(color_theme[0] * (1 - y/h * 0.5))
        g = int(color_theme[1] * (1 - y/h * 0.4))
        b = int(color_theme[2] * (1 - y/h * 0.3))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Desenho de Elementos Artísticos do Mito (Rios, Sol, Selva, Magia, Peixes)
    if icon_type == "river":
        # Rio serpenteante sagrado da Amazônia
        draw.polygon([(0, 1200), (w, 1400), (w, 1920), (0, 1920)], fill=(15, 65, 95))
        draw.polygon([(0, 1400), (w, 1550), (w, 1920), (0, 1920)], fill=(25, 95, 135))
        draw.ellipse([(700, 300), (1000, 600)], fill=(255, 200, 100)) # Sol Místico
    elif icon_type == "artist":
        # Tela de pintura indígena vibrante
        draw.rectangle([(150, 400), (930, 1400)], fill=(35, 25, 20), outline=(212, 175, 55), width=8)
        draw.rectangle([(180, 430), (900, 1370)], fill=(180, 70, 40))
        draw.ellipse([(350, 600), (730, 980)], fill=(240, 180, 60))
    elif icon_type == "entity":
        # Entidade Mística Meno nas matas
        draw.ellipse([(340, 550), (740, 950)], fill=(20, 15, 25))
        draw.ellipse([(430, 680), (480, 730)], fill=(255, 50, 50)) # Olho Vermelho 1
        draw.ellipse([(600, 680), (650, 730)], fill=(255, 50, 50)) # Olho Vermelho 2
    elif icon_type == "warrior":
        # Guerreiro Indígena com Tocha
        draw.rectangle([(500, 700), (580, 1400)], fill=(140, 80, 40))
        draw.ellipse([(480, 500), (600, 620)], fill=(255, 140, 0)) # Fogo da Tocha
    elif icon_type == "confrontation":
        # Confronto Ritual e Magia
        draw.ellipse([(150, 600), (930, 1300)], outline=(100, 240, 255), width=12)
        draw.ellipse([(300, 750), (780, 1150)], fill=(40, 180, 220))
    elif icon_type == "transformation":
        # Explosão de energia mágica na água
        for r in range(400, 50, -50):
            draw.ellipse([(540 - r, 960 - r), (540 + r, 960 + r)], outline=(255, 220, 50), width=6)
    elif icon_type == "sarapo_fish":
        # Peixes Sarapós (Enguias Elétricas) nadando
        draw.arc([(200, 600), (880, 1000)], start=0, end=180, fill=(0, 240, 255), width=24)
        draw.arc([(200, 800), (880, 1200)], start=180, end=360, fill=(0, 240, 255), width=24)
        draw.arc([(200, 1000), (880, 1400)], start=0, end=180, fill=(255, 215, 0), width=24)
    elif icon_type == "fishermen":
        # Pescadores Desana na Canoa
        draw.polygon([(100, 1100), (980, 1100), (850, 1220), (230, 1220)], fill=(80, 45, 20))
        draw.ellipse([(300, 920), (400, 1020)], fill=(40, 20, 10))
        draw.ellipse([(680, 920), (780, 1020)], fill=(40, 20, 10))
    elif icon_type == "museum":
        # Museu da Amazônia MUSA
        draw.rectangle([(200, 600), (880, 1300)], fill=(45, 30, 20), outline=(255, 215, 0), width=6)
        draw.polygon([(150, 600), (540, 350), (930, 600)], fill=(120, 60, 30))
    elif icon_type == "sunset":
        # Pôr do sol amazônico majestoso
        draw.ellipse([(340, 700), (740, 1100)], fill=(255, 120, 30))
        draw.polygon([(0, 1100), (w, 1100), (w, 1920), (0, 1920)], fill=(10, 20, 40))

    # Moldura Artística e Rótulo da Cena
    draw.rectangle([(40, 40), (1040, 1880)], outline=(255, 215, 0, 180), width=6)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    draw.text((540, 1750), f"CENA {scene_id} - MITOLOGIA DESANA/TUYUKA", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

    img.save(out_path, format="PNG")
    print(f"  ✓ Cena {scene_id}: Ilustração Artística Exclusiva 9:16 gerada ({icon_type})")


LONG_ILLUSTRATED_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas brenhas profundas do Rio Uaupés, no Alto Rio Negro, a mitologia dos povos indígenas Desana e Tuyuka guarda um dos contos cosmogônicos mais fascinantes da Amazônia.",
        "duration": 9.0,
        "motion": "zoom_in",
        "theme": (20, 45, 65),
        "icon": "river"
    },
    {
        "scene_id": 2,
        "narration": "Esta narrativa foi preservada pela tradição oral dos pajés e imortalizada nas pinturas vibrantes do mestre artista indígena Feliciano Lana, hoje em acervo no Museu da Amazônia.",
        "duration": 10.0,
        "motion": "pan_left",
        "theme": (70, 35, 20),
        "icon": "artist"
    },
    {
        "scene_id": 3,
        "narration": "Segundo o mito ancestral, nos tempos primordiais, a entidade conhecida como Diabo Sem Cú habitava as densas florestas tropicais, vagando isolada entre as grandes árvores.",
        "duration": 9.5,
        "motion": "zoom_out",
        "theme": (15, 20, 30),
        "icon": "entity"
    },
    {
        "scene_id": 4,
        "narration": "A criatura possuía uma anatomia única e misteriosa: não tinha orifício de saída em seu corpo, o que fazia acumular uma força interna descomunal e uma fúria incansável.",
        "duration": 9.8,
        "motion": "pan_right",
        "theme": (45, 25, 15),
        "icon": "warrior"
    },
    {
        "scene_id": 5,
        "narration": "Em uma noite de grande travessia, guerreiros e sabedores indígenas encontraram a criatura nas margens de uma igarapé sagrada, travando um confronto de espíritos e magia ancestral.",
        "duration": 10.2,
        "motion": "zoom_in",
        "theme": (20, 50, 70),
        "icon": "confrontation"
    },
    {
        "scene_id": 6,
        "narration": "Pressionada pelo poder das rezas dos pajés, a entidade caiu nas águas correntes do rio. Em um estalo mágico, sua energia acumulada se transformou e se dissipou na água.",
        "duration": 9.5,
        "motion": "pan_left",
        "theme": (60, 50, 15),
        "icon": "transformation"
    },
    {
        "scene_id": 7,
        "narration": "Foi nesse momento exato que nasceram os sarapós, os famosos peixes elétricos de corpo alongado que habitam o leito dos rios amazônicos, conhecidos por emitirem impulsos de energia.",
        "duration": 10.0,
        "motion": "zoom_out",
        "theme": (10, 60, 80),
        "icon": "sarapo_fish"
    },
    {
        "scene_id": 8,
        "narration": "Para os povos Desana e Tuyuka, a forma fina e ondulante dos peixes sarapós e sua descarga de energia são a lembrança viva da força represada da criatura mitológica.",
        "duration": 9.2,
        "motion": "pan_right",
        "theme": (30, 40, 25),
        "icon": "fishermen"
    },
    {
        "scene_id": 9,
        "narration": "Esta riqueza de simbolismos demonstra como a cosmologia indígena explica a origem da biodiversidade e dos animais através de ensinamentos morais e espirituais.",
        "duration": 9.0,
        "motion": "zoom_in",
        "theme": (40, 25, 20),
        "icon": "museum"
    },
    {
        "scene_id": 10,
        "narration": "Gostou de conhecer a história ilustrada da origem dos sarapós no acervo do MUSA? Compartilhe este vídeo e siga o canal para mais mitos da cultura brasileira!",
        "duration": 9.5,
        "motion": "zoom_out",
        "theme": (60, 30, 15),
        "icon": "sunset"
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


def produce_long_illustrated_video():
    topic_id = "diabo_sem_cu_longo_ilustrado"
    print(f"\n==========================================")
    print(f"[VÍDEO LONGO ILUSTRADO - MUSA] Gerando 10 Cenas Ilustradas HD Exclusivas")
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

    for sc in LONG_ILLUSTRATED_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]
        theme_col = sc["theme"]
        icon_tp = sc["icon"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Criar Ilustração Artística HD 9:16 Exclusiva para a cena
        create_artistic_illustration(scene_id, narration[:30], theme_col, icon_tp, img_path)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 40)
            except Exception:
                font = ImageFont.load_default()

            line1 = "DIABO SEM CÚ"
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
        print(f"  [SCENE] Cena {scene_id} renderizada com ilustração artística ({voice_dur:.2f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final Longo com Áudio
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

    print(f"[OK] VÍDEO LONGO ILUSTRADO DO MUSA CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_long_illustrated_video()


if __name__ == "__main__":
    main()
