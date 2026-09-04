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
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
output_dir = Path(__file__).resolve().parent / "output" / "videos" / "tamar_floripa_master_doc"
audio_dir = Path(__file__).resolve().parent / "output" / "audio" / "tamar_floripa_master_doc"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

output_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)

# 22 CENAS EXPANDIDAS PARA Atingir 3 MINUTOS E 15 SEGUNTOS (195s+) COM ZERO BURACOS DE ÁUDIO
SYNCHRONIZED_SCENES_3MIN = [
    # BLOCO 1: O MUSEU DO TAMAR
    {
        "scene_id": "01_museu_entrada",
        "narration": "Começamos o nosso documentário especial no Museu Educativo do Projeto Tamar na Ilha de Florianópolis!",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.55.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "02_museu_portal",
        "narration": "Logo na chegada, a recepção temática e os portais decorados convidam famílias e turistas para uma imersão completa na vida marinha.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.55.mp4",
        "vid_start": 8.0
    },
    {
        "scene_id": "03_museu_paineis",
        "narration": "O espaço conta com painéis científicos interativos, fotos históricas de resgates e maquetes educativas de alta precisão.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.43.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "04_museu_esqueletos",
        "narration": "Exposições impressionantes compostas por esqueletos reais de tartarugas marinhas ensinam na prática a anatomia desses incríveis répteis.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.43.mp4",
        "vid_start": 10.0
    },

    # BLOCO 2: AS ESPÉCIES DO TAMAR
    {
        "scene_id": "05_especies_gigantes",
        "narration": "Conheça agora as principais espécies protegidas pelo Projeto Tamar no Brasil! Ao caminhar pela área de tanques, ficamos cara a cara com gigantes oceânicos.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "06_especies_cabecuda",
        "narration": "Destaca-se a Tartaruga-Cabeçuda, famosa por sua estrutura robusta e mandíbula extremamente forte usada para triturar crustáceos no fundo do mar.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4",
        "vid_start": 12.0
    },
    {
        "scene_id": "07_especies_pente_verde",
        "narration": "Vemos também a icônica Tartaruga-de-Pente, ameaçada pelo valor histórico do seu casco, e a graciosa Tartaruga-Verde, herbívora essencial para os recifes.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4",
        "vid_start": 25.0
    },
    {
        "scene_id": "08_especies_oliva_couro",
        "narration": "O Tamar protege ainda a Tartaruga-Oliva e a monumental Tartaruga-de-Couro, a maior de todas as espécies marinhas do planeta.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4",
        "vid_start": 40.0
    },
    {
        "scene_id": "09_especies_ecologia",
        "narration": "Cada uma dessas espécies cumpre um papel ecológico insubstituível, controlando a população de águas-vivas e mantendo a vida dos oceanos saudável.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.06.mp4",
        "vid_start": 55.0
    },

    # BLOCO 3: A PRAIA DA BARRA DA LAGOA
    {
        "scene_id": "10_praia_orla",
        "narration": "Saindo dos pavilhões de exposição, somos brindados com o cenário paradisíaco do parque, situado ao lado da mundialmente famosa Praia da Barra da Lagoa!",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.13.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "11_praia_paisagem",
        "narration": "A brisa salgada do mar, a vegetação nativa preservada e a energia única da Ilha da Magia proporcionam um passeio encantador.",
        "video_file": "WhatsApp Video 2026-08-08 at 13.29.42.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "12_praia_canal",
        "narration": "O canal da Barra da Lagoa conecta a lagoa ao oceano Atlântico, criando um ecossistema rico e vibrante em Santa Catarina.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.01.59.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "13_praia_alamedas",
        "narration": "As alamedas de acesso contam com sinalização informativa e espaços de descanso sob a sombra das árvores costeiras.",
        "video_file": "WhatsApp Video 2026-08-08 at 13.29.10.mp4",
        "vid_start": 0.0
    },

    # BLOCO 4: OS TANQUES E AS TARTARUGAS NADANDO
    {
        "scene_id": "14_tanques_chegada",
        "narration": "Chegamos agora ao ponto alto da visita: os tanques abertos de água marinha límpida e cristalina!",
        "video_file": "WhatsApp Video 2026-08-08 at 14.02.39.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "15_tanques_transparencia",
        "narration": "É fascinante acompanhar a natação serena das tartarugas a poucos centímetros dos nossos olhos. A transparência da água revela o movimento harmonioso de suas nadadeiras.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.02.39.mp4",
        "vid_start": 10.0
    },
    {
        "scene_id": "16_tanques_detalhes_casco",
        "narration": "Cada curva do casco e cada respiração na superfície mostram a beleza e a resistência desses animais milenares.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.02.39.mp4",
        "vid_start": 25.0
    },
    {
        "scene_id": "17_tanques_reabilitacao",
        "narration": "Nestes tanques de observação, tartarugas resgatadas com ferimentos causados por redes de pesca recebem tratamento veterinário dedicado até sua plena recuperação.",
        "video_file": "WhatsApp Video 2026-08-08 at 13.29.07.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "18_tanques_soltura",
        "narration": "Quando os animais recuperam a saúde total, a equipe realiza a soltura comemorativa na praia, um momento emocionante para pesquisadores e visitantes.",
        "video_file": "WhatsApp Video 2026-08-08 at 13.29.07.mp4",
        "vid_start": 20.0
    },

    # BLOCO 5: ENCERRAMENTO E CTA
    {
        "scene_id": "19_encerramento_impacto",
        "narration": "Visitar o Projeto Tamar é a prova de que o turismo sustentável pode caminhar lado a lado com a ciência e a conservação da biodiversidade marinha no Brasil.",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.13.mp4",
        "vid_start": 0.0
    },
    {
        "scene_id": "20_encerramento_pergunta",
        "narration": "Você já teve a oportunidade de conhecer o Projeto Tamar em Florianópolis? Qual é o seu lugar preferido para visitar em Santa Catarina?",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.13.mp4",
        "vid_start": 15.0
    },
    {
        "scene_id": "21_encerramento_interacao",
        "narration": "Escreva a sua resposta nos comentários e compartilhe este vídeo com amigos e familiares que amam viajar e proteger a natureza!",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.13.mp4",
        "vid_start": 35.0
    },
    {
        "scene_id": "22_encerramento_cta",
        "narration": "Inscreva-se agora mesmo no canal Rota Calculada e ative o sininho para não perder nossas próximas expedições pelas maravilhas do Brasil!",
        "video_file": "WhatsApp Video 2026-08-08 at 14.03.13.mp4",
        "vid_start": 55.0
    }
]

async def generate_voice(text: str, out_path: str):
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="-1%")
            await communicate.save(out_path)
            if Path(out_path).exists() and Path(out_path).stat().st_size > 300:
                return
        except Exception:
            await asyncio.sleep(1.5)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception:
        pass

def render_3min_zero_gaps_documentary():
    print("==========================================")
    print("[PRODUZINDO DOCUMENTÁRIO 3m+ RIGOROSAMENTE SEM BURACOS DE ÁUDIO (180s+)]")
    print("==========================================")

    video_clips_list = []
    audio_clips_list = []
    raw_video_keepalive = []
    current_time = 0.0

    w_t, h_t = 1080, 1920

    for idx, sc in enumerate(SYNCHRONIZED_SCENES_3MIN, 1):
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        v_fname = sc["video_file"]
        v_st = sc["vid_start"]

        voice_file = audio_dir / f"sync_voice_3m_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        
        # Audio duration determines exact video subclip duration (+0.12s smooth buffer)
        exact_dur = voice_clip.duration + 0.12

        v_path = tamar_dir / v_fname
        if not v_path.exists():
            print(f"Warning: {v_fname} not found!")
            continue

        v_raw = VideoFileClip(str(v_path))
        raw_video_keepalive.append(v_raw)

        # Slice video subclip exactly matching voice duration
        if v_st + exact_dur <= v_raw.duration:
            v_sub = v_raw.subclipped(v_st, v_st + exact_dur)
        else:
            v_sub = v_raw.subclipped(0, min(v_raw.duration, exact_dur))
            if v_sub.duration < exact_dur:
                v_sub = CompositeVideoClip([v_raw, v_raw]).subclipped(0, exact_dur)

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
        video_clips_list.append(v_res)

        a_res = voice_clip.with_start(current_time).with_volume_scaled(1.7)
        audio_clips_list.append(a_res)

        current_time += exact_dur
        print(f"  ✓ Cena {idx:02d} [{scene_id}]: Duração {exact_dur:.2f}s | Acumulado: {current_time:.1f}s ({current_time/60.0:.2f} min)")

    v_comp = CompositeVideoClip(video_clips_list).with_duration(current_time)

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
            draw.text((540, 390), "DOCUMENTÁRIO COMPLETO ~3.2 MINUTOS", fill=(255, 255, 255), font=font_b, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        draw.rectangle([(25, 25), (1055, 1895)], outline=(255, 215, 0), width=6)
        return np.array(frame_pil)

    v_final_doc = v_comp.transform(add_doc_overlay)

    # Save thumbnail to artifacts for chat preview
    first_frame = Image.fromarray(v_final_doc.get_frame(1.5))
    first_frame.save(artifacts_dir / "tamar_floripa_zero_gaps_3min_thumb.png", format="PNG")

    # Relaxing Beach Music Background Soundtrack
    bgm_p = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        bgm = AudioFileClip(str(bgm_p)).subclipped(0, min(current_time, AudioFileClip(str(bgm_p)).duration)).with_volume_scaled(0.12)
        audio_clips_list.append(bgm)

    comp_a = CompositeAudioClip(audio_clips_list)
    v_final_doc = v_final_doc.with_audio(comp_a).with_duration(current_time)

    master_path = output_dir / "tamar_floripa_3min_documentary_FINAL_MOVIE.mp4"
    temp_aud = str(output_dir / "temp_audio_3min_zero_gaps.m4a")

    v_final_doc.write_videofile(str(master_path), codec="libx264", audio_codec="aac", temp_audiofile=temp_aud, remove_temp=True, fps=24, logger=None)

    v_final_doc.close()
    comp_a.close()
    for c in video_clips_list:
        c.close()
    for a in audio_clips_list:
        a.close()
    for v in raw_video_keepalive:
        v.close()

    print(f"\n🎉 [DOCUMENTÁRIO 3M+ SEM BURACOS DE ÁUDIO CONCLUÍDO] Duração Final: {current_time:.1f}s ({current_time/60.0:.2f} min) -> {master_path}")

if __name__ == "__main__":
    render_3min_zero_gaps_documentary()
