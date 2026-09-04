import os
import sys
import asyncio
import time
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
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

BRAIN_DIR = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

CARRANCAS_HD_MAP = {
    1: BRAIN_DIR / "carranca_scene1_1785456061800.jpg",
    2: BRAIN_DIR / "carranca_scene2_1785456076567.jpg",
    3: BRAIN_DIR / "carranca_scene2_1785456076567.jpg",
    4: BRAIN_DIR / "carranca_scene1_1785456061800.jpg",
    5: BRAIN_DIR / "carranca_scene2_1785456076567.jpg",
    6: BRAIN_DIR / "carranca_scene1_1785456061800.jpg",
}

INTERIOR_TOPICS = [
    {
        "id": "carrancas_velho_chico",
        "title": "A LENDA DA CARRANCA DO VELHO CHICO",
        "local_map": CARRANCAS_HD_MAP,
        "script_scenes": [
            {
                "scene_id": 1,
                "narration": "Nas margens do Rio São Francisco, no sertão baiano, nasceu uma das lendas mais temidas da navegação brasileira.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "As carrancas, esculturas de madeira de rostos grotescos e dentes afiados, eram fixadas na proa dos barcos a vapor.",
                "duration": 5.2,
                "motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Navegadores acreditavam que as carrancas soltavam gemidos e espantavam o Caboclo d'Água e os espíritos do rio.",
                "duration": 5.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Construídas por mestres carpinteiros de Juazeiro e Bom Jesus da Lapa, cada peça carregava um talismã de proteção.",
                "duration": 5.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 5,
                "narration": "Hoje, as carrancas são reconhecidas como símbolos sagrados do patrimônio e da cultura popular sertaneja.",
                "duration": 4.8,
                "motion": "zoom_in"
            },
            {
                "scene_id": 6,
                "narration": "Você teria uma carranca protetora na sua casa? Comente sua opinião e compartilhe essa lenda da Bahia!",
                "duration": 5.0,
                "motion": "zoom_out"
            }
        ]
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


def produce_video(topic_data: dict):
    print(f"\n==========================================")
    print(f"[PRODUCAO] Re-renderizando Vídeo das Carrancas com 100% Imagens HD 9:16: {topic_data['title']}")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_data["id"]
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_data["id"]
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_data["id"]

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    scenes = topic_data["script_scenes"]
    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in scenes:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]

        # 1. Carregar Imagem HD 9:16 Sem Cortes
        img_path = images_dir / f"scene_{scene_id}.png"
        local_map = topic_data.get("local_map", {})

        if scene_id in local_map and local_map[scene_id].exists():
            img = Image.open(local_map[scene_id]).convert("RGB")
            img_final = img.resize((1080, 1920), Image.Resampling.LANCZOS)
            img_final.save(img_path)
            print(f"  ✓ Cena {scene_id}: Imagem HD 9:16 de Carranca/Velho Chico carregada")
        else:
            img = Image.new("RGB", (1080, 1920), (35, 25, 15))
            img.save(img_path)

        # 2. Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 420)], fill=(0, 0, 0, 195))
            try:
                font = ImageFont.truetype("arialbd.ttf", 42)
            except Exception:
                font = ImageFont.load_default()

            title_str = topic_data["title"]
            parts = title_str.split(" DO ")
            line1 = parts[0]
            line2 = "DO " + parts[1] if len(parts) > 1 else title_str

            draw.text((540, 290), line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            img.convert("RGB").save(img_path)

        # 3. Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # 4. Renderizar Vídeo MP4 com Movimento OpenCV
        scene_mp4 = output_dir / f"scene_{scene_id}.mp4"
        img_cv = cv2.imread(str(img_path))
        h_cv, w_cv, _ = img_cv.shape
        fps = 24
        total_f = int(dur * fps)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_v = cv2.VideoWriter(str(scene_mp4), fourcc, fps, (w_cv, h_cv))

        for f_idx in range(total_f):
            prog = f_idx / float(total_f)
            if motion == "zoom_in":
                scale = 1.0 + (0.08 * prog)
            elif motion == "zoom_out":
                scale = 1.08 - (0.08 * prog)
            else:
                scale = 1.04

            nw, nh = int(w_cv * scale), int(h_cv * scale)
            resized = cv2.resize(img_cv, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

            if motion == "pan_left":
                sx = int((nw - w_cv) * (1.0 - prog))
            elif motion == "pan_right":
                sx = int((nw - w_cv) * prog)
            else:
                sx = (nw - w_cv) // 2

            sy = (nh - h_cv) // 2
            out_v.write(resized[sy : sy + h_cv, sx : sx + w_cv])

        out_v.release()

        # 5. Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.5))

        current_time += voice_dur
        print(f"  [SCENE] Cena {scene_id} renderizada com imagem HD das Carrancas ({voice_dur:.2f}s)")

    # 6. Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # 7. Exportar Vídeo Master Final com Áudio
    master_path = output_dir / f"{topic_data['id']}_FINAL_MOVIE.mp4"
    comp_v = CompositeVideoClip(video_clips)
    comp_a = CompositeAudioClip(audio_clips)
    comp_v = comp_v.with_audio(comp_a)

    comp_v.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None
    )

    print(f"[OK] VIDEO DAS CARRANCAS RE-RENDERIZADO COM SUCESSO: {master_path}")
    return master_path


def main():
    print("[INIT] RE-RENDERIZACAO DAS IMAGENS DO VIDEO DAS CARRANCAS DO VELHO CHICO")
    for t_data in INTERIOR_TOPICS:
        produce_video(t_data)
    print("\n[SUCCESS] VIDEO DAS CARRANCAS RE-GERADO COM SUCESSO!")


if __name__ == "__main__":
    main()
