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


OBJECTIVE_CINEMATIC_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas brenhas profundas da floresta amazônica, a mitologia indígena dos povos Desana e Tuyuka relata a história da entidade conhecida como Diabo Sem Cú.",
        "duration": 6.8,
        "motion": "zoom_in",
        "prompt": "Cinematic fantasy concept art 9:16 vertical, giant shadowy mythical forest entity with glowing red eyes standing in dark mist in ancient Amazon rainforest, dramatic volumetric lighting, 8k resolution, trending on ArtStation"
    },
    {
        "scene_id": 2,
        "narration": "Sem orifício de saída em seu corpo, o ser acumulava uma força interna descomunal e perambulava soltando grunhidos pelas trilhas noturnas.",
        "duration": 6.5,
        "motion": "pan_left",
        "prompt": "Cinematic fantasy concept art 9:16 vertical, ancient Amazon jungle trail at midnight, glowing magical aura and dark spirit in rainforest mist, dramatic lighting, 8k resolution"
    },
    {
        "scene_id": 3,
        "narration": "Nas margens do igarapé, pajés e guerreiros indígenas confrontaram a criatura com rezas e rituais mágicos ancestrais.",
        "duration": 6.2,
        "motion": "zoom_out",
        "prompt": "Cinematic fantasy concept art 9:16 vertical, indigenous Amazonian shaman in ritual headdress casting glowing magic at river edge, dramatic night, 8k resolution"
    },
    {
        "scene_id": 4,
        "narration": "Encurralada, a entidade caiu nas águas profundas do rio, onde sua energia represada explodiu e se dissipou na água.",
        "duration": 6.5,
        "motion": "pan_right",
        "prompt": "Cinematic fantasy concept art 9:16 vertical, glowing gold and turquoise magic energy bursting into deep dark river water, bioluminescence, 8k resolution"
    },
    {
        "scene_id": 5,
        "narration": "Dessa transformação nasceram os sarapós, as famosas enguias elétricas que habitam os rios e emitem impulsos de energia.",
        "duration": 6.8,
        "motion": "zoom_in",
        "prompt": "Cinematic underwater fantasy concept art 9:16 vertical, glowing electric knife fish Sarapos swimming in crystal clear Amazon river water, magical light, 8k resolution"
    },
    {
        "scene_id": 6,
        "narration": "Gostou de conhecer a fascinante lenda da origem dos sarapós? Deixe seu comentário e siga o canal para mais mitologias!",
        "duration": 6.0,
        "motion": "zoom_out",
        "prompt": "Cinematic 9:16 vertical, majestic Amazon river sunset with indigenous canoe silhouette, golden glowing reflection, 8k resolution"
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
    print(f"[ROTEIRO DIRETO & IMAGENS CINEMÁTICAS] Gerando Vídeo Objetivo (6 Cenas de Alta Qualidade)")
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
        prompt_txt = sc["prompt"]

        img_path = images_dir / f"scene_{scene_id}.png"

        # Geração da Ilustração Cinematográfica HD 9:16 via Pollinations AI
        enc_p = urllib.parse.quote(prompt_txt)
        ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={5500 + scene_id}"
        
        download_ok = False
        try:
            req = urllib.request.Request(ai_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                with open(img_path, "wb") as f:
                    f.write(resp.read())
            download_ok = True
            print(f"  ✓ Cena {scene_id}: Imagem Cinematográfica HD 9:16 gerada com sucesso")
        except Exception as e:
            print(f"  ⚠️ Erro ao gerar imagem cinematográfica da cena {scene_id} ({e})")

        if not download_ok:
            img = Image.new("RGB", (1080, 1920), (15, 30, 20))
            img.save(img_path)

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
        print(f"  [SCENE] Cena {scene_id} renderizada com imagem cinematográfica ({voice_dur:.2f}s)")

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

    print(f"[OK] VÍDEO OBJETIVO E CINEMATOGRÁFICO CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_objective_cinematic_video()


if __name__ == "__main__":
    main()
