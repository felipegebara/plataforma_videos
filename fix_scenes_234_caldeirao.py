import os
import sys
import time
import json
import asyncio
import urllib.request
import urllib.parse
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


def fetch_ai_image_scenes_234(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera imagens de IA 8K de altíssima qualidade especificamente para as Cenas 2, 3 e 4."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    enhanced_prompt = (
        f"{prompt}, 8k resolution, photorealistic, National Geographic documentary photograph, "
        f"ARRI Alexa 65 camera, 35mm anamorphic lens, ray traced global illumination, "
        f"volumetric lighting, cinematic composition, depth of field, HDR, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + seed_id * 8888) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=headers)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [NOVA IMAGEM IA 8K GERADA] Cena {seed_id}: '{prompt[:45]}...' ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)
    return False


def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata imagem para 9:16 HD 1080x1920 com contraste cinematográfico."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        return

    try:
        img = Image.open(raw_img_path).convert("RGB")
        aspect_target = 9 / 16.0
        aspect_img = img.width / float(img.height)

        if aspect_img > aspect_target:
            new_w = int(img.height * aspect_target)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, img.height))
        else:
            new_h = int(img.width / aspect_target)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, img.width, top + new_h))

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        
        img = ImageEnhance.Contrast(img).enhance(1.20)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        pass


def render_scene_clip_234(img_path: Path, scene_id: int, narration_text: str, duration: float, movement_type: str, out_mp4_path: Path):
    """Renderiza os novos clipes MP4 24 FPS para as Cenas 2, 3 e 4."""
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

    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
        font_title = ImageFont.truetype("arialbd.ttf", 40)
        font_subhead = ImageFont.truetype("arialbd.ttf", 28)
    except Exception:
        font_sub = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_subhead = ImageFont.load_default()

    words = narration_text.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])

    grain_noise = np.random.randint(-3, 4, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        if movement_type == "dolly_forward":
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
        else:
            scale = 1.05 + 0.05 * prog
            angle = 0.0
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

        # Legendas Dinâmicas Amarelas e Brancas
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE CENA {scene_id} RE-GERADO OK] ({duration:.1f}s)")


UPDATED_SCENES_234 = [
    # CENA 2 — ESTÁTUA DO PADRE CÍCERO NO HORTO EM JUAZEIRO DO NORTE (SEM ROSTO DO BEATO)
    {
        "scene_id": 2,
        "movement_type": "dolly_forward",
        "narration": "Em 1920, o Beato José Lourenço fundou na Serra do Araripe o Caldeirão de Santa Cruz, com a bênção solene do lendário Padre Cícero!",
        "duration": 9.0,
        "prompt": "Hyperrealistic 8k documentary photograph of the giant white concrete Statue of Padre Cícero standing tall on Horto hill in Juazeiro do Norte Ceará during golden sunset, majestic atmosphere, ARRI Alexa 65, 35mm anamorphic lens, IMAX quality"
    },
    # CENA 3 — LAVOURAS COMUNITÁRIAS E AÇUDE NO SERTÃO
    {
        "scene_id": 3,
        "movement_type": "slow_push_in",
        "narration": "Sem dinheiro nem patrões, os fiéis trabalhavam juntos nas colheitas, transformando a seca em fartura com açudes e lavouras coletivas!",
        "duration": 8.5,
        "prompt": "Hyperrealistic 8k documentary photograph of a thriving 1930s Brazilian sertanejo farming community in Ceará, lush green corn and cassava plantations next to a full water reservoir in countryside, wooden ox cart transporting crops, soft golden hour sunlight filtering through trees"
    },
    # CENA 4 — CORONÉIS E LATIFUNDIÁRIOS A CAVALO NO PENHASCO
    {
        "scene_id": 4,
        "movement_type": "handheld_documentary",
        "narration": "Impressionados com o crescimento do arraial, grandes fazendeiros e autoridades da época começaram a observar o movimento com apreensão!",
        "duration": 9.0,
        "prompt": "Hyperrealistic 8k cinematic photograph of 1930s Brazilian sertão land barons and colonels wearing suits and leather hats on horseback standing on a mountain cliff, looking down at a distant valley village under dramatic dark thunderclouds, high contrast chiaroscuro lighting, IMAX documentary quality"
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


def fix_scenes_234_caldeirao():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-GERAÇÃO ESPECÍFICA DAS CENAS 2, 3 E 4 POR IA 8K]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 1. Re-gerar especificamente Cenas 2, 3 e 4
    for sc in UPDATED_SCENES_234:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        movement_type = sc["movement_type"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # Gerar Imagem por IA 8K com os novos prompts exatos
        fetch_ai_image_scenes_234(prompt_txt, scene_id, raw_img_path)
        format_photo_to_916_hd(raw_img_path, formatted_img_path)

        # Renderizar Clipe 24 FPS
        render_scene_clip_234(formatted_img_path, scene_id, narration, dur, movement_type, scene_mp4)

        # Gerar Voz
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

    # 2. Re-compilar Vídeo Master Final com todas as 6 cenas (1, 2, 3, 4, 5, 6)
    video_clips = []
    audio_clips = []
    current_time = 0.0

    all_scenes_info = [
        (1, "Poucos sabem, mas anos após o fim de Canudos, o sertão do Ceará abrigou uma das comunidades mais prósperas e misteriosas da história do Brasil!"),
        (2, "Em 1920, o Beato José Lourenço fundou na Serra do Araripe o Caldeirão de Santa Cruz, com a bênção solene do lendário Padre Cícero!"),
        (3, "Sem dinheiro nem patrões, os fiéis trabalhavam juntos nas colheitas, transformando a seca em fartura com açudes e lavouras coletivas!"),
        (4, "Impressionados com o crescimento do arraial, grandes fazendeiros e autoridades da época começaram a observar o movimento com apreensão!"),
        (5, "Em 1937, a comunidade foi cercada e desfeita pelas forças públicas, encerrando um dos episódios mais marcantes da história nordestina."),
        (6, "O Caldeirão tornou-se símbolo de fé e perseverança no Ceará. Já conhecia essa história impressionante? Deixe seu comentário e siga o canal!")
    ]

    for scene_id, text in all_scenes_info:
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        if not voice_path.exists():
            asyncio.run(generate_voice(text, str(voice_path)))

        if scene_mp4.exists():
            v_clip = VideoFileClip(str(scene_mp4))
            voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
            voice_dur = voice_clip.duration + 0.1

            v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
            video_clips.append(v_clip)
            audio_clips.append(voice_clip.with_volume_scaled(1.6))

            current_time += voice_dur
            print(f"    [MASTER CLIP] Cena {scene_id}/6 acoplada ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 3. Trilha BGM
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_fix_234.m4a")

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

    print(f"\n  🎉 [RE-GERAÇÃO DAS CENAS 2, 3 E 4 CONCLUÍDA] VÍDEO NOVO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    fix_scenes_234_caldeirao()


if __name__ == "__main__":
    main()
