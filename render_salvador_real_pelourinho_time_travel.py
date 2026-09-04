import os
import sys
import time
import shutil
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

def render_real_pelourinho_time_travel():
    topic_id = "salvador_pelourinho_real_timetravel"
    print("=== RE-RENDERIZANDO VÍDEO COM A FOTO REAL DO PELOURINHO EM SALVADOR ===")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / "pelourinho_real"
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    fmt_mod = images_dir / "pelourinho_real_modern.png"
    fmt_past = images_dir / "pelourinho_real_1880.png"

    if not fmt_mod.exists():
        print("Error: pelourinho_real_modern.png not found!")
        return

    shutil.copy(fmt_mod, artifacts_dir / "salvador_pelourinho_real_modern.png")
    shutil.copy(fmt_past, artifacts_dir / "salvador_pelourinho_real_1880.png")

    narration_parts = [
        ("scene1", "Veja o famoso Largo do Pelourinho em Salvador hoje, no coração do centro histórico da Bahia."),
        ("scene2", "Agora, repare na transição temporal viajando 140 anos no tempo para 1880! As pedras coloniais e a iluminação em sépia original."),
        ("scene3", "Uma viagem fascinante pela história de Salvador! Deixe nos comentários qual cidade quer ver no passado e siga o Rota Calculada!")
    ]

    for name, txt in narration_parts:
        asyncio.run(generate_voice(txt, str(audio_dir / f"voice_{name}.mp3")))

    v1_audio = AudioFileClip(str(audio_dir / "voice_scene1.mp3"))
    dur1 = v1_audio.duration + 0.2
    scene1_mp4 = output_dir / "scene1.mp4"
    render_clip(fmt_mod, dur1, "PELOURINHO - SALVADOR HOJE 📍", "CENTRO HISTÓRICO DA BAHIA", scene1_mp4, is_hook=True)

    v2_audio = AudioFileClip(str(audio_dir / "voice_scene2.mp3"))
    dur2 = v2_audio.duration + 0.2
    scene2_mp4 = output_dir / "scene2.mp4"
    render_morph_clip(fmt_mod, fmt_past, dur2, "PELOURINHO EM 1880 📜", "TRANSIÇÃO NO MESMO ÂNGULO", scene2_mp4)

    v3_audio = AudioFileClip(str(audio_dir / "voice_scene3.mp3"))
    dur3 = v3_audio.duration + 0.2
    scene3_mp4 = output_dir / "scene3.mp4"
    render_clip(fmt_past, dur3, "QUAL A PRÓXIMA CIDADE? 👇", "SIGA @ROTACALCULADA", scene3_mp4, is_hook=False)

    c1 = VideoFileClip(str(scene1_mp4)).with_start(0).with_duration(dur1)
    c2 = VideoFileClip(str(scene2_mp4)).with_start(dur1).with_duration(dur2)
    c3 = VideoFileClip(str(scene3_mp4)).with_start(dur1 + dur2).with_duration(dur3)

    a1 = v1_audio.with_start(0).with_volume_scaled(1.6)
    a2 = v2_audio.with_start(dur1).with_volume_scaled(1.6)
    a3 = v3_audio.with_start(dur1 + dur2).with_volume_scaled(1.6)

    video_clips = [c1, c2, c3]
    audio_clips = [a1, a2, a3]
    total_dur = dur1 + dur2 + dur3

    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(total_dur, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(output_dir / "temp_audio_real_pelo.m4a")

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio,
        remove_temp=True,
        fps=24,
        logger=None
    )

    comp_v.close()
    comp_a.close()
    for c in video_clips:
        c.close()
    for a in audio_clips:
        a.close()

    print(f"\n🎉 VÍDEO REAL DO PELOURINHO CONCLUÍDO COM SUCESSO ({total_dur:.1f}s): {master_path}")

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+4%")
    await communicate.save(out_path)

def render_clip(img_path: Path, dur: float, title: str, sub: str, out_mp4: Path, is_hook: bool = False):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)
        scale = 1.0 + 0.12 * prog

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w) * 0.5)
        sy = int((nh - h) * 0.5)
        frame_cropped = frame_res[sy : sy + h, sx : sx + w].copy()
        frame_cropped = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_CUBIC)
        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        if is_hook and f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), title, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_banner, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
        out_v.write(cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR))

    out_v.release()

def render_morph_clip(img1_path: Path, img2_path: Path, dur: float, title: str, sub: str, out_mp4: Path):
    w, h = 1080, 1920
    fps = 24
    total_frames = int(dur * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_v = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    img1_np = cv2.resize(np.array(Image.open(img1_path).convert("RGB")), (w, h))
    img2_np = cv2.resize(np.array(Image.open(img2_path).convert("RGB")), (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        alpha = f_idx / float(total_frames)
        blended = cv2.addWeighted(img1_np, 1.0 - alpha, img2_np, alpha, 0)

        frame_grain = np.clip(blended.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)
        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        if f_idx < int(2.5 * fps):
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), title, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_banner, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
        out_v.write(cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR))

    out_v.release()

if __name__ == "__main__":
    render_real_pelourinho_time_travel()
