import os
import sys
import asyncio
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

downloads_dir = Path(r"C:\Users\fgeba\Downloads\morro azul")
output_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\morro_azul_user_edit")
output_dir.mkdir(parents=True, exist_ok=True)

# Selected clips from user's request
CLIP_HOOK = downloads_dir / "WhatsApp Video 2026-08-04 at 22.10.53.mp4"
CLIP_SCENE = downloads_dir / "WhatsApp Video 2026-08-04 at 22.09.08.mp4"
CLIP_BROLL = downloads_dir / "WhatsApp Video 2026-08-04 at 21.21.16.mp4"
CLIP_OUTRO = downloads_dir / "WhatsApp Video 2026-08-04 at 22.08.28.mp4"

# Audio script matching user prompt
NARRATION_PARTS = [
    ("part1", "Quem olha o Morro Azul de longe em Santa Catarina enxerga esse véu azulado cobrindo as montanhas..."),
    ("part2", "Não é magia e nem portal... é a própria floresta respirando! As árvores liberam óleos essenciais que reagem com a luz do sol..."),
    ("part3", "E tingem a montanha inteira de azul! Siga o Rota Calculada para mais mistérios!")
]

async def generate_narration():
    for name, text in NARRATION_PARTS:
        out_mp3 = output_dir / f"voice_{name}.mp3"
        communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+8%")
        await communicate.save(str(out_mp3))
        print(f"Generated voice {name}: {out_mp3}")

def apply_color_grading_and_crop(frame_bgr, target_w=1080, target_h=1920):
    # Convert to PIL for precision color grading & cropping
    img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    # 9:16 Aspect ratio cropping
    aspect_target = 9 / 16.0
    aspect_img = pil_img.width / float(pil_img.height)

    if aspect_img > aspect_target:
        new_w = int(pil_img.height * aspect_target)
        left = (pil_img.width - new_w) // 2
        pil_img = pil_img.crop((left, 0, left + new_w, pil_img.height))
    else:
        new_h = int(pil_img.width / aspect_target)
        top = (pil_img.height - new_h) // 2
        pil_img = pil_img.crop((0, top, pil_img.width, top + new_h))

    pil_img = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Color grading: +15% Saturation, +10% Contrast, +25% Sharpness
    pil_img = ImageEnhance.Color(pil_img).enhance(1.15)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.10)
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.25)

    # Convert back to numpy BGR
    img_graded = np.array(pil_img)
    
    # Slight cool/blue tint boost for "Morro Azul" atmosphere
    b, g, r = cv2.split(cv2.cvtColor(img_graded, cv2.COLOR_RGB2BGR))
    b = np.clip(b.astype(np.int16) + 4, 0, 255).astype(np.uint8)
    r = np.clip(r.astype(np.int16) - 2, 0, 255).astype(np.uint8)
    
    return cv2.merge([b, g, r])

def process_video_clip(input_mp4: Path, out_mp4: Path, target_dur: float, is_hook: bool = False):
    cap = cv2.VideoCapture(str(input_mp4))
    total_src_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = 24
    target_total_frames = int(target_dur * fps)

    w, h = 1080, 1920
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_writer = cv2.VideoWriter(str(out_mp4), fourcc, fps, (w, h))

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_hook = ImageFont.load_default()

    frames_written = 0
    src_idx = 0

    while frames_written < target_total_frames:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break

        graded_bgr = apply_color_grading_and_crop(frame, w, h)

        # Hook text overlay for the first 2 seconds of hook clip
        if is_hook and frames_written < int(2.0 * fps):
            pil_frame = Image.fromarray(cv2.cvtColor(graded_bgr, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_frame)

            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), "POR QUE ESSE MORRO É SEMPRE AZUL? ⛰️", fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), "MISTÉRIO DO MORRO AZUL - TIMBÓ SC", fill=(255, 255, 255), font=font_hook, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            graded_bgr = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)

        # Cinematic Golden Frame
        cv2.rectangle(graded_bgr, (25, 25), (w - 25, h - 25), (0, 215, 255), 6)

        out_writer.write(graded_bgr)
        frames_written += 1

    cap.release()
    out_writer.release()
    print(f"Processed video clip {out_mp4.name} ({target_dur:.2f}s)")

def main():
    print("=== PROCESSSANDO EDIÇÃO COM SEUS VÍDEOS DE CELULAR DA PASTA MORRO AZUL ===")
    asyncio.run(generate_narration())

    # Measure exact audio lengths
    v1_audio = AudioFileClip(str(output_dir / "voice_part1.mp3"))
    v2_audio = AudioFileClip(str(output_dir / "voice_part2.mp3"))
    v3_audio = AudioFileClip(str(output_dir / "voice_part3.mp3"))

    dur_hook = 2.0
    dur_scene = max(5.0, v1_audio.duration)
    dur_broll = max(5.0, v2_audio.duration)
    dur_outro = max(4.0, v3_audio.duration)

    out_clip1 = output_dir / "rendered_clip1_hook.mp4"
    out_clip2 = output_dir / "rendered_clip2_scene.mp4"
    out_clip3 = output_dir / "rendered_clip3_broll.mp4"
    out_clip4 = output_dir / "rendered_clip4_outro.mp4"

    # Process all 4 raw WhatsApp videos
    process_video_clip(CLIP_HOOK, out_clip1, dur_hook, is_hook=True)
    process_video_clip(CLIP_SCENE, out_clip2, dur_scene, is_hook=False)
    process_video_clip(CLIP_BROLL, out_clip3, dur_broll, is_hook=False)
    process_video_clip(CLIP_OUTRO, out_clip4, dur_outro, is_hook=False)

    # Combine video clips and audio tracks (completely muting original phone microphone noise)
    video_clips = []
    audio_clips = []
    current_time = 0.0

    # 1. Hook Clip (0:00 to 0:02)
    vc1 = VideoFileClip(str(out_clip1)).with_start(current_time).with_duration(dur_hook)
    video_clips.append(vc1)
    current_time += dur_hook

    # 2. Scene Clip (Rampa & Horizonte Azul)
    vc2 = VideoFileClip(str(out_clip2)).with_start(current_time).with_duration(dur_scene)
    ac1 = v1_audio.with_start(current_time).with_volume_scaled(1.6)
    video_clips.append(vc2)
    audio_clips.append(ac1)
    current_time += dur_scene

    # 3. B-Roll Clip (Dentro das Árvores)
    vc3 = VideoFileClip(str(out_clip3)).with_start(current_time).with_duration(dur_broll)
    ac2 = v2_audio.with_start(current_time).with_volume_scaled(1.6)
    video_clips.append(vc3)
    audio_clips.append(ac2)
    current_time += dur_broll

    # 4. Outro Clip (Vista Aberta)
    vc4 = VideoFileClip(str(out_clip4)).with_start(current_time).with_duration(dur_outro)
    ac3 = v3_audio.with_start(current_time).with_volume_scaled(1.6)
    video_clips.append(vc4)
    audio_clips.append(ac3)
    current_time += dur_outro

    # Add background ambient music
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / "morro_azul_user_edit_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(output_dir / "temp_audio_user.m4a")

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
    for v in video_clips:
        v.close()
    for a in audio_clips:
        a.close()

    print(f"\n🎉 VÍDEO EDITADO COM SEUS TAKES DE CELULAR CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")

if __name__ == "__main__":
    main()
