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

from video_ai_engine import video_ai_engine

# Reconfiguração segura de encoding para UTF-8 no Windows Console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))


def fetch_ultra_hd_ai_image(prompt: str, seed_id: int, out_path: Path) -> bool:
    """Gera ilustração cinematográfica hyper-detalhada em 8K por IA via Pollinations Engine."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={95000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=16) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    ✓ Imagem por IA 8K Gerada com Sucesso: '{prompt[:45]}...'")
                return True
    except Exception:
        pass
    return False


def create_epic_custom_canvas(scene_id: int, out_path: Path):
    """Cria uma tela procedural de alta definição caso a API de IA sofra timeout."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (35, 20, 15))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        r = int(65 - y/h * 45)
        g = int(35 - y/h * 25)
        b = int(20 - y/h * 15)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)
    img.save(out_path, format="PNG")


def render_clean_scene_clip(raw_img_path: Path, scene_id: int, narration_text: str, duration: float, out_mp4_path: Path):
    """
    Renderiza clipe de vídeo limpo SEM NOME DE MODELO nem NÚMERO DE CENA estampados na tela!
    Apenas vídeo em movimento 3D com legendas dinâmicas amarelas/brancas e moldura de cinema.
    """
    img_pil = Image.open(raw_img_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
    img_pil = ImageEnhance.Contrast(img_pil).enhance(1.25)
    img_pil = ImageEnhance.Color(img_pil).enhance(1.15)
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

    grain_noise = np.random.randint(-4, 5, (h, w, 3), dtype=np.int16)

    for f_idx in range(total_frames):
        prog = f_idx / float(total_frames)

        scale = 1.0 + 0.12 * np.sin(prog * np.pi * 0.5)
        angle = -1.2 + 2.4 * prog

        nw, nh = int(w * scale), int(h * scale)
        frame_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)

        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), angle, 1.0)
        frame_rot = cv2.warpAffine(frame_res, M, (nw, nh), flags=cv2.INTER_CUBIC)

        sx = int((nw - w) * (0.5 + 0.3 * np.cos(prog * np.pi)))
        sy = int((nh - h) * (0.5 + 0.3 * np.sin(prog * np.pi)))

        sx = max(0, min(sx, nw - w))
        sy = max(0, min(sy, nh - h))

        frame_cropped = frame_rot[sy : sy + h, sx : sx + w].copy()
        frame_grain = np.clip(frame_cropped.astype(np.int16) + grain_noise, 0, 255).astype(np.uint8)

        frame_pil = Image.fromarray(frame_grain)
        draw = ImageDraw.Draw(frame_pil)

        # 1. Estampar Banner de Título Limpo APENAS na Cena 1 (Sem Nome de Modelo!)
        if scene_id == 1:
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 210))
            draw.rectangle([(0, 240), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 290), "O CALDEIRÃO DE SANTA CRUZ", fill=(255, 215, 0), font=font_title, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), "O SEGUNDO CANUDOS DO SERTÃO", fill=(255, 255, 255), font=font_subhead, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # 2. Legendas Dinâmicas da Narração no Rodapé (Sem CENA 1/6 nem nome do modelo!)
        draw.rectangle([(60, h - 320), (w - 60, h - 140)], fill=(0, 0, 0, 210))
        draw.text((w // 2, h - 260), line1, fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((w // 2, h - 190), line2, fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

        # 3. Moldura Dourada Elegante
        draw.rectangle([(25, 25), (w - 25, h - 25)], outline=(255, 215, 0), width=6)

        frame_out = np.array(frame_pil)
        out_v.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

    out_v.release()
    print(f"    ✓ [SCENE CLEAN OK] Cena {scene_id} renderizada sem marcas d'água ({duration:.1f}s)")


CLEAN_CALDEIRAO_AI_SCENES = [
    {
        "scene_id": 1,
        "narration": "Você sabia que anos após a destruição de Canudos, o sertão do Ceará viveu outro império de fé e tragédia esquecido pela história?",
        "duration": 8.5,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 painting, Serra do Araripe mountains at golden sunrise in dry Ceara sertao Brazil, dramatic clouds, fine art"
    },
    {
        "scene_id": 2,
        "narration": "Na década de 1920, o Beato José Lourenço fundou na Serra do Araripe a comunidade do Caldeirão de Santa Cruz, sob benção do Padre Cícero.",
        "duration": 9.0,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 portrait, wise Afro-Brazilian religious leader Beato Jose Lourenco receiving blessing from Padre Cicero in Juazeiro do Norte"
    },
    {
        "scene_id": 3,
        "narration": "Milhares de sertanejos miseráveis migraram para lá, criando uma sociedade igualitária com lavouras prósperas no meio da seca.",
        "duration": 8.5,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 painting, poor 1930s Brazilian sertanejo farmers harvesting green crops together in prosperous community farm, dry Ceara sertao"
    },
    {
        "scene_id": 4,
        "narration": "Assustados com o poder daquela comunidade que lembrava o Arraial de Canudos, autoridades e fazendeiros acusaram o povo de fanatismo.",
        "duration": 9.0,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 masterpiece, wealthy 1930s Brazilian sertao land barons on horseback looking down at village under dark stormy sky"
    },
    {
        "scene_id": 5,
        "narration": "Em 1937, a Força Pública e aviões militares bombardearam o Caldeirão, destruindo o arraial e sepultando uma das maiores utopias do sertão.",
        "duration": 9.5,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 battle painting, 1930s military biplanes dropping bombs over burning Brazilian sertao village, smoke and fire explosion"
    },
    {
        "scene_id": 6,
        "narration": "Conhecia a impressionante história do Caldeirão do Ceará? Deixe seu comentário e siga o canal para mais histórias épicas!",
        "duration": 8.0,
        "prompt": "Hyper-realistic 8k cinematic vertical 9:16 landscape, golden sunset over Chapada do Araripe mountains Ceara Brazil, dramatic sky, fine art"
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


def produce_clean_caldeirao_video():
    topic_id = "misterio_caldeirao_do_deserto"
    print(f"\n==========================================")
    print(f"[RE-RENDER LIMPO POR IA] misterio_caldeirao_do_deserto (Sem Nomes de Modelos/Cenas)")
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

    for sc in CLEAN_CALDEIRAO_AI_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        prompt_txt = sc["prompt"]

        raw_img_path = images_dir / f"raw_scene_{scene_id}.jpg"
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"

        # 1. Gerar Imagem por IA em 8K
        img_ok = fetch_ultra_hd_ai_image(prompt_txt, scene_id, raw_img_path)
        if not img_ok or not raw_img_path.exists():
            create_epic_custom_canvas(scene_id, raw_img_path)

        # 2. Renderizar Clipe de Vídeo LIMPO (Sem texto de marca d'água/modelo)
        render_clean_scene_clip(raw_img_path, scene_id, narration, dur, scene_mp4)

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
        print(f"    [SCENE OK] Cena {scene_id}/6 gerada e limpa ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # 5. Adicionar Trilha BGM
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 6. Exportar Vídeo Master Limpo em C:\Users\fgeba\Documents\quizz\lendas e historia\output\videos\misterio_caldeirao_do_deserto
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    temp_audio_file = str(output_dir / "temp_audio_clean.m4a")

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

    print(f"\n  🎉 [SUCESSO] VÍDEO LIMPO GERADO POR IA CONCLUÍDO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_clean_caldeirao_video()


if __name__ == "__main__":
    main()
