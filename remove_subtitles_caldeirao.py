import os
import sys
import time
import json
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

# Safe UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def render_clean_scene_clip_no_subtitles(img_path: Path, scene_id: int, duration: float, movement_type: str, out_mp4_path: Path):
    """
    Renderiza clipe MP4 24 FPS com visual cinematográfico limpo SEM NENHUMA LEGENDA OU TEXTO NA TELA.
    """
    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)

    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    
    if out_mp4_path.exists():
        try:
            out_mp4_path.unlink()
        except Exception:
            pass

    out_v = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        # Seleção de Movimentos de Câmera Parallax 24 FPS
        if movement_type == "drone_reveal":
            scale = 1.15 - 0.12 * prog
            angle = -0.5 + 1.0 * prog
            dx, dy = 0.0, -0.05 * prog
        elif movement_type == "dolly_forward":
            scale = 1.0 + 0.15 * prog
            angle = 0.0
            dx, dy = 0.0, 0.02 * prog
        elif movement_type == "slow_push_in":
            scale = 1.0 + 0.12 * (prog ** 1.5)
            angle = 0.0
            dx, dy = 0.0, 0.0
        elif movement_type == "handheld_documentary":
            scale = 1.05 + 0.03 * np.sin(prog * np.pi * 4.0)
            angle = 0.8 * np.sin(prog * np.pi * 3.0)
            dx = 0.02 * np.cos(prog * np.pi * 5.0)
            dy = 0.02 * np.sin(prog * np.pi * 4.0)
        elif movement_type == "drone_orbit":
            scale = 1.08 + 0.04 * np.cos(prog * np.pi * 2.0)
            angle = -2.0 + 4.0 * prog
            dx = 0.03 * np.sin(prog * np.pi * 2.0)
            dy = 0.0
        else: # slow_zoom_out
            scale = 1.15 - 0.15 * prog
            angle = 0.5 - 1.0 * prog
            dx, dy = 0.0, 0.0

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)

        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), angle, 1.0)
        frame_rot = cv2.warpAffine(frame_res, M, (nw, nh), flags=cv2.INTER_CUBIC)

        sx = int((nw - w) * (0.5 + dx))
        sy = int((nh - h) * (0.5 + dy))

        sx = max(0, min(sx, nw - w))
        sy = max(0, min(sy, nh - h))

        frame_cropped = frame_rot[sy : sy + h, sx : sx + w].copy()
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)

        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        # Moldura Cinematográfica Dourada (Sem Legendas)
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CENA {scene_id} LIMPA SEM LEGENDAS RENDERIZADA] ({duration:.1f}s)")


SCENES_NO_SUBTITLES = [
    (1, 8.5, "drone_reveal", "Poucos sabem, mas anos após o fim de Canudos, o sertão do Ceará abrigou uma das comunidades mais prósperas e misteriosas da história do Brasil!"),
    (2, 9.0, "dolly_forward", "Em 1920, o Beato José Lourenço fundou na Serra do Araripe o Caldeirão de Santa Cruz, com a bênção solene do lendário Padre Cícero!"),
    (3, 8.5, "slow_push_in", "Sem dinheiro nem patrões, os fiéis trabalhavam juntos nas colheitas, transformando a seca em fartura com açudes e lavouras coletivas!"),
    (4, 9.0, "handheld_documentary", "Impressionados com o crescimento do arraial, grandes fazendeiros e autoridades da época começaram a observar o movimento com apreensão!"),
    (5, 9.5, "slow_push_in", "Em 1937, o arraial foi cercado e desfeito, deixando para trás apenas as ruínas de pedra e a memória de um sonho no sertão."),
    (6, 8.0, "slow_zoom_out", "O Caldeirão tornou-se símbolo de fé e perseverança no Ceará. Já conhecia essa história impressionante? Deixe seu comentário e siga o canal!")
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


def remove_subtitles_caldeirao():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-RENDERIZAÇÃO DO VÍDEO COMPLETO SEM LEGENDAS]")
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

    for scene_id, dur, mov_type, text in SCENES_NO_SUBTITLES:
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        # 1. Renderizar Clipe Sem Legendas
        if formatted_img_path.exists():
            render_clean_scene_clip_no_subtitles(formatted_img_path, scene_id, dur, mov_type, scene_mp4)

        # 2. Gerar / Carregar Voz Humana Neural
        if not voice_path.exists():
            asyncio.run(generate_voice(text, str(voice_path)))

        # 3. Acoplar Vídeo e Áudio
        if scene_mp4.exists():
            v_clip = VideoFileClip(str(scene_mp4))
            voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
            voice_dur = voice_clip.duration + 0.1

            v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
            video_clips.append(v_clip)
            audio_clips.append(voice_clip.with_volume_scaled(1.6))

            current_time += voice_dur
            print(f"    [CLIP LIMPO OK] Cena {scene_id}/6 acoplada ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 4. Trilha Sonora de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 5. Exportar Vídeo Master Final sem legendas
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_no_subtitles.m4a")

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio_file,
        remove_temp=True,
        fps=24,
        logger=None
    )

    comp_v.close()
    comp_a.close()
    for vc in video_clips:
        vc.close()
    for ac in audio_clips:
        ac.close()

    print(f"\n  🎉 [REMOÇÃO DE LEGENDAS CONCLUÍDA] VÍDEO COMPLETO LIMPO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    remove_subtitles_caldeirao()


if __name__ == "__main__":
    main()
