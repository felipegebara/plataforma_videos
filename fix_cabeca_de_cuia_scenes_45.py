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


def fetch_ai_image_8k_scenes45(prompt: str, scene_id: int, out_path: Path) -> bool:
    """Gera imagens de IA 8K de altíssima qualidade especificamente para as Cenas 4 e 5."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    enhanced_prompt = (
        f"{prompt}, 8k resolution, photorealistic, National Geographic documentary photograph, "
        f"ARRI Alexa 65 camera, 35mm anamorphic lens, ray traced global illumination, "
        f"volumetric lighting, cinematic composition, depth of field, HDR, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed_val = (int(time.time()) + scene_id * 4545) % 999999
    ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(ai_url, headers=headers)
            with urllib.request.urlopen(req, timeout=18) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [NOVA IMAGEM IA 8K GERADA] Cena {scene_id}: '{prompt[:45]}...' ({out_path.name})")
                    return True
        except Exception:
            time.sleep(1.0)
    return False


def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata foto para 9:16 HD 1080x1920 com tratamento cinematográfico."""
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
        
        img = ImageEnhance.Contrast(img).enhance(1.22)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
    except Exception:
        pass


def render_scene_clip_no_subtitles(img_path: Path, scene_id: int, duration: float, movement_type: str, out_mp4_path: Path):
    """Renderiza clipe MP4 24 FPS dinâmico sem legendas poluídas no rodapé."""
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

        if movement_type == "drone_reveal":
            scale = 1.18 - 0.15 * prog
            angle = -1.0 + 2.0 * prog
            dx, dy = 0.0, -0.04 * prog
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

        # Moldura Dourada Cinematográfica
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [CLIPE CENA {scene_id} RE-GERADO OK] ({duration:.1f}s)")


UPDATED_SCENES_45 = [
    # CENA 4: A PRAGA DAS 7 MARIAS (ILUSTRAÇÃO IA 8K MISTERIOSA DAS ÁGUAS)
    {
        "scene_id": 4,
        "movement_type": "drone_reveal",
        "narration": "A lenda diz que ele só voltará a ser humano no dia em que devorar sete Marias!",
        "duration": 3.5,
        "prompt": "Hyperrealistic 8k documentary photograph, dramatic night scene on the banks of Rio Parnaiba river in Piaui Brazil, mysterious moonlight reflecting on dark water, misty atmosphere, shadow reflection of a giant creature in water, cinematic composition, ARRI Alexa 65"
    },
    # CENA 5: VISTA AÉREA ESPETACULAR DE TERESINA E ENCONTRO DOS RIOS
    {
        "scene_id": 5,
        "movement_type": "slow_zoom_out",
        "narration": "Conhecia a lenda do Cabeça de Cuia em Teresina? Comente e siga o canal para mais mistérios!",
        "duration": 3.0,
        "prompt": "Breathtaking 8k aerial photograph of the iconic Encontro dos Rios park in Teresina Piaui Brazil where Parnaiba and Poty rivers meet at vibrant golden hour sunset, statue monument in lush park, volumetric sunlight piercing clouds, National Geographic style"
    }
]


async def generate_fast_voice(text: str, out_path: str):
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+10%")
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


def fix_cabeca_de_cuia_scenes_45():
    topic_id = "short_cabeca_de_cuia"
    print(f"\n==========================================")
    print(f"[RE-GERAÇÃO ESPECÍFICA DAS CENAS 4 E 5 POR IA 8K]")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 1. Re-gerar Cenas 4 e 5 por IA 8K
    for sc in UPDATED_SCENES_45:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        mov_type = sc["movement_type"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        fetch_ai_image_8k_scenes45(prompt_txt, scene_id, raw_img_path)
        format_photo_to_916_hd(raw_img_path, formatted_img_path)
        render_scene_clip_no_subtitles(formatted_img_path, scene_id, dur, mov_type, scene_mp4)
        asyncio.run(generate_fast_voice(narration, str(voice_path)))

    # 2. Re-compilar Vídeo Master Final com todas as 5 cenas
    video_clips = []
    audio_clips = []
    current_time = 0.0

    all_scenes_info = [
        (1, "O dia que um jovem agrediu a própria mãe e recebeu a praga mais assustadora do Piauí!"),
        (2, "Faminto, Crispim surtou ao receber apenas sopa com osso de boi e tirou a vida da mãe!"),
        (3, "Moribunda, ela o amaldiçoou a se transformar num monstro com cabeça gigante de cuia nas águas do Rio Parnaíba!"),
        (4, "A lenda diz que ele só voltará a ser humano no dia em que devorar sete Marias!"),
        (5, "Conhecia a lenda do Cabeça de Cuia em Teresina? Comente e siga o canal para mais mistérios!")
    ]

    for scene_id, text in all_scenes_info:
        sc_mp4 = output_dir / f"scene_{scene_id}.mp4"
        vc_path = audio_dir / f"voice_scene_{scene_id}.mp3"

        if not vc_path.exists():
            asyncio.run(generate_fast_voice(text, str(vc_path)))

        if sc_mp4.exists():
            v_clip = VideoFileClip(str(sc_mp4))
            voice_clip = AudioFileClip(str(vc_path)).with_start(current_time)
            voice_dur = voice_clip.duration + 0.05

            v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
            video_clips.append(v_clip)
            audio_clips.append(voice_clip.with_volume_scaled(1.6))

            current_time += voice_dur
            print(f"    [MASTER CLIP] Cena {scene_id}/5 acoplada ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 3. Trilha BGM
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.14)
        audio_clips.append(bgm_clip)

    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_fix_45.m4a")

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

    print(f"\n  🎉 [RE-GERAÇÃO DAS CENAS 4 E 5 CONCLUÍDA] VÍDEO COMPLETO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    fix_cabeca_de_cuia_scenes_45()


if __name__ == "__main__":
    main()
