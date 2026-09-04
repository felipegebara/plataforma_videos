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
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
output_dir = Path(__file__).resolve().parent / "output" / "videos" / "tamar_floripa_master_doc"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "tamar_floripa_master_doc"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# 100% VIDEO FOOTAGE ONLY (ZERO STATIC IMAGES)
# EXACT ROTEIRO SOLICITADO PELO USUÁRIO:
# 1. Museu do Tamar -> 2. Espécies do Tamar -> 3. Praia da Barra da Lagoa -> 4. Tanques e Tartarugas Nadando -> 5. Encerramento & CTA
PERFECT_STORY_BLOCKS = [
    # BLOCO 1: O MUSEU DO TAMAR (Exclusivo vídeos do museu e recepção)
    {
        "block_id": "block1_museu",
        "title": "O MUSEU DO PROJETO TAMAR 🏛️",
        "narration": "Começamos o nosso passeio pelo Museu Educativo do Projeto Tamar em Florianópolis! Com painéis científicos interativos, réplicas em tamanho real e esqueletos de tartarugas marinhas, este espaço ensina de forma viva a importância da conscientização ambiental. É a porta de entrada perfeita para famílias e crianças aprenderem sobre os mistérios dos oceanos antes de irem para a área externa.",
        "vid_files": [
            {"name": "WhatsApp Video 2026-08-08 at 14.01.43.mp4", "dur": 21.0},
            {"name": "WhatsApp Video 2026-08-08 at 14.01.55.mp4", "dur": 25.0}
        ]
    },
    # BLOCO 2: AS ESPÉCIES DE TARTARUGAS DO TAMAR (Exclusivo vídeos das tartarugas gigantes)
    {
        "block_id": "block2_especies",
        "title": "AS ESPÉCIES DO PROJETO TAMAR 🐢",
        "narration": "Conheça agora as espécies de tartarugas protegidas no Tamar! Aqui no centro de visitantes de Floripa, encontramos a impressionante Tartaruga-Cabeçuda, famosa por sua mandíbula forte, a graciosa Tartaruga-Verde e a icônica Tartaruga-de-Pente. No Brasil, o projeto atua também na proteção da Tartaruga-de-Couro e da Tartaruga-Oliva. Cada uma desempenha um papel ecológico fundamental no equilíbrio do ecossistema marinho.",
        "vid_files": [
            {"name": "WhatsApp Video 2026-08-08 at 14.03.06.mp4", "dur": 45.0}
        ]
    },
    # BLOCO 3: A PRAIA DA BARRA DA LAGOA (Exclusivo vídeos da área externa, praia e placas)
    {
        "block_id": "block3_praia",
        "title": "A PRAIA DA BARRA DA LAGOA 🏖️🌊",
        "narration": "Saindo da área de exposições, somos presenteados com a localização espetacular do parque: exatamente ao lado da famosa Praia da Barra da Lagoa! O canal de águas calmas, a brisa do mar e a paisagem da Ilha da Magia tornam a visita uma experiência inesquecível de turismo sustentável no litoral catarinense.",
        "vid_files": [
            {"name": "WhatsApp Video 2026-08-08 at 14.01.13.mp4", "dur": 15.0},
            {"name": "WhatsApp Video 2026-08-08 at 13.29.42.mp4", "dur": 8.5},
            {"name": "WhatsApp Video 2026-08-08 at 13.29.10.mp4", "dur": 13.0}
        ]
    },
    # BLOCO 4: OS TANQUES E AS TARTARUGAS NADANDO (Exclusivo vídeos das tartarugas nadando no tanque em água cristalina)
    {
        "block_id": "block4_tanques",
        "title": "OS TANQUES E A NATAÇÃO DAS TARTARUGAS 💧🐢",
        "narration": "Chegamos ao coração do Projeto Tamar: os grandes tanques de água marinha límpida! Veja como é fascinante observar as tartarugas nadando livremente a poucos centímetros dos visitantes. A transparência da água revela a agilidade das nadadeiras e o desenho único do casco. Nesses tanques, animais resgatados recebem cuidados veterinários até estarem prontos para voltar ao mar.",
        "vid_files": [
            {"name": "WhatsApp Video 2026-08-08 at 14.02.39.mp4", "dur": 45.0},
            {"name": "WhatsApp Video 2026-08-08 at 13.29.07.mp4", "dur": 30.0}
        ]
    },
    # BLOCO 5: ENCERRAMENTO E CTA DO ROTA CALCULADA
    {
        "block_id": "block5_encerramento",
        "title": "INSCREVA-SE NO ROTA CALCULADA 🔔",
        "narration": "Você já conhecia o Projeto Tamar em Florianópolis? Qual sua praia favorita em Santa Catarina? Deixe seu comentário, compartilhe este vídeo com quem ama natureza e inscreva-se agora no canal Rota Calculada para acompanhar nossas próximas viagens e expedições pelo Brasil!",
        "vid_files": [
            {"name": "WhatsApp Video 2026-08-08 at 14.03.13.mp4", "dur": 25.0}
        ]
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

def produce_perfect_tamar_documentary():
    print("==========================================")
    print("[PRODUZINDO DOCUMENTÁRIO PERFECT TAMAR 3m+ (100% VÍDEO SEM FOTO PARADA)]")
    print("==========================================")

    clips_list = []
    audio_clips = []
    raw_video_keepalive = []
    current_time = 0.0
    w_t, h_t = 1080, 1920

    for b_idx, block in enumerate(PERFECT_STORY_BLOCKS, 1):
        block_id = block["block_id"]
        narration = block["narration"]
        v_list = block["vid_files"]

        voice_file = audio_dir / f"voice_{block_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        voice_dur = voice_clip.duration + 0.3

        # Assemble video clips assigned to this story block
        block_vids_dur = 0.0
        for v_item in v_list:
            v_fname = v_item["name"]
            req_dur = v_item["dur"]
            v_path = tamar_dir / v_fname

            if v_path.exists():
                v_raw = VideoFileClip(str(v_path))
                raw_video_keepalive.append(v_raw)

                sub_d = min(req_dur, v_raw.duration)
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
                block_vids_dur += sub_d

        # Attach voice audio exactly aligned
        audio_clips.append(voice_clip.with_start(current_time - block_vids_dur).with_volume_scaled(1.7))

        print(f"  ✓ Bloco {b_idx}: {block['title']} (Duração acumulada: {current_time:.1f}s / {current_time/60.0:.2f} min)")

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
            draw.text((540, 390), "DOCUMENTÁRIO 100% VÍDEO ~3.5 MINUTOS", fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final_doc = v_comp.transform(add_doc_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final_doc.get_frame(2.0))
    first_frame.save(artifacts_dir / "tamar_floripa_perfect_doc_thumb.png", format="PNG")

    # Beach Acoustic Relaxing Soundtrack
    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    comp_a = CompositeAudioClip(audio_clips)
    v_final_doc = v_final_doc.with_audio(comp_a).with_duration(current_time)

    master_path = output_dir / "tamar_floripa_3min_documentary_FINAL_MOVIE.mp4"
    temp_aud = str(output_dir / "temp_audio_perfect_doc.m4a")

    v_final_doc.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final_doc.close()
    comp_a.close()
    for c in clips_list:
        c.close()
    for a in audio_clips:
        a.close()
    for v in raw_video_keepalive:
        v.close()

    print(f"\n🎉 [DOCUMENTÁRIO PERFECT 3m+ CONCLUÍDO COM SUCESSO] Duração: {current_time:.1f}s ({current_time/60.0:.2f} min) -> {master_path}")

if __name__ == "__main__":
    produce_perfect_tamar_documentary()
