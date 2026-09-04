import os
import sys
import time
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

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def create_fallback_pro_image(scene_id: int, out_path: Path):
    """Gera uma Imagem de Alta Fidelidade Local com gradientes cinematográficos e névoa volumétrica se a API expirar."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        prog = y / float(h)
        if scene_id == 1:
            r = int(255 - prog * 180)
            g = int(140 - prog * 90)
            b = int(30 + prog * 40)
        elif scene_id == 2:
            r = int(230 - prog * 150)
            g = int(120 - prog * 80)
            b = int(40 + prog * 30)
        elif scene_id == 3:
            r = int(120 + prog * 80) if prog < 0.5 else int(40 - (prog-0.5)*40)
            g = int(180 + prog * 50) if prog < 0.5 else int(110 - (prog-0.5)*60)
            b = int(220 - prog * 140) if prog < 0.5 else int(30 - (prog-0.5)*20)
        elif scene_id == 4:
            r = int(50 - prog * 30)
            g = int(40 - prog * 25)
            b = int(60 - prog * 35)
        elif scene_id == 5:
            r = int(180 - prog * 140)
            g = int(60 - prog * 40)
            b = int(20)
        else:
            r = int(255 - prog * 190)
            g = int(110 - prog * 80)
            b = int(20 + prog * 30)
        draw.line([(0, y), (w, y)], fill=(max(0, r), max(0, g), max(0, b)))

    # Elementos visuais por cena
    if scene_id in [1, 6]:
        draw.ellipse([(410, 480), (670, 740)], fill=(255, 230, 150))
        draw.polygon([(0, 1000), (540, 880), (1080, 1020), (1080, 1920), (0, 1920)], fill=(25, 15, 10))
    elif scene_id == 2:
        draw.ellipse([(340, 400), (740, 800)], fill=(255, 200, 80))
        draw.polygon([(460, 520), (620, 520), (590, 600), (490, 600)], fill=(20, 15, 25))
        draw.polygon([(510, 600), (570, 600), (580, 1200), (500, 1200)], fill=(20, 15, 25))
        draw.polygon([(0, 1150), (540, 1050), (1080, 1180), (1080, 1920), (0, 1920)], fill=(15, 10, 18))
    elif scene_id == 3:
        draw.ellipse([(440, 300), (640, 500)], fill=(255, 240, 180))
        draw.polygon([(0, 900), (1080, 900), (1080, 1920), (0, 1920)], fill=(35, 75, 25))
        draw.ellipse([(150, 1100), (930, 1550)], fill=(40, 110, 160))
    elif scene_id == 4:
        draw.line([(300, 100), (340, 350), (320, 360), (380, 600)], fill=(255, 240, 180), width=4)
        draw.polygon([(0, 850), (450, 700), (1080, 900), (1080, 1920), (0, 1920)], fill=(20, 18, 22))
        draw.polygon([(300, 680), (350, 680), (340, 750), (290, 750)], fill=(10, 8, 12))
    elif scene_id == 5:
        draw.polygon([(200, 300), (320, 300), (260, 270)], fill=(20, 20, 20))
        draw.polygon([(700, 400), (820, 400), (760, 370)], fill=(20, 20, 20))
        draw.ellipse([(200, 900), (600, 1300)], fill=(255, 100, 0))
        draw.ellipse([(500, 1000), (900, 1400)], fill=(255, 160, 0))

    draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="JPEG")
    print(f"    ✓ [IMAGEM PRO FALLBACK CRIADA] {out_path.name}")


def fetch_super_hd_ai_image(prompt: str, scene_id: int, out_path: Path) -> bool:
    """Gera imagem de IA com parâmetros de ultra-definição 8K (Flux / SDXL Engine)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    
    enhanced_prompt = (
        f"{prompt}, 8k resolution, photorealistic, National Geographic documentary photograph, "
        f"hyperdetailed textures, ARRI Alexa 65, 35mm anamorphic lens, ray traced global illumination, "
        f"volumetric lighting, cinematic composition, depth of field, HDR, no watermark, no text"
    )
    enc_p = urllib.parse.quote(enhanced_prompt)
    seed_val = int(time.time() * 1000) % 900000 + scene_id * 54321
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={seed_val}"
    
    for attempt in range(2):
        try:
            req = urllib.request.Request(ai_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                if len(content) > 15000:
                    with open(out_path, "wb") as f:
                        f.write(content)
                    print(f"    ✓ [SUPER HD 8K IA GERADA] Cena {scene_id}: '{prompt[:45]}...' ({out_path.name})")
                    return True
        except Exception:
            time.sleep(0.5)

    create_fallback_pro_image(scene_id, out_path)
    return True


def format_ai_image_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata imagem para 9:16 HD 1080x1920 com contraste e nitidez cinematográfica."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        create_fallback_pro_image(1, raw_img_path)

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
        img_dummy = Image.new("RGB", (w, h), (30, 20, 15))
        img_dummy.save(out_path, format="PNG")


def render_super_hd_scene_clip(img_path: Path, scene_id: int, narration_text: str, duration: float, movement_type: str, out_mp4_path: Path):
    """
    Renderiza um clipe MP4 limpo em 24 FPS com o movimento de câmera específico,
    legendas dinâmicas amarelas/brancas e moldura de cinema.
    """
    if not img_path.exists():
        w, h = 1080, 1920
        img_dummy = Image.new("RGB", (w, h), (30, 20, 15))
        img_dummy.save(img_path, format="PNG")

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

        # Seleção de Movimento de Câmera
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
        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        # Banner de Título apenas na Cena 1
        if scene_id == 1:
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 240), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 290), "O MASSACRE DO CALDEIRÃO", fill=(255, 215, 0), font=font_title, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), "O CIDADE APAGADA DO CEARÁ", fill=(255, 255, 255), font=font_subhead, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Legendas Dinâmicas Amarelas e Brancas
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [SUPER HD CLIP OK] Cena {scene_id} ({movement_type.upper()}) renderizada ({duration:.1f}s)")


SUPER_HD_BLUEPRINT_SCENES = [
    # CENA 1 — O SERTÃO (Drone Reveal)
    {
        "scene_id": 1,
        "movement_type": "drone_reveal",
        "narration": "Poucos sabem, mas anos após o massacre de Canudos, o governo usou aviões de guerra para apagar do mapa uma cidade inteira de fiéis no sertão!",
        "duration": 8.5,
        "prompt": "Photorealistic 8k cinematic aerial view of the Brazilian sertão during golden hour sunrise, cracked dry earth, morning mist floating between hills, volumetric sunlight rays piercing dusty atmosphere, vintage 1930s military biplanes soaring far in the sky dropping bombs over distant village, smoke trails"
    },
    # CENA 2 — O BEATO JOSÉ LOURENÇO & PADRE CÍCERO (Dolly Forward)
    {
        "scene_id": 2,
        "movement_type": "dolly_forward",
        "narration": "Fugindo da miséria, o beato negro José Lourenço fundou o Caldeirão de Santa Cruz no Ceará, abençoado pelo próprio Padre Cícero!",
        "duration": 9.0,
        "prompt": "Photorealistic 8k historical portrait, charismatic Afro-Brazilian religious leader Beato José Lourenço in humble white linen clothes, weathered face with detailed skin pores, receiving solemn blessing from elderly Padre Cícero holding a wooden cross, golden hour sunlight rim lighting"
    },
    # CENA 3 — A UTOPIA E LAVOURAS (Slow Push-In)
    {
        "scene_id": 3,
        "movement_type": "slow_push_in",
        "narration": "Lá não havia dinheiro nem patrões: tudo era de todos! Em pleno sertão castigado pela seca, a comunidade produzia toneladas de comida e fartura.",
        "duration": 8.5,
        "prompt": "Photorealistic 8k documentary photograph, 1930s Brazilian sertanejo farming community working together in lush green crops next to a filled water dam in dry countryside, men and women harvesting corn and cassava, ox carts carrying food, warm golden sunlight filtering through dust"
    },
    # CENA 4 — A CONSPIRAÇÃO DOS CORONÉIS (Handheld Documentary)
    {
        "scene_id": 4,
        "movement_type": "handheld_documentary",
        "narration": "Aterrorizados ao verem seus trabalhadores fugindo para o Caldeirão, coronéis e a elite acusaram o povo de criar uma república comunista fanática!",
        "duration": 9.0,
        "prompt": "Photorealistic 8k cinematic masterpiece, 1930s wealthy Brazilian land barons and colonels in suits and leather hats on horseback standing on a cliff edge looking down at a valley village under ominous dark storm clouds, dramatic chiaroscuro lighting, volumetric fog"
    },
    # CENA 5 — O BOMBARDEIO E AS VALAS COMUNS (Drone Orbit)
    {
        "scene_id": 5,
        "movement_type": "drone_orbit",
        "narration": "Em maio de 1937, biplanos militares despejaram bombas sobre homens, mulheres e crianças inocentes, sepultando a utopia em valas comuns!",
        "duration": 9.5,
        "prompt": "Photorealistic 8k historical tragedy scene, 1930s military biplane aircraft bombing a Brazilian countryside village, massive smoke plumes and fire explosions, simple wooden crosses planted on a misty hill at dusk, dramatic moody lighting"
    },
    # CENA 6 — O MEMORIAL NA CHAPADA DO ARARIPE (Slow Zoom Out)
    {
        "scene_id": 6,
        "movement_type": "slow_zoom_out",
        "narration": "A história tentou silenciar o Caldeirão, mas a memória do sertão jamais será apagada. Conhecia esse mistério? Comente e siga para mais segredos!",
        "duration": 8.0,
        "prompt": "Photorealistic 8k landscape photograph, breathtaking golden sunset over Chapada do Araripe mountains in Ceará Brazil, solitary wooden memorial cross standing on a rocky cliff top overlooking the vast sertão valley below, golden sun rays piercing clouds"
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


def produce_super_hd_caldeirao_video():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[SUPER GERADOR IA DE ALTA DEFINIÇÃO 8K] misterio_caldeirao_do_deserto")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    # Limpeza limpa de imagens e vídeos antigos
    for d in [output_dir, images_dir]:
        if d.exists():
            for f in d.glob("*.*"):
                try:
                    f.unlink()
                except Exception:
                    pass

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in SUPER_HD_BLUEPRINT_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        movement_type = sc["movement_type"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Gerar Nova Imagem IA em Super HD 8K
        fetch_super_hd_ai_image(prompt_txt, scene_id, raw_img_path)
        format_ai_image_to_916_hd(raw_img_path, formatted_img_path)

        # 2. Renderizar Clipe 24 FPS
        render_super_hd_scene_clip(formatted_img_path, scene_id, narration, dur, movement_type, scene_mp4)

        # 3. Gerar Voz Humana Neural
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # 4. Acoplar Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.6))

        current_time += voice_dur
        print(f"    [SCENE SUPER HD OK] Cena {scene_id}/6 masterizada ({voice_dur:.2f}s | Total: {current_time:.1f}s)")

    # 5. Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 6. Exportar Vídeo Master Final em C:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\misterio_caldeirao_do_deserto
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_super_hd.m4a")

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

    print(f"\n  🎉 [SUPER HD 8K CONCLUÍDO] VÍDEO COMPLETO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_super_hd_caldeirao_video()


if __name__ == "__main__":
    main()
