import os
import sys
import time
import json
import shutil
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import edge_tts
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
output_base = Path(__file__).resolve().parent / "output" / "videos"
audio_base = Path(__file__).resolve().parent / "output" / "audio"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

# Gather raw video files
raw_vids = sorted(list(tamar_dir.glob("*.mp4")))
raw_imgs = sorted(list(tamar_dir.glob("*.jpg")) + list(tamar_dir.glob("*.jpeg")))

SHORTS_SPECS = [
    {
        "topic_id": "short_tamar_floripa_1",
        "title": "Short 1: O Maior Refúgio de Tartarugas de Floripa",
        "hook_text": "O MAIOR REFÚGIO DE TARTARUGAS! 🐢🌊",
        "sub_text": "PROJETO TAMAR - FLORIANÓPOLIS",
        "narration": "Você sabia que em Florianópolis existe um santuário incrível dedicado a salvar as tartarugas marinhas? No Projeto Tamar da Barra da Lagoa, você fica frente a frente com espécies gigantes! Siga o Rota Calculada!",
        "video_idx": [0, 1]
    },
    {
        "topic_id": "short_tamar_floripa_2",
        "title": "Short 2: Como é a Alimentação das Tartarugas",
        "hook_text": "ALIMENTAÇÃO DAS TARTARUGAS! 🥬🐟",
        "sub_text": "BARRA DA LAGOA - FLORIPA",
        "narration": "Olhe só como funciona o momento da alimentação das tartarugas no Projeto Tamar! Os biólogos explicam a dieta de cada espécie enquanto elas nadam pertinho dos visitantes. Incrível né? Siga o Rota Calculada!",
        "video_idx": [2, 3]
    },
    {
        "topic_id": "short_tamar_floripa_3",
        "title": "Short 3: Vale a Pena Visitar o Tamar em Floripa",
        "hook_text": "VALE A PENA VISITAR O TAMAR? 📍🇧🇷",
        "sub_text": "DICA DE VIAGEM EM FLORIPA",
        "narration": "Vale a pena visitar o Projeto Tamar na Barra da Lagoa em Floripa? Com tanques gigantes, museu interativo e passeio à beira-mar, é um dos melhores passeios da ilha! Salve esse vídeo e siga o Rota Calculada!",
        "video_idx": [4, 5]
    },
    {
        "topic_id": "short_tamar_floripa_4",
        "title": "Short 4: Como o Tamar Salva Tartarugas em Extinção",
        "hook_text": "COMO O TAMAR SALVA TARTARUGAS? 🛡️🐢",
        "sub_text": "CONSERVAÇÃO E REABILITAÇÃO",
        "narration": "Como o Projeto Tamar salva milhares de tartarugas marinhas da extinção? Muitas são resgatadas de redes de pesca e reabilitadas aqui antes de voltarem ao oceano! Deixe seu apoio e siga o Rota Calculada!",
        "video_idx": [6, 7]
    },
    {
        "topic_id": "short_tamar_floripa_5",
        "title": "Short 5: Espaço Educativo e Atividades no Tamar",
        "hook_text": "ESPAÇO EDUCATIVO NO TAMAR! 🎨🦴",
        "sub_text": "CULTURA E PRESERVAÇÃO",
        "narration": "Além dos tanques, o Tamar em Florianópolis tem um espaço educativo sensacional com réplicas gigantes, esqueletos e oficinas para crianças! Um passeio perfeito para a família! Siga o Rota Calculada!",
        "video_idx": [8, 9]
    },
    {
        "topic_id": "short_tamar_floripa_6",
        "title": "Short 6: Praia da Barra da Lagoa e o Tamar",
        "hook_text": "PRAIA DA BARRA DA LAGOA + TAMAR! 🏖️🌊",
        "sub_text": "FLORIANÓPOLIS - SC",
        "narration": "Localizado exatamente na Praia da Barra da Lagoa, o Projeto Tamar une a beleza natural de Florianópolis à conscientização ambiental. Qual sua praia favorita em Floripa? Comente e siga o Rota Calculada!",
        "video_idx": [10, 11]
    }
]

async def generate_voice(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+4%")
    await communicate.save(out_path)

def process_short_video(spec: dict):
    topic_id = spec["topic_id"]
    title = spec["title"]
    hook = spec["hook_text"]
    sub = spec["sub_text"]
    narration = spec["narration"]
    v_indices = spec["video_idx"]

    out_dir = output_base / topic_id
    aud_dir = audio_base / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    aud_dir.mkdir(parents=True, exist_ok=True)

    voice_path = aud_dir / "voice.mp3"
    asyncio.run(generate_voice(narration, str(voice_path)))
    voice_clip = AudioFileClip(str(voice_path))
    target_dur = max(13.0, voice_clip.duration + 0.2)

    # Use raw videos assigned
    clips_to_concat = []
    dur_per_clip = target_dur / len(v_indices)

    for idx in v_indices:
        v_path = raw_vids[idx % len(raw_vids)]
        v_raw = VideoFileClip(str(v_path))
        sub_dur = min(dur_per_clip, v_raw.duration)
        v_sub = v_raw.subclipped(0, sub_dur)

        # Scale & Crop to 9:16 Vertical HD 1080x1920
        w_t, h_t = 1080, 1920
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

        v_resized = v_crop.resized((w_t, h_t))
        clips_to_concat.append(v_resized)

    # Build sequence
    current_t = 0.0
    timed_clips = []
    for c in clips_to_concat:
        timed_clips.append(c.with_start(current_t))
        current_t += c.duration

    v_comp = CompositeVideoClip(timed_clips).with_duration(target_dur)

    try:
        font_b = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_b = ImageFont.load_default()

    def add_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        if t < 2.5:
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), hook, fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), sub, fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final = v_comp.transform(add_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final.get_frame(0.5))
    first_frame.save(artifacts_dir / f"{topic_id}_thumb.png", format="PNG")

    audio_clips = [voice_clip.with_volume_scaled(1.7)]
    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(target_dur, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    comp_a = CompositeAudioClip(audio_clips)
    v_final = v_final.with_audio(comp_a).with_duration(target_dur)

    master_path = out_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    temp_aud = str(out_dir / f"temp_audio_{topic_id}.m4a")

    v_final.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final.close()
    comp_a.close()
    voice_clip.close()
    for c in clips_to_concat:
        c.close()

    print(f"  ✓ [{title.upper()} CONCLUÍDO] Duração: {target_dur:.1f}s -> {master_path}")

def process_master_documentary():
    topic_id = "tamar_floripa_master_doc"
    out_dir = output_base / topic_id
    aud_dir = audio_base / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    aud_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 Montando OPÇÃO A: Mini-Documentário Master do Projeto Tamar Floripa...")

    narration_script = (
        "Bem-vindos ao Projeto Tamar em Florianópolis, localizado na deslumbrante Praia da Barra da Lagoa. "
        "Fundado para proteger as tartarugas marinhas ameaçadas de extinção no litoral brasileiro, o centro de visitantes de Floripa é um dos pontos mais fascinantes da ilha de Santa Catarina. "
        "Aqui, os visitantes acompanham de perto espécies como a Tartaruga-Cabeçuda, a Tartaruga-de-Pente e a Tartaruga-Verde nadando em tanques gigantes de água marinha. "
        "Durante o passeio, os biólogos realizam palestras explicativas e demonstram a alimentação dos animais, destacando a importância da preservação dos oceanos. "
        "Além dos tanques, o complexo conta com um museu interativo, exposições de esqueletos reais e espaço cultural para crianças e famílias. "
        "Um passeio inesquecível que une conscientização ambiental, ciência e as belezas naturais da Barra da Lagoa. "
        "Se você ama a natureza e viagens, inscreva-se no canal Rota Calculada e acompanhe nossos próximos destinos pelo Brasil!"
    )

    voice_path = aud_dir / "master_voice.mp3"
    asyncio.run(generate_voice(narration_script, str(voice_path)))
    voice_clip = AudioFileClip(str(voice_path))
    doc_dur = voice_clip.duration + 0.5

    # Sequence all 12 raw videos smoothly
    clips_doc = []
    current_t = 0.0
    dur_per_video = doc_dur / len(raw_vids)

    w_t, h_t = 1080, 1920
    try:
        font_b = ImageFont.truetype("arialbd.ttf", 42)
    except Exception:
        font_b = ImageFont.load_default()

    for idx, v_path in enumerate(raw_vids):
        v_raw = VideoFileClip(str(v_path))
        sub_d = min(dur_per_video, v_raw.duration)
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

        v_res = v_crop.resized((w_t, h_t)).with_start(current_t)
        clips_doc.append(v_res)
        current_t += sub_d

    v_comp_doc = CompositeVideoClip(clips_doc).with_duration(doc_dur)

    def add_doc_overlay(get_frame, t):
        frame = get_frame(t)
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)
        if t < 3.5:
            draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
            draw.text((540, 320), "PROJETO TAMAR FLORIPA 🐢", fill=(255, 215, 0), font=font_b, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 390), "DOCUMENTÁRIO COMPLETO - BARRA DA LAGOA", fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final_doc = v_comp_doc.transform(add_doc_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final_doc.get_frame(1.0))
    first_frame.save(artifacts_dir / f"{topic_id}_thumb.png", format="PNG")

    audio_clips = [voice_clip.with_volume_scaled(1.7)]
    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(doc_dur, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips.append(bgm)

    comp_a = CompositeAudioClip(audio_clips)
    v_final_doc = v_final_doc.with_audio(comp_a).with_duration(doc_dur)

    master_path = out_dir / f"{topic_id}_FINAL_MOVIE.mp4"
    temp_aud = str(out_dir / f"temp_audio_{topic_id}.m4a")

    v_final_doc.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final_doc.close()
    comp_a.close()
    voice_clip.close()
    for c in clips_doc:
        c.close()

    print(f"🎉 [DOCUMENTÁRIO MASTER CONCLUÍDO] Duração: {doc_dur:.1f}s ({doc_dur/60.0:.2f} min) -> {master_path}")

def build_full_tamar_suite():
    print("==========================================")
    print("[PRODUZINDO SUÍTE COMPLETA: 6 SHORTS + MINI-DOCUMENTÁRIO MASTER TAMAR FLORIPA]")
    print("==========================================")

    # 1. Process 6 Shorts
    for spec in SHORTS_SPECS:
        process_short_video(spec)

    # 2. Process Master Documentary
    process_master_documentary()

if __name__ == "__main__":
    build_full_tamar_suite()
