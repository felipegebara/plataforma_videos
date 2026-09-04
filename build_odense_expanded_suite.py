import os
import sys
import time
import json
import shutil
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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

odense_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\odense")
output_shorts_dir = Path(__file__).resolve().parent / "output" / "videos" / "odense_shorts"
output_long_dir = Path(__file__).resolve().parent / "output" / "videos" / "odense_master_doc"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "odense_suite"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
output_long_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# DEFINIÇÃO DOS 7 SHORTS DE ODENSE (DURAÇÃO PERFECT 12-15 SECONDS STRICT)
ODENSE_SHORTS_DEFINITIONS = [
    {
        "short_id": "short_odense_1",
        "title": "A Cidade de Hans Christian Andersen 🎩",
        "hook": "A CIDADE DOS CONTOS DE FADAS! 🎩",
        "narration": "Bem-vindo a Odense, na Dinamarca! A cidade natal de Hans Christian Andersen, o lendário autor que criou A Pequena Sereia, O Patinho Feio e O Soldadinho de Chumbo!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.09.50.mp4", "start": 0.0, "dur": 13.5}]
    },
    {
        "short_id": "short_odense_2",
        "title": "O Museu Encantado H.C. Andersens Hus 🏰",
        "hook": "MUSEU INTERATIVO MAGICO! 🏰",
        "narration": "Este é o famoso H.C. Andersens Hus! Um museu futurista projetado pelo renomado arquiteto Kengo Kuma, misturando natureza, tecnologia e os mistérios dos contos dinamarqueses!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.09.54.mp4", "start": 0.0, "dur": 13.8}]
    },
    {
        "short_id": "short_odense_3",
        "title": "Casinhas Coloridas Enxaimel 🏠",
        "hook": "RUAS HISTORICAS DA DINAMARCA! 🏠",
        "narration": "Caminhar pelas ruas de Odense é como viajar no tempo até o século dezenove! Suas casas históricas enxaimel preservam todo o charme da infância de um dos maiores escritores do planeta.",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.10.23.mp4", "start": 0.0, "dur": 13.2}]
    },
    {
        "short_id": "short_odense_4",
        "title": "A Estátua e o Legado de Andersen 📜",
        "hook": "O GENIO DOS CONTOS DE FADAS! 📜",
        "narration": "Nas praças e parques de Odense, estátuas e esculturas homenageiam os personagens lendários de Andersen que encantaram e continuam encantando gerações em todo o mundo!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.10.24 (2).mp4", "start": 0.0, "dur": 13.5}]
    },
    {
        "short_id": "short_odense_5",
        "title": "O Soldadinho de Chumbo e Contos Famosos 💂‍♂️",
        "hook": "A ORIGEM DOS MAIORES CONTOS! 💂‍♂️",
        "narration": "Você sabia que a infância humilde de Andersen nas ruas de Odense inspirou a criação de O Patinho Feio e O Soldadinho de Chumbo? Cada cantinho desta cidade histórica respira poesia e magia!",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.10.24 (1).mp4", "start": 0.0, "dur": 13.5}]
    },
    {
        "short_id": "short_odense_6",
        "title": "Jardins Secretos de Odense 🌿",
        "hook": "JARDINS MAGICOS DA DINAMARCA! 🌿",
        "narration": "Os parques e jardins ao redor do museu H.C. Andersens Hus parecem ter saído diretamente de um livro de histórias! Uma atmosfera de paz, beleza e arquitetura única na Dinamarca.",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.10.24.mp4", "start": 0.0, "dur": 13.2}]
    },
    {
        "short_id": "short_odense_7",
        "title": "Vale a Pena Visitar Odense? 🇩🇰",
        "hook": "VALE A PENA CONHECER ODENSE? 🇩🇰",
        "narration": "Visitar a cidade histórica de Odense na ilha de Fyn é um passeio inesquecível em qualquer viagem pelo norte da Europa! Um destino perfeito para quem ama cultura e literatura.",
        "video_clips": [{"file": "WhatsApp Video 2026-08-11 at 21.09.50.mp4", "start": 5.0, "dur": 13.5}]
    }
]

# DOCUMENTÁRIO MASTER COMPLETO DE ODENSE
ODENSE_LONG_DOC_SCENES = [
    {
        "scene_id": "01_intro_odense",
        "narration": "Bem-vindo a Odense, a terceira maior cidade da Dinamarca e a terra natal de um dos maiores contadores de histórias de toda a humanidade!",
        "video_file": "WhatsApp Video 2026-08-11 at 21.09.50.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "02_nascimento_andersen",
        "narration": "Foi aqui que em mil oitocentos e cinco nasceu Hans Christian Andersen, filho de um humilde sapateiro e de uma lavadeira.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.10.23.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "03_ruas_historicas",
        "narration": "As ruas de paralelepípedo e as tradicionais casinhas enxaimel coloridas preservam até hoje a atmosfera mágica que alimentou a imaginação do jovem escritor.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.10.24 (2).mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "04_museu_kengo_kuma",
        "narration": "O grande destaque da cidade é o novo museu H.C. Andersens Hus, projetado pelo renomado arquiteto japonês Kengo Kuma.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.09.54.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "05_experiencia_imersiva",
        "narration": "Em vez de apenas exibir objetos antigos, o museu proporciona uma imersão sensorial completa pelos mundos da Pequena Sereia, do Patinho Feio e da Polegarzinha.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.10.24 (1).mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "06_jardins_natureza",
        "narration": "Jardins suspensos, sebes vivas e labirintos de plantas conectam a arquitetura moderna do museu com a natureza serena da cidade de Odense.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.10.24.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "07_legado_universal",
        "narration": "A obra de Andersen transcendeu fronteiras e idiomas, ensinando ao mundo lições sobre empatia, resiliência e a beleza de ser diferente.",
        "video_file": "WhatsApp Video 2026-08-11 at 21.09.50.mp4",
        "vid_start": 5.0
    },
    {
        "scene_id": "08_encerramento_cta",
        "narration": "Qual conto de fadas marcou a sua infância? Deixe sua resposta nos comentários e inscreva-se no canal Rota Calculada para explorar os lugares mais fascinantes do mundo!",
        "video_file": "WhatsApp Video 2026-08-11 at 21.09.54.mp4",
        "vid_start": 5.0
    }
]

async def generate_voice(text: str, out_path: str):
    p = Path(out_path)
    if p.exists() and p.stat().st_size > 1000:
        return

    for attempt in range(5):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-1%")
            await communicate.save(out_path)
            if p.exists() and p.stat().st_size > 1000:
                return
        except Exception:
            await asyncio.sleep(2.0)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        pass

def produce_all_odense_videos():
    print("==========================================")
    print("[PRODUZINDO SUÍTE EXPANDIDA DE ODENSE: 7 SHORTS (12-14S PERFEITOS) + MASTER DOC!]")
    print("==========================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    # --- 1. PRODUZIR OS 7 SHORTS ---
    for idx, sdef in enumerate(ODENSE_SHORTS_DEFINITIONS, 1):
        short_id = sdef["short_id"]
        title = sdef["title"]
        hook_text = sdef["hook"]
        narration = sdef["narration"]
        v_clips_def = sdef.get("video_clips", [])

        voice_file = audio_dir / f"voice_{short_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.3

        clips_list = []
        raw_keepalive = []
        current_time = 0.0

        item_dur = target_dur / float(len(v_clips_def))
        for v_info in v_clips_def:
            v_fname = v_info["file"]
            v_st = v_info.get("start", 0.0)
            v_path = odense_dir / v_fname
            if v_path.exists():
                v_raw = VideoFileClip(str(v_path))
                raw_keepalive.append(v_raw)

                sub_d = min(item_dur, max(0.1, v_raw.duration - v_st))
                v_sub = v_raw.subclipped(v_st, v_st + sub_d)

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

        v_comp = CompositeVideoClip(clips_list).with_duration(current_time)

        def add_short_overlay(get_frame, t):
            frame = get_frame(t)
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)

            if t < 2.5:
                draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 230))
                draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
                draw.text((540, 350), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

            draw.rectangle([(0, 80), (1080, 160)], fill=(0, 0, 0, 160))
            draw.text((540, 120), "ROTA CALCULADA | ODENSE 🎩", fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
            return np.array(frame_pil)

        v_final_short = v_comp.transform(add_short_overlay)

        first_frame = Image.fromarray(v_final_short.get_frame(1.2))
        first_frame.save(artifacts_dir / f"{short_id}_thumb.png", format="PNG")

        bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.7)]

        if bgm_p.exists():
            bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
            audio_mix.append(bgm)

        comp_a = CompositeAudioClip(audio_mix)
        v_final_short = v_final_short.with_audio(comp_a).with_duration(current_time)

        master_path = output_shorts_dir / f"{short_id}_FINAL_MOVIE.mp4"
        temp_aud = str(output_shorts_dir / f"temp_audio_{short_id}_{run_id}_{idx}.m4a")

        v_final_short.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

        v_final_short.close()
        comp_a.close()
        for c in clips_list:
            c.close()
        for v in raw_keepalive:
            v.close()

        print(f"  ✓ Short {idx:02d} [{short_id}]: {title} | Duração: {current_time:.1f}s -> {master_path}")

    # --- 2. PRODUZIR DOCUMENTÁRIO MASTER ESTENDIDO DE ODENSE ---
    print("\n[PRODUZINDO DOCUMENTÁRIO MASTER ESTENDIDO DE ODENSE]")
    long_video_clips = []
    long_audio_clips = []
    long_raw_keepalive = []
    long_time = 0.0

    for idx, sc in enumerate(ODENSE_LONG_DOC_SCENES, 1):
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        v_fname = sc["video_file"]
        v_st = sc["vid_start"]

        voice_file = audio_dir / f"sync_voice_long_{scene_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        exact_dur = voice_clip.duration + 0.15

        v_path = odense_dir / v_fname
        if v_path.exists():
            v_raw = VideoFileClip(str(v_path))
            long_raw_keepalive.append(v_raw)

            if v_st + exact_dur <= v_raw.duration:
                v_sub = v_raw.subclipped(v_st, v_st + exact_dur)
            else:
                v_sub = v_raw.subclipped(0, min(v_raw.duration, exact_dur))

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

            v_res = v_crop.resized((w_t, h_t)).with_start(long_time)
            long_video_clips.append(v_res)

            long_audio_clips.append(voice_clip.with_start(long_time).with_volume_scaled(1.7))
            long_time += exact_dur

            print(f"  ✓ Cena {idx:02d} [{scene_id}]: Duração {exact_dur:.2f}s | Acumulado: {long_time:.1f}s ({long_time/60.0:.2f} min)")

    v_long_comp = CompositeVideoClip(long_video_clips).with_duration(long_time)

    def add_long_doc_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        if t < 4.5:
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), "ODENSE - DINAMARCA 🎩", fill=(255, 215, 0), font=font_sub, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), "DOCUMENTÁRIO COMPLETO ~1.8 MINUTOS", fill=(255, 255, 255), font=font_sub, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_long_final = v_long_comp.transform(add_long_doc_overlay)

    first_frame_long = Image.fromarray(v_long_final.get_frame(1.5))
    first_frame_long.save(artifacts_dir / "odense_master_doc_thumb.png", format="PNG")

    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm_long = AudioFileClip(str(bgm_p)).subclipped(0, min(long_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        long_audio_clips.append(bgm_long)

    comp_a_long = CompositeAudioClip(long_audio_clips)
    v_long_final = v_long_final.with_audio(comp_a_long).with_duration(long_time)

    long_master_path = output_long_dir / "odense_master_doc_FINAL_MOVIE.mp4"
    temp_aud_long = str(output_long_dir / f"temp_audio_long_{run_id}.m4a")

    v_long_final.write_videofile(str(long_master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud_long, remove_temp=True, fps=24, logger=None)

    v_long_final.close()
    comp_a_long.close()
    for c in long_video_clips:
        c.close()
    for a in long_audio_clips:
        a.close()
    for v in long_raw_keepalive:
        v.close()

    print(f"\n🎉 [SUÍTE EXPANDIDA DE ODENSE CONCLUÍDA] 7 Shorts + Documentário Master ({long_time:.1f}s / {long_time/60.0:.2f} min) -> {long_master_path}")

if __name__ == "__main__":
    produce_all_odense_videos()
