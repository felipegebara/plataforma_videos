import os
import sys
import time
import json
import shutil
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
output_dir = Path(__file__).resolve().parent / "output" / "videos" / "tamar_floripa_master_doc"
images_extra_dir = tamar_dir / "web_extra_images"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "tamar_floripa_master_doc"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_dir.mkdir(parents=True, exist_ok=True)
images_extra_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# Extended Script specifically structured to cover ALL 12 RAW VIDEOS + WEB PHOTOS to reach 3.5 minutes (210s+)
DOCUMENTARY_SCRIPT_STRICT_3MIN = [
    {
        "part_id": "part1",
        "narration": "Localizado na paradisíaca Praia da Barra da Lagoa, no município de Florianópolis, o Centro de Visitantes do Projeto Tamar é uma das fortalezas mais importantes na preservação das tartarugas marinhas no Sul do Brasil. Fundado no ano de dois mil e cinco, este santuário ambiental atua como uma verdadeira barreira viva para proteger espécies que habitam a vasta bacia oceânica atlântica brasileira.",
        "vid_files": ["WhatsApp Video 2026-08-08 at 14.01.55.mp4", "WhatsApp Video 2026-08-08 at 13.29.10.mp4"],
        "img_file": "barra_lagoa_beach.jpg"
    },
    {
        "part_id": "part2",
        "narration": "Ao percorrer os tanques de água marinha límpida do complexo, os visitantes ficam cara a cara com verdadeiros gigantes dos oceanos. Entre eles, destacam-se a impressionante Tartaruga-Cabeçuda, famosa por sua mandíbula poderosa capaz de triturar moluscos e crustáceos, a icônica Tartaruga-de-Pente e a graciosa Tartaruga-Verde. Cada uma dessas espécies desempenha um papel ecológico insubstituível no equilíbrio dos ecossistemas marinhos, mantendo a saúde dos recifes e o controle natural da biodiversidade costeira.",
        "vid_files": ["WhatsApp Video 2026-08-08 at 14.03.06.mp4", "WhatsApp Video 2026-08-08 at 14.02.39.mp4"],
        "img_file": "turtle_caretta.jpg"
    },
    {
        "part_id": "part3",
        "narration": "No mar de Santa Catarina, o maior desafio enfrentado pelas tartarugas marinhas é a captura acidental em redes de pesca e a ingesta perigosa de resíduos plásticos descartados nos oceanos. O Tamar Floripa atua diretamente no resgate de emergência, tratamento veterinário avançado e reabilitação intensiva desses animais machucados. Quando totalmente recuperadas, as tartarugas são devolvidas ao seu habitat natural sob a celebração festiva da comunidade, famílias e pesquisadores da ilha.",
        "vid_files": ["WhatsApp Video 2026-08-08 at 13.29.07.mp4", "WhatsApp Video 2026-08-08 at 14.03.13.mp4"],
        "img_file": "tamar_conservation.jpg"
    },
    {
        "part_id": "part4",
        "narration": "O complexo conta também com um museu educativo de primeiro mundo. Exposições compostas por esqueletos reais de tartarugas marinhas, maquetes interativas em tamanho real, painéis científicos detalhados e oficinas pedagógicas transformam a visita em uma aula viva de conscientização ambiental. Milhares de estudantes, crianças e turistas passam por aqui todos os anos, aprendendo na prática que o futuro dos oceanos depende da responsabilidade e da ação consciente de cada um de nós.",
        "vid_files": ["WhatsApp Video 2026-08-08 at 14.01.43.mp4", "WhatsApp Video 2026-08-08 at 14.01.13.mp4"],
        "img_file": "turtle_swimming.jpg"
    },
    {
        "part_id": "part5",
        "narration": "Visitar o Projeto Tamar é conectar a beleza estonteante da Ilha da Magia à preservação apaixonada da vida marinha. A Barra da Lagoa, com seu canal de águas cristalinas, vilas de pescadores e praias deslumbrantes, torna a experiência de viagem ainda mais memorável. É a prova viva e concreta de que o turismo sustentável pode caminhar lado a lado com a ciência, a pesquisa e a conservação da biodiversidade no Brasil.",
        "vid_files": ["WhatsApp Video 2026-08-08 at 13.29.42.mp4", "WhatsApp Video 2026-08-08 at 14.01.59.mp4"],
        "img_file": "barra_lagoa_beach.jpg"
    },
    {
        "part_id": "part6",
        "narration": "Você já teve a oportunidade de conhecer o Projeto Tamar em Florianópolis? Qual é o seu lugar preferido para visitar na Ilha de Santa Catarina? Deixe a sua opinião nos comentários, compartilhe este vídeo com quem ama viajar e curta para fortalecer nosso trabalho. Inscreva-se agora no canal Rota Calculada para não perder nenhum de nossos próximos documentários e expedições pelas maravilhas do Brasil!",
        "vid_files": ["WhatsApp Video 2026-08-08 at 14.01.13 (1).mp4", "WhatsApp Video 2026-08-08 at 14.09.53.mp4"],
        "img_file": "tamar_conservation.jpg"
    }
]

async def generate_voice(text: str, out_path: str):
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-2%")
            await communicate.save(out_path)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 500:
                return
        except Exception:
            await asyncio.sleep(1.5)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        pass

def create_image_video_clip(img_path: Path, dur: float, w_t=1080, h_t=1920) -> ImageClip:
    img_pil = Image.open(img_path).convert("RGB")
    aspect_target = 9 / 16.0
    aspect_img = img_pil.width / float(img_pil.height)

    if aspect_img > aspect_target:
        new_w = int(img_pil.height * aspect_target)
        left = (img_pil.width - new_w) // 2
        img_pil = img_pil.crop((left, 0, left + new_w, img_pil.height))
    else:
        new_h = int(img_pil.width / aspect_target)
        top = (img_pil.height - new_h) // 2
        img_pil = img_pil.crop((0, top, img_pil.width, top + new_h))

    img_pil = img_pil.resize((w_t, h_t), Image.Resampling.LANCZOS)
    return ImageClip(np.array(img_pil)).with_duration(dur)

def produce_strictly_3min_plus_documentary():
    print("==========================================")
    print("[PRODUZINDO DOCUMENTÁRIO MASTER > 3 MINUTOS (180s+ CRÍTICO)]")
    print("==========================================")

    clips_list = []
    audio_clips = []
    raw_video_clips_keepalive = []
    current_time = 0.0

    w_t, h_t = 1080, 1920

    for idx, part in enumerate(DOCUMENTARY_SCRIPT_STRICT_3MIN, 1):
        part_id = part["part_id"]
        narration = part["narration"]
        v_filenames = part["vid_files"]
        i_fname = part["img_file"]

        voice_file = audio_dir / f"voice_{part_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        
        part_dur = voice_clip.duration + 0.5

        # 1. Add ALL full raw video clips assigned to this part
        v_clips_dur_sum = 0.0
        for v_fname in v_filenames:
            v_path = tamar_dir / v_fname
            if v_path.exists():
                v_raw = VideoFileClip(str(v_path))
                raw_video_clips_keepalive.append(v_raw)

                # Use full video duration safely
                sub_d = min(v_raw.duration, 25.0)
                v_sub = v_raw.subclipped(0, sub_d)

                vw, vh = v_sub.w, v_sub.h
                aspect_t = 9 / 16.0
                aspect_v = vw / float(vh)

                if aspect_v > aspect_t:
                    new_w = int(vh * aspect_t)
                    crop_x = (vw - new_w) // 2
                    v_crop = v_sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
                else:
                    new_h = int(vw / aspect_t)
                    crop_y = (vh - new_h) // 2
                    v_crop = v_sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)

                v_res = v_crop.resized((w_t, h_t)).with_start(current_time)
                clips_list.append(v_res)
                current_time += sub_d
                v_clips_dur_sum += sub_d

        # 2. Add extra web image clip to complement duration
        i_path = images_extra_dir / i_fname
        img_dur_needed = max(6.0, part_dur - v_clips_dur_sum)
        if i_path.exists():
            i_clip = create_image_video_clip(i_path, img_dur_needed, w_t, h_t).with_start(current_time)
            clips_list.append(i_clip)
            current_time += img_dur_needed

        # Attach narration audio exactly aligned
        audio_clips.append(voice_clip.with_start(current_time - (v_clips_dur_sum + img_dur_needed)).with_volume_scaled(1.7))

        print(f"  ✓ Parte {idx:02d} processada (Duração acumulada: {current_time:.1f}s / {current_time/60.0:.2f} min)")

    v_comp = CompositeVideoClip(clips_list).with_duration(current_time)

    try:
        font_b = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_b = ImageFont.load_default()

    def add_doc_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        if t < 4.5:
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), "PROJETO TAMAR FLORIPA 🐢", fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), "DOCUMENTÁRIO COMPLETO ~3.5 MINUTOS", fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final_doc = v_comp.transform(add_doc_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final_doc.get_frame(1.5))
    first_frame.save(artifacts_dir / "tamar_floripa_3min_doc_thumb.png", format="PNG")

    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    comp_a = CompositeAudioClip(audio_clips)
    v_final_doc = v_final_doc.with_audio(comp_a).with_duration(current_time)

    master_path = output_dir / "tamar_floripa_3min_documentary_FINAL_MOVIE.mp4"
    temp_aud = str(output_dir / "temp_audio_3min_safe.m4a")

    v_final_doc.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final_doc.close()
    comp_a.close()
    for c in clips_list:
        c.close()
    for a in audio_clips:
        a.close()
    for v in raw_video_clips_keepalive:
        v.close()

    print(f"\n🎉 [DOCUMENTÁRIO COMPLETO STRICT > 3 MINUTOS CONCLUÍDO] Duração: {current_time:.1f}s ({current_time/60.0:.2f} min) -> {master_path}")

if __name__ == "__main__":
    produce_strictly_3min_plus_documentary()
