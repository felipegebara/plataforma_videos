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
output_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\morro_azul_3min_documentary")
output_dir.mkdir(parents=True, exist_ok=True)

# List of all user uploaded raw WhatsApp videos
USER_VIDEOS = [
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.10.53.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.09.08.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 21.20.30.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 21.21.16.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.06.52.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.07.44.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.07.54.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.08.28.mp4",
    downloads_dir / "WhatsApp Video 2026-08-04 at 22.08.57.mp4",
]

# Rich 3-Minute Documentary Script
DOCUMENTARY_PARTS = [
    ("part1", "No coração de Santa Catarina, na divisa entre Timbó e Pomerode, ergue-se uma montanha que há séculos desafia a imaginação dos moradores e visitantes: o Morro Azul."),
    ("part2", "Com mais de 750 metros de altitude, quem avista essa impressionante formação da encosta enxerga uma característica fascinante e misteriosa: um véu de cor azul-anil profundo cobrindo toda a montanha."),
    ("part3", "Por gerações, narrativas populares e lendas de colonos atribuíam esse tom azulado a portais de energia espiritual, auras místicas e até mesmo a lenda da serpente gigante adormecida nas rochas subterrâneas."),
    ("part4", "Mas a explicação científica revelada pela biologia e pela física é ainda mais espetacular: o mistério do Morro Azul é a prova viva de que a floresta está respirando!"),
    ("part5", "As árvores nativas da Mata Atlântica liberam continuamente óleos essenciais e compostos orgânicos voláteis na atmosfera como mecanismo natural de proteção contra a seca e o calor."),
    ("part6", "Quando os raios de sol atingem essas micropartículas de óleo suspensas na neblina, ocorre o fenômeno físico conhecido como Dispersão de Rayleigh — o mesmo princípio que faz o próprio céu parecer azul."),
    ("part7", "A luz solar se espalha pelas partículas de vapor e óleos essenciais, tingindo toda a paisagem da serra com um manto azul denso e inconfundível."),
    ("part8", "Hoje, a rampa do Morro Azul em Timbó é ponto de encontro de pilotos de voo livre, campistas e amantes da natureza que vêm contemplar a fusão perfeita entre a botânica e a física."),
    ("part9", "Uma verdadeira obra-prima natural no Vale do Itajaí. E você, já conhecia o segredo científico por trás do Morro Azul? Deixe seu comentário e siga o canal Rota Calculada para mais segredos pelo Brasil!")
]

async def generate_narration():
    for name, text in DOCUMENTARY_PARTS:
        out_mp3 = output_dir / f"voice_{name}.mp3"
        communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+3%")
        await communicate.save(str(out_mp3))
        print(f"Generated narration {name}: {out_mp3}")

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

    # Color grading
    pil_img = ImageEnhance.Color(pil_img).enhance(1.15)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.10)
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.25)

    img_graded = np.array(pil_img)
    b, g, r = cv2.split(cv2.cvtColor(img_graded, cv2.COLOR_RGB2BGR))
    b = np.clip(b.astype(np.int16) + 5, 0, 255).astype(np.uint8)
    r = np.clip(r.astype(np.int16) - 2, 0, 255).astype(np.uint8)
    
    return cv2.merge([b, g, r])

def process_video_clip(input_mp4: Path, out_mp4: Path, target_dur: float, scene_id: int):
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

        # Hook overlay on scene 1
        if scene_id == 1 and frames_written < int(3.0 * fps):
            pil_frame = Image.fromarray(cv2.cvtColor(graded_bgr, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_frame)

            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), "O SEGREDO DO MORRO AZUL ⛰️", fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), "DOCUMENTÁRIO COMPLETO - TIMBÓ SC", fill=(255, 255, 255), font=font_hook, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            graded_bgr = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)

        # Golden cinematic border
        cv2.rectangle(graded_bgr, (25, 25), (w - 25, h - 25), (0, 215, 255), 6)

        out_writer.write(graded_bgr)
        frames_written += 1

    cap.release()
    out_writer.release()
    print(f"Processed scene {scene_id} ({target_dur:.2f}s)")

def main():
    print("=== PROCESSSANDO DOCUMENTÁRIO COMPLETO DE ~3 MINUTOS DO MORRO AZUL ===")
    asyncio.run(generate_narration())

    video_clips = []
    audio_clips = []
    current_time = 0.0

    # Sequence and match user's cell phone clips into 9 documentary chapters
    for idx, (part_name, text) in enumerate(DOCUMENTARY_PARTS, 1):
        voice_path = output_dir / f"voice_{part_name}.mp3"
        v_audio = AudioFileClip(str(voice_path))
        scene_dur = max(6.0, v_audio.duration + 0.3)

        # Pick user video clip in loop
        raw_v_path = USER_VIDEOS[(idx - 1) % len(USER_VIDEOS)]
        rendered_scene_mp4 = output_dir / f"rendered_scene_{idx}.mp4"

        process_video_clip(raw_v_path, rendered_scene_mp4, scene_dur, idx)

        v_clip = VideoFileClip(str(rendered_scene_mp4)).with_start(current_time).with_duration(scene_dur)
        a_clip = v_audio.with_start(current_time).with_volume_scaled(1.6)

        video_clips.append(v_clip)
        audio_clips.append(a_clip)

        current_time += scene_dur
        print(f"Acopladed Scene {idx}/9 ({scene_dur:.2f}s | Total: {current_time:.1f}s)")

    # Add background documentary ambient music
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / "morro_azul_3min_documentary_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio = str(output_dir / "temp_audio_doc.m4a")

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

    print(f"\n🎉 DOCUMENTÁRIO DE 3 MINUTOS CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")

if __name__ == "__main__":
    main()
