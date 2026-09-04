import os
import sys
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

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


class ModularPromptDirector:
    """
    Diretor de Prompts Modulares Cinematográficos.
    Combina Subject, Environment, Camera, Lens, Movement, Lighting, Atmosphere,
    Cinematic References, Quality Block e Negative Prompt de forma totalmente modular!
    """

    QUALITY_BLOCK = (
        "photorealistic, hyper realistic, physically accurate lighting, "
        "ray traced global illumination, volumetric fog, HDR, 8K RAW, "
        "cinematic composition, realistic skin, natural motion blur, "
        "depth of field, film grain 35mm, high dynamic range, professional color grading, ultra detailed"
    )

    CINEMATIC_REFS = "Inspired by Denis Villeneuve cinematography, Roger Deakins lighting, National Geographic documentary realism, BBC Earth composition, ARRI Alexa 65, IMAX documentary, Kodak Vision3 film stock"

    @classmethod
    def build_scene_prompt(cls, subject: str, environment: str, camera: str, lens: str, movement: str, lighting: str, atmosphere: str, hist_context: str) -> str:
        components = [
            f"Subject: {subject}",
            f"Environment: {environment}",
            f"Historical Context: {hist_context}",
            f"Camera: {camera}",
            f"Lens: {lens}",
            f"Movement: {movement}",
            f"Lighting: {lighting}",
            f"Atmosphere: {atmosphere}",
            f"Cinematic References: {cls.CINEMATIC_REFS}",
            f"Quality: {cls.QUALITY_BLOCK}"
        ]
        return ", ".join(components)


def fetch_modular_ai_image(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera a imagem de IA utilizando o motor de prompts modulares ultra-realista 8K."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={250000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=18) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ [DIRETOR CINEMATOGRÁFICO] Imagem 8K Gerada: {out_path.name}")
                return True
    except Exception:
        pass
    return False


def format_ai_image_to_916_hd(raw_img_path: Path, out_path: Path):
    """Formata imagem de IA para 9:16 HD 1080x1920 com tratamento de cor Kodak Vision3."""
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
        
        # Color grading Kodak Vision3 & Contraste ARRI Alexa
        img = ImageEnhance.Contrast(img).enhance(1.22)
        img = ImageEnhance.Color(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.20)
        img.save(out_path, format="PNG")
    except Exception:
        pass


def render_cinematic_modular_scene_clip(img_path: Path, scene_id: int, narration_text: str, duration: float, movement_type: str, out_mp4_path: Path):
    """
    Renderiza o clipe MP4 com movimento de câmera específico (Drone Reveal, Dolly Forward, Push-in, Handheld, Orbit, Zoom Out),
    legendas dinâmicas amarelas/brancas e moldura de cinema dourada.
    """
    img_pil = Image.open(img_path).convert("RGB")
    img_np = np.array(img_pil)

    w, h = 1080, 1920
    fps = 24
    total_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
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

        # Seleção Específica de Movimento de Câmera Cinematográfico
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

        # Banner de Título apenas no primeiro frame
        if scene_id == 1:
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 240), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 290), "O MASSACRE DO CALDEIRÃO", fill=(255, 215, 0), font=font_title, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), "O CIDADE APAGADA DO CEARÁ", fill=(255, 255, 255), font=font_subhead, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Legenda Dinâmica Amarela e Branca
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # Moldura Dourada
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [MOVIMENTO: {movement_type.upper()}] Cena {scene_id} renderizada em 24 FPS ({duration:.1f}s)")


# DIREÇÃO CINEMATOGRÁFICA MODULAR COMPLETA DAS 6 CENAS
CINEMATIC_BLUEPRINT_SCENES = [
    # CENA 1 — O SERTÃO (Drone Reveal)
    {
        "scene_id": 1,
        "movement_type": "drone_reveal",
        "narration": "Poucos sabem, mas anos após o massacre de Canudos, o governo usou aviões de guerra para apagar do mapa uma cidade inteira de fiéis no sertão!",
        "duration": 8.5,
        "prompt": (
            "Ultra-realistic cinematic aerial drone shot over the Brazilian sertão during golden sunrise, "
            "endless dry landscape with cracked earth, dramatic morning mist floating through valleys, "
            "warm volumetric sunlight piercing dusty air, hyper-detailed vegetation adapted to semi-arid climate, "
            "realistic heat haze, subtle wind moving dry bushes, shot on ARRI Alexa 65, 35mm anamorphic lens, HDR, "
            "Kodak Vision3 color grading, National Geographic documentary quality, 8K RAW, cinematic masterpiece"
        ),
        "negative_prompt": "cartoon, anime, CGI, oversaturated colors, blurry, watermark, logo, low resolution, distorted terrain, duplicated vegetation"
    },
    # CENA 2 — O CALDEIRÃO / A COMUNIDADE (Dolly Forward)
    {
        "scene_id": 2,
        "movement_type": "dolly_forward",
        "narration": "Fugindo da miséria, o beato negro José Lourenço fundou o Caldeirão de Santa Cruz no Ceará, abençoado pelo próprio Padre Cícero!",
        "duration": 9.0,
        "prompt": (
            "Thriving rural community hidden inside the Brazilian sertão in the 1930s, lush green plantations "
            "contrasting against the surrounding dry landscape, handmade adobe houses, families harvesting crops, "
            "ox carts transporting food, children laughing and running between fields, soft dust illuminated by golden sunlight, "
            "cinematic slow drone descent, highly realistic faces, historical accuracy, Discovery Channel documentary, IMAX quality, HDR, 8K"
        ),
        "negative_prompt": "modern buildings, asphalt roads, electricity poles, plastic objects, modern clothing, cars, text, watermark"
    },
    # CENA 3 — JOSÉ LOURENÇO / O LÍDER (Slow Push-In)
    {
        "scene_id": 3,
        "movement_type": "slow_push_in",
        "narration": "Lá não havia dinheiro nem patrões: tudo era de todos! Em pleno sertão castigado pela seca, a comunidade produzia toneladas de comida e fartura.",
        "duration": 8.5,
        "prompt": (
            "Close-up portrait of José Lourenço, charismatic Afro-Brazilian religious leader from the 1930s, "
            "humble linen clothing, weathered face marked by years under the sun, calm but determined eyes, "
            "cinematic rim light illuminating his profile, shallow depth of field, slow push-in camera movement, "
            "subtle wind moving his clothes, realistic skin pores, historical realism, photographed with an ARRI Alexa Mini LF, 85mm cinematic lens, documentary style"
        ),
        "negative_prompt": "young face, smiling, modern haircut, modern clothes, artificial lighting, CGI look"
    },
    # CENA 4 — O ATAQUE MILITAR (Handheld Documentary)
    {
        "scene_id": 4,
        "movement_type": "handheld_documentary",
        "narration": "Aterrorizados ao verem seus trabalhadores fugindo para o Caldeirão, coronéis e a elite acusaram o povo de criar uma república comunista fanática!",
        "duration": 9.0,
        "prompt": (
            "Vintage Brazilian military biplanes flying low above the dry Brazilian sertão in 1937, "
            "enormous dust clouds rising from the ground, frightened civilians running through fields, "
            "dramatic cinematic composition, realistic smoke interacting with sunlight, handheld documentary camera with subtle shake, "
            "volumetric lighting, authentic historical uniforms, emotional atmosphere, epic historical reconstruction, 24 fps, HDR, Dolby Vision, 8K"
        ),
        "negative_prompt": "explosions from Hollywood, futuristic aircraft, missiles, helicopters, science fiction, cartoon, video game"
    },
    # CENA 5 — AS RUÍNAS E AS VALAS COMUNS (Drone Orbit)
    {
        "scene_id": 5,
        "movement_type": "drone_orbit",
        "narration": "Em maio de 1937, biplanos militares despejaram bombas sobre homens, mulheres e crianças inocentes, sepultando a utopia em valas comuns!",
        "duration": 9.5,
        "prompt": (
            "Ancient abandoned ruins of Caldeirão de Santa Cruz do Deserto at sunset, collapsed stone walls covered by dry vegetation, "
            "lonely atmosphere, wooden crosses on a misty hill, cinematic drone orbit, long shadows stretching across the landscape, "
            "realistic dust particles illuminated by orange sunlight, subtle birds flying in the distance, National Geographic documentary, 8K RAW, ultra realistic textures, HDR"
        ),
        "negative_prompt": "tourists, modern houses, electric poles, graffiti, bright colors, fantasy"
    },
    # CENA 6 — O MEMORIAL E CONCLUSÃO (Slow Zoom Out)
    {
        "scene_id": 6,
        "movement_type": "slow_zoom_out",
        "narration": "A história tentou silenciar o Caldeirão, mas a memória do sertão jamais será apagada. Conhecia esse mistério? Comente e siga para mais segredos!",
        "duration": 8.0,
        "prompt": (
            "Golden sunset over Chapada do Araripe mountains Ceara Brazil, wooden cross memorial monument standing on cliff "
            "overlooking vast sertao landscape, dramatic golden rays, Roger Deakins lighting, ARRI Alexa 65, IMAX documentary, "
            "Kodak Vision3 film stock, 8K RAW, ultra realistic"
        ),
        "negative_prompt": "modern buildings, cars, city, text, watermark, low quality"
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


def produce_master_cinematic_caldeirao():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-RENDER COM TEMPLATE CINEMATOGRÁFICO V2] C:\\...\\output\\videos\\misterio_caldeirao_do_deserto")
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

    for sc in CINEMATIC_BLUEPRINT_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]
        movement_type = sc["movement_type"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        formatted_img_path = images_dir / f"scene_{scene_id}.png"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Gerar Imagem por IA utilizando o Prompt V2 e Template Cinematográfico Modular
        fetch_modular_ai_image(prompt_txt, scene_id, raw_img_path)
        format_ai_image_to_916_hd(raw_img_path, formatted_img_path)

        # 2. Renderizar Clipe 24 FPS com o Movimento Específico de Câmera
        render_cinematic_modular_scene_clip(formatted_img_path, scene_id, narration, dur, movement_type, scene_mp4)

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
        print(f"    [SCENE TEMPLATE V2 OK] Cena {scene_id}/6 concluída ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

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

    temp_audio_file = str(output_dir / "temp_audio_cinematic_blueprint.m4a")

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

    print(f"\n  🎉 [SUCESSO DEFINITIVO TEMPLATE CINEMATOGRÁFICO V2] VÍDEO COMPLETO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_master_cinematic_caldeirao()


if __name__ == "__main__":
    main()
