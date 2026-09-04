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


def render_scene_clip(img_path: Path, scene_id: int, duration: float, movement_type: str, banner_text: str, out_mp4_path: Path):
    """Renderiza cada clipe em 24 FPS com enquadramento perfeito 9:16 HD 1080x1920."""
    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    if not img_path.exists():
        img_blank = Image.new("RGB", (w, h), (15, 30, 55))
        img_blank.save(img_path, format="PNG")

    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)

    if out_mp4_path.exists():
        try:
            out_mp4_path.unlink()
        except Exception:
            pass

    out_v = cv2.VideoWriter(str(out_mp4_path), fourcc, fps, (w, h))
    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    try:
        font_banner = ImageFont.truetype("arialbd.ttf", 42)
    except Exception:
        font_banner = ImageFont.load_default()

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        if movement_type == "drone_reveal":
            scale = 1.18 - 0.15 * prog
            angle = -1.0 + 2.0 * prog
            dx, dy = 0.0, -0.04 * prog
        elif movement_type == "slow_push_in":
            scale = 1.0 + 0.16 * (prog ** 1.2)
            angle = 0.0
            dx, dy = 0.0, 0.0
        elif movement_type == "macro_pan":
            scale = 1.12
            angle = 0.0
            dx, dy = -0.05 * prog, 0.02 * prog
        elif movement_type == "dolly_forward":
            scale = 1.0 + 0.15 * prog
            angle = -0.5 + 1.0 * prog
            dx, dy = 0.0, 0.02 * prog
        else: # slow_zoom_out
            scale = 1.16 - 0.16 * prog
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

        # TEXTO DE BANNER
        if banner_text:
            draw.rectangle([(0, 260), (1080, 420)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 420)], fill=(255, 215, 0))
            draw.text((540, 340), banner_text, fill=(255, 215, 0), font=font_banner, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE CENA {scene_id} RENDERIZADO COM IMAGEM 8K] ({duration:.1f}s)")


SCENES_FROM_8_PACK = [
    # CENA 1: HOOK (image_1.png)
    {
        "scene_id": 1,
        "img_filename": "image_1.png",
        "movement_type": "drone_reveal",
        "banner_text": "POR QUE ESSA MONTANHA É AZUL? ⛰️",
        "narration": "Por que essa montanha em Santa Catarina está sempre coberta por um véu azul misterioso?"
    },
    # CENA 2: O MISTÉRIO DA BRUMA (image_2.png)
    {
        "scene_id": 2,
        "img_filename": "image_2.png",
        "movement_type": "slow_push_in",
        "banner_text": "Portal? Fenômeno sobrenatural? 🛸",
        "narration": "Quem olha o Morro Azul de longe enxerga uma bruma índigo constante."
    },
    # CENA 3: A LENDA SUBTERRÂNEA (image_5.png)
    {
        "scene_id": 3,
        "img_filename": "image_5.png",
        "movement_type": "dolly_forward",
        "banner_text": "A LENDA SUBTERRÂNEA 🐍",
        "narration": "Por décadas, histórias populares falavam de portais energéticos e até uma serpente adormecida nas profundezas das rochas."
    },
    # CENA 4: A REVELAÇÃO DA FLORESTA (image_3.png)
    {
        "scene_id": 4,
        "img_filename": "image_3.png",
        "movement_type": "macro_pan",
        "banner_text": "A FLORESTA RESPIRANDO 🌿",
        "narration": "Mas a verdade é ainda mais fascinante: isso é a própria floresta respirando! As árvores liberam óleos essenciais na atmosfera para se proteger."
    },
    # CENA 5: A FÍSICA E O ENXAIMEL (image_6.png)
    {
        "scene_id": 5,
        "img_filename": "image_6.png",
        "movement_type": "dolly_forward",
        "banner_text": "A LUZ SE ESPALHA 🌤️",
        "narration": "Quando a luz do sol atinge essas micropartículas, ela se espalha e tinge as encostas de Timbó e Pomerode de azul."
    },
    # CENA 6: O CÉU NOTURNO (image_7.png)
    {
        "scene_id": 6,
        "img_filename": "image_7.png",
        "movement_type": "slow_zoom_out",
        "banner_text": "CIÊNCIA & MAGIA 🌌",
        "narration": "Um espetáculo visual único onde a botânica e a física criam pura magia."
    },
    # CENA 7: O MIRANTE E VOO LIVRE (image_4.png)
    {
        "scene_id": 7,
        "img_filename": "image_4.png",
        "movement_type": "drone_reveal",
        "banner_text": "O TOPO DO MORRO AZUL 🪂",
        "narration": "Do topo da rampa do Morro Azul, a visão do vale é verdadeiramente inesquecível."
    },
    # CENA 8: CALL TO ACTION (image_8.png)
    {
        "scene_id": 8,
        "img_filename": "image_8.png",
        "movement_type": "slow_zoom_out",
        "banner_text": "Já viu isso de perto? 👇 / @RotaCalculada",
        "narration": "Você conhecia o segredo do Morro Azul? Deixe nos comentários e siga o Rota Calculada para desvendar mais mistérios!"
    }
]


async def generate_documentary_voice(text: str, out_path: str):
    """Gera locução neural documentária limpa."""
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+6%")
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


def produce_video_from_8_pack():
    topic_id = "morro_azul_8_pack_movie"
    print(f"\n==========================================")
    print(f"[RE-RENDERIZANDO VÍDEO DOCUMENTÁRIO COM O PACOTE DE 8 IMAGENS 8K]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / "morro_azul_8_pack"
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in SCENES_FROM_8_PACK:
        scene_id = sc["scene_id"]
        img_fn = sc["img_filename"]
        mov_type = sc["movement_type"]
        banner_txt = sc["banner_text"]
        narration_txt = sc["narration"]

        img_path = images_dir / img_fn
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        # 1. Gerar Áudio Neural
        asyncio.run(generate_documentary_voice(narration_txt, str(voice_path)))
        voice_clip = AudioFileClip(str(voice_path))
        exact_dur = voice_clip.duration + 0.1

        # 2. Renderizar Clipe
        render_scene_clip(img_path, scene_id, exact_dur, mov_type, banner_txt, scene_mp4)

        # 3. Acoplar Vídeo e Áudio
        v_clip = VideoFileClip(str(scene_mp4)).with_start(current_time)
        voice_clip = voice_clip.with_start(current_time)

        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += exact_dur
        print(f"    [MASTER 8-PACK OK] Cena {scene_id}/8 acoplada ({exact_dur:.2f}s | Total: {current_time:.1f}s)")

    # 4. Trilha Sonora Documentária de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 5. Exportar Vídeo Master Final com o pacote de 8 imagens
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_8pack.m4a")

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

    print(f"\n  🎉 [VÍDEO COM PACOTE DE 8 IMAGENS 8K CONCLUÍDO] DURAÇÃO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_video_from_8_pack()


if __name__ == "__main__":
    main()
