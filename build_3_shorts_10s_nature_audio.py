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
output_base = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\videos")

# 3 Short configurations matched perfectly to voice narration length
SHORTS_SPECS = [
    {
        "id": "short_morro_azul_10s_1",
        "title": "Short 1: Por Que Essa Montanha É Azul?",
        "hook_text": "POR QUE ESSA MONTANHA É AZUL? ⛰️",
        "sub_text": "MISTÉRIO DO MORRO AZUL - TIMBÓ SC",
        "narration": "Você sabia que o Morro Azul em Santa Catarina está sempre coberto por uma incrível neblina azulada? Siga o Rota Calculada para mais mistérios!",
        "video_clips": [
            downloads_dir / "WhatsApp Video 2026-08-04 at 22.10.53.mp4",
            downloads_dir / "WhatsApp Video 2026-08-04 at 22.09.08.mp4"
        ]
    },
    {
        "id": "short_morro_azul_10s_2",
        "title": "Short 2: A Floresta Respirando",
        "hook_text": "A FLORESTA RESPIRANDO! 🌿",
        "sub_text": "CIÊNCIA DO MORRO AZUL - TIMBÓ SC",
        "narration": "O tom azul do Morro Azul é a própria floresta respirando e liberando óleos essenciais sob a luz do sol! Gostou de saber? Deixe seu comentário!",
        "video_clips": [
            downloads_dir / "WhatsApp Video 2026-08-04 at 21.21.16.mp4",
            downloads_dir / "WhatsApp Video 2026-08-04 at 22.07.44.mp4"
        ]
    },
    {
        "id": "short_morro_azul_10s_3",
        "title": "Short 3: O Mirante do Morro Azul",
        "hook_text": "O VISUAL MAIS LINDO DE SC! 🌅",
        "sub_text": "TIMBÓ & POMERODE - SANTA CATARINA",
        "narration": "A mais de 750 metros de altitude em Timbó, esse mirante incrível proporciona uma das vistas mais inesquecíveis de Santa Catarina! Siga o canal!",
        "video_clips": [
            downloads_dir / "WhatsApp Video 2026-08-04 at 22.08.28.mp4",
            downloads_dir / "WhatsApp Video 2026-08-04 at 22.08.57.mp4"
        ]
    }
]

def apply_color_grading_and_crop(frame_bgr, target_w=1080, target_h=1920):
    img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

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

    pil_img = ImageEnhance.Color(pil_img).enhance(1.15)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.10)
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.25)

    img_graded = np.array(pil_img)
    b, g, r = cv2.split(cv2.cvtColor(img_graded, cv2.COLOR_RGB2BGR))
    b = np.clip(b.astype(np.int16) + 4, 0, 255).astype(np.uint8)
    r = np.clip(r.astype(np.int16) - 2, 0, 255).astype(np.uint8)
    
    return cv2.merge([b, g, r])

def render_short_clip(input_mp4: Path, out_mp4: Path, target_dur: float, hook_text: str, sub_text: str, is_first: bool):
    cap = cv2.VideoCapture(str(input_mp4))
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

    while frames_written < target_total_frames:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break

        graded_bgr = apply_color_grading_and_crop(frame, w, h)

        if is_first and frames_written < int(2.5 * fps):
            pil_frame = Image.fromarray(cv2.cvtColor(graded_bgr, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_frame)

            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub_text, fill=(255, 255, 255), font=font_hook, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            graded_bgr = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)

        cv2.rectangle(graded_bgr, (25, 25), (w - 25, h - 25), (0, 215, 255), 6)

        out_writer.write(graded_bgr)
        frames_written += 1

    cap.release()
    out_writer.release()
    print(f"Rendered clip {out_mp4.name} ({target_dur:.2f}s)")

async def generate_voice(text: str, out_path: str):
    # Natural pacing rate matched to short length
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-2%")
    await communicate.save(out_path)

def build_single_10s_short(spec):
    short_id = spec["id"]
    hook_text = spec["hook_text"]
    sub_text = spec["sub_text"]
    narration_txt = spec["narration"]
    clips = spec["video_clips"]

    out_folder = output_base / short_id
    out_folder.mkdir(parents=True, exist_ok=True)

    voice_mp3 = out_folder / "voice.mp3"
    asyncio.run(generate_voice(narration_txt, str(voice_mp3)))

    v_voice = AudioFileClip(str(voice_mp3))
    # EXACT AUDIO MATCH: Total video length is set exactly to voice duration + 0.3s buffer
    total_short_dur = v_voice.duration + 0.3
    clip_dur = total_short_dur / float(len(clips))

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for idx, raw_mp4 in enumerate(clips, 1):
        rendered_mp4 = out_folder / f"clip_{idx}.mp4"
        is_first = (idx == 1)
        render_short_clip(raw_mp4, rendered_mp4, clip_dur, hook_text, sub_text, is_first)

        vc = VideoFileClip(str(rendered_mp4)).with_start(current_time).with_duration(clip_dur)
        video_clips.append(vc)
        current_time += clip_dur

    a_voice = v_voice.with_start(0.0).with_volume_scaled(1.6)
    audio_clips.append(a_voice)

    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        nature_bgm = raw_bgm.subclipped(0, min(total_short_dur, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(nature_bgm)

    master_path = out_folder / f"{short_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(out_folder / "temp_audio.m4a")

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

    print(f"🎉 SHORT CONCLUÍDO (ÁUDIO E VÍDEO 100% SINCRONIZADOS): {master_path} ({total_short_dur:.1f}s)")
    return master_path

def main():
    print("=== AJUSTANDO 3 SHORTS COM ÁUDIO E VÍDEO 100% SINCRONIZADOS ===")
    results = []
    for spec in SHORTS_SPECS:
        res = build_single_10s_short(spec)
        results.append(res)
    print("\n🎉 TODOS OS 3 SHORTS FORAM RE-RENDERIZADOS COM SUCESSO!")

if __name__ == "__main__":
    main()
