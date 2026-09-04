import os
import sys
import time
import json
import asyncio
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import edge_tts
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, concatenate_videoclips, vfx

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent
legoland_dir = base_dir / "output" / "legoland"
output_long_dir = base_dir / "output" / "videos" / "legoland_master_doc"
audio_dir = base_dir / "output" / "audio" / "legoland_train_journey"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\8289ff40-6fee-4bc8-a053-70c64e03f4f7")

output_long_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir.mkdir(parents=True, exist_ok=True)

# ESTRUTURA DO TOUR SOBRE TRILHOS: O TREM DA LEGOLAND CONECTANDO TODAS AS ÁREAS DO PARQUE
LEGOLAND_TRAIN_JOURNEY_SCENES = [
    {
        "scene_id": "01_trem_partida_safari",
        "badge": "PARTIDA DO TREM: ESTAÇÃO CENTRAL 🚂",
        "topic": "TODOS A BORDO DO LEGOLAND EXPRESS!",
        "narration": "Todos a bordo do Legoland Express! Hoje nós vamos fazer uma viagem mágica sobre os trilhos pelo primeiro parque Legoland do mundo, em Billund na Dinamarca! O trem parte da estação central e logo avistamos a área do Safari com animais selvagens esculpidos em Lego!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 0.5, "dur": 17.5}
        ]
    },
    {
        "scene_id": "02_parada_entrada_historia",
        "badge": "PARADA 1: PORTAL DE ENTRADA 🇩🇰",
        "topic": "A FUNDAÇÃO DA LEGOLAND EM 1968",
        "narration": "Nossa primeira parada é o histórico portal de entrada do parque! Fundado em mil novecentos e sessenta e oito por Ole Kirk Christiansen e seu filho Godtfred, a Legoland foi construída exatamente ao lado da fábrica original da Lego para receber visitantes do planeta inteiro.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.46.18.mp4", "start": 0.5, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.46.21.mp4", "start": 0.5, "dur": 6.5},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (3).mp4", "start": 0.5, "dur": 5.5}
        ]
    },
    {
        "scene_id": "03_trem_caminho_miniland",
        "badge": "TRILHOS DO TREM: RUMO A MINILAND 🌿",
        "topic": "PASSANDO PELAS PONTES E JARDINS",
        "narration": "O trem volta a acelerar pelos trilhos entre bosques e pontes de madeira! Pela janela, começamos a ver a aproximação da área mais emblemática e famosa de todo o complexo: a grandiosa Miniland!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 30.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "04_parada_miniland_copenhague",
        "badge": "PARADA 2: MINILAND COPENHAGUE 🇩🇰",
        "topic": "PORTO DE NYHAVN & CANAIS REAIS",
        "narration": "Olha que espetáculo! O trem margeia o famoso porto de Nyhavn, em Copenhague. Mais de três milhões de pecinhas Lego recriam os casarios coloridos, pontes históricas e navios mercantes que navegam em águas de verdade!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (6).mp4", "start": 1.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "05_parada_miniland_aeroporto",
        "badge": "PARADA 3: AEROPORTO DE BILLUND ✈️",
        "topic": "PISTAS & JATOS EM MOVIMENTO",
        "narration": "Logo ao lado dos trilhos, avistamos a réplica exata do Aeroporto Internacional de Billund! Aviões a jato e aeronaves comerciais taxiam continuamente pelas pistas acionados por motores elétricos de alta precisão!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (5).mp4", "start": 2.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "06_parada_miniland_fazendas",
        "badge": "PARADA 4: FAZENDAS & MOINHOS 🚜",
        "topic": "A VIDA RURAL NÓRDICA EM LEGO",
        "narration": "Seguindo pelo caminho, o trem passa pelos campos da zona rural nórdica! Vemos moinhos de vento clássicos girando com o vento, tratores cultivando os campos e dezenas de animais de fazenda esculpidos peça por peça!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (7).mp4", "start": 1.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "07_parada_miniland_eclusas",
        "badge": "PARADA 5: ENGENHARIA DOS CANAIS 🚤",
        "topic": "ECLUSAS AQUÁTICAS DE VERDADE",
        "narration": "Neste trecho do percurso, vemos os canais navegáveis com um engenhoso sistema de eclusas aquáticas reais! Os barcos de Lego sobem e descem os níveis da água automaticamente cercados por jardins estilo bonsai!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (3).mp4", "start": 2.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "08_parada_miniland_transito",
        "badge": "PARADA 6: TRÂNSITO INTELIGENTE 🚗",
        "topic": "RUAS E CARROS AUTÔNOMOS",
        "narration": "Olha o dinamismo urbano desta cidade em miniatura! Carros, ônibus e caminhões circulam pelas ruas parando nos semáforos e faixas, movidos por cabos elétricos condutores subterrâneos!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (4).mp4", "start": 2.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "09_trem_caminho_piratas",
        "badge": "TRILHOS DO TREM: ZONA DOS PIRATAS 🏴‍☠️",
        "topic": "AVANÇANDO PELO PARQUE",
        "narration": "O apito do trem soa novamente enquanto cruzamos novas alamedas floridas do parque! Estamos agora nos aproximando dos mares revoltos e das aventuras da terra dos Piratas!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 80.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "10_parada_pirate_land",
        "badge": "PARADA 7: PIRATE LAND 🏴‍☠️",
        "topic": "BANDA DO JACK SPARROW & BATALHAS",
        "narration": "Paramos em Pirate Land e somos recebidos pela incrível banda de piratas animatrônicos inspirada no Capitão Jack Sparrow! Eles tocam instrumentos musicais ao lado de navios gigantes e batalhas navais interativas com canhões de água!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (5).mp4", "start": 0.5, "dur": 8.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (8).mp4", "start": 1.0, "dur": 8.5}
        ]
    },
    {
        "scene_id": "11_parada_ninjago_world",
        "badge": "PARADA 8: LEGO NINJAGO® WORLD 🥷",
        "topic": "TREINAMENTO & TEMPLO 4D",
        "narration": "Nossa próxima estação é o LEGO Ninjago World! Aqui os visitantes entram no templo sagrado oriental, treinam os reflexos ninja e encaram uma batalha interativa em Quatro D com sensores de movimento que lançam poderes com as mãos!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (2).mp4", "start": 0.5, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (1).mp4", "start": 0.5, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (7).mp4", "start": 0.5, "dur": 6.0}
        ]
    },
    {
        "scene_id": "12_parada_knights_kingdom",
        "badge": "PARADA 9: KNIGHT'S KINGDOM 🏰",
        "topic": "CASTELO & MONTANHA-RUSSA DO DRAGÃO",
        "narration": "Ao lado da ferrovia ergue-se o imponente castelo de Knight's Kingdom! É aqui que fica o Dragon Coaster, uma montanha-russa radical que percorre as câmaras secretas do castelo medieval e o covil de um dragão gigante!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (11).mp4", "start": 0.5, "dur": 9.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (4).mp4", "start": 0.5, "dur": 6.5}
        ]
    },
    {
        "scene_id": "13_parada_polar_land",
        "badge": "PARADA 10: POLAR LAND & GELO 🧊",
        "topic": "EXPEDIÇÕES POLARES & SPLASH ZONE",
        "narration": "Cruzamos agora a fria Polar Land e a Caverna de Gelo! Uma zona com esculturas em tamanho real de pinguins e ursos polares, além de atrações aquáticas refrescantes perfeitas para os dias ensolarados!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46.mp4", "start": 1.0, "dur": 8.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (1).mp4", "start": 0.5, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (3).mp4", "start": 2.0, "dur": 4.5}
        ]
    },
    {
        "scene_id": "14_retorno_estacao_conclusao",
        "badge": "CHEGADA NA ESTAÇÃO CENTRAL 🌟",
        "topic": "FIM DO TOUR NO LEGOLAND EXPRESS",
        "narration": "O trem completa seu circuito passando pela autoescola infantil Trafikskolen e retorna suavemente à estação central! O que você achou desse passeio sobre trilhos pela Legoland Billund? Comente abaixo, compartilhe este vídeo e inscreva-se no canal Rota Calculada para mais aventuras pelo mundo!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 165.0, "dur": 10.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 230.0, "dur": 9.0}
        ]
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
            await asyncio.sleep(1.5)

    try:
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(out_path)
    except Exception as e:
        print(f"Erro TTS: {e}")

def prepare_subclip_9_16(v_path: Path, st: float, dur: float, w_t=1080, h_t=1920, keepalive=None) -> VideoFileClip:
    raw = VideoFileClip(str(v_path))
    if keepalive is not None:
        keepalive.append(raw)

    max_avail = max(0.1, raw.duration - st)
    actual_dur = min(dur, max_avail)
    sub = raw.subclipped(st, st + actual_dur)

    vw, vh = sub.w, sub.h
    aspect_t = 9 / 16.0
    aspect_v = vw / float(vh)

    if aspect_v > aspect_t:
        new_w = int(vh * aspect_t)
        crop_x = (vw - new_w) // 2
        v_crop = sub.cropped(x1=crop_x, width=new_w, y1=0, height=vh)
    else:
        new_h = int(vw / aspect_t)
        crop_y = (vh - new_h) // 2
        v_crop = sub.cropped(x1=0, width=vw, y1=crop_y, height=new_h)

    return v_crop.resized((w_t, h_t))

def produce_train_journey_movie():
    print("==================================================================")
    print(" [PRODUZINDO VÍDEO LONGO: O TOUR SOBRE TRILHOS NA LEGOLAND 🚂🧱] ")
    print("==================================================================")

    w_t, h_t = 1080, 1920

    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 36)
        font_topic = ImageFont.truetype("arialbd.ttf", 44)
        font_canal = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        font_badge = ImageFont.load_default()
        font_topic = ImageFont.load_default()
        font_canal = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    long_video_clips = []
    long_audio_clips = []
    long_raw_keepalive = []
    long_time = 0.0

    for idx, sc in enumerate(LEGOLAND_TRAIN_JOURNEY_SCENES, 1):
        scene_id = sc["scene_id"]
        badge_text = sc["badge"]
        topic_text = sc["topic"]
        narration = sc["narration"]
        v_clips_def = sc.get("video_clips", [])

        voice_file = audio_dir / f"voice_{idx:02d}_{scene_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.35

        scene_parts = []
        tot_dur_planned = sum(v_info.get("dur", 5.0) for v_info in v_clips_def)
        scale_factor = target_dur / float(tot_dur_planned) if tot_dur_planned > 0 else 1.0

        for v_info in v_clips_def:
            v_fname = v_info["file"]
            v_st = v_info.get("start", 0.0)
            v_dur = v_info.get("dur", 5.0) * scale_factor
            v_path = legoland_dir / v_fname
            if not v_path.exists():
                v_path = list(legoland_dir.glob("*.mp4"))[0]

            sub_clip = prepare_subclip_9_16(v_path, v_st, v_dur, w_t, h_t, long_raw_keepalive)
            scene_parts.append(sub_clip)

        if len(scene_parts) > 1:
            joined_scene = concatenate_videoclips(scene_parts)
        else:
            joined_scene = scene_parts[0]

        if joined_scene.duration < target_dur:
            joined_scene = joined_scene.with_effects([vfx.Loop(duration=target_dur)])
        else:
            joined_scene = joined_scene.subclipped(0, target_dur)

        # Dynamic overlay with station badges and train theme
        def create_scene_overlay(b_txt, t_txt, sc_idx, total_sc):
            def overlay_func(get_frame, t):
                frame = get_frame(t)
                frame_pil = Image.fromarray(frame)
                draw = ImageDraw.Draw(frame_pil)

                # Cabeçalho Superior Fixo
                draw.rectangle([(0, 70), (1080, 160)], fill=(0, 0, 0, 185))
                draw.text((540, 115), "ROTA CALCULADA | EXPRESSO LEGOLAND 🚂🧱", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

                # Placa de Destaque da Estação / Parada (Primeiros 5.5 segundos de cada cena)
                if t < 5.5:
                    draw.rectangle([(0, 240), (1080, 430)], fill=(0, 0, 0, 220))
                    draw.rectangle([(0, 240), (25, 430)], fill=(255, 215, 0))
                    draw.text((540, 300), f"[{sc_idx:02d}/{total_sc}] {b_txt}", fill=(255, 215, 0), font=font_badge, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
                    draw.text((540, 370), t_txt, fill=(255, 255, 255), font=font_topic, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

                # Moldura Dourada Cinematográfica
                draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
                return np.array(frame_pil)
            return overlay_func

        final_scene_clip = joined_scene.transform(create_scene_overlay(badge_text, topic_text, idx, len(LEGOLAND_TRAIN_JOURNEY_SCENES))).with_start(long_time)
        long_video_clips.append(final_scene_clip)

        long_audio_clips.append(voice_clip.with_start(long_time).with_volume_scaled(1.7))
        long_time += target_dur

        print(f"  ✓ Parada {idx:02d}/{len(LEGOLAND_TRAIN_JOURNEY_SCENES)}: [{badge_text}] | Duração: {target_dur:.1f}s | Acumulado: {long_time:.1f}s ({long_time/60.0:.2f} min)")

    v_long_comp = CompositeVideoClip(long_video_clips).with_duration(long_time)

    # Trilha sonora de fundo sincronizada e em loop
    bgm_p = base_dir / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_p.exists():
        raw_bgm = AudioFileClip(str(bgm_p))
        bgm_duration = raw_bgm.duration
        loops_needed = int(long_time // bgm_duration) + 1
        bgm_clips = []
        for i in range(loops_needed):
            st = i * bgm_duration
            if st < long_time:
                dur = min(bgm_duration, long_time - st)
                bgm_clips.append(raw_bgm.subclipped(0, dur).with_start(st).with_volume_scaled(0.10))
        
        long_audio_clips.extend(bgm_clips)

    comp_a_long = CompositeAudioClip(long_audio_clips)
    v_long_final = v_long_comp.with_audio(comp_a_long).with_duration(long_time)

    # Thumbnail da capa do vídeo do trem
    first_frame = Image.fromarray(v_long_final.get_frame(2.0))
    first_frame.save(artifacts_dir / "legoland_expresso_trem_thumb.png", format="PNG")
    first_frame.save(output_long_dir / "legoland_expresso_trem_thumb.png", format="PNG")

    master_path = output_long_dir / "legoland_billund_expresso_trem_FINAL_MOVIE.mp4"
    temp_aud = str(output_long_dir / f"temp_audio_train_{run_id}.m4a")

    print(f"\n[RENDERIZANDO VÍDEO DO PASSEIO DE TREM: {long_time:.1f}s ({long_time/60.0:.2f} min)]...")
    v_long_final.write_videofile(
        str(master_path),
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        threads=4,
        temp_audiofile=temp_aud,
        remove_temp=True,
        fps=24,
        logger=None
    )

    v_long_final.close()
    comp_a_long.close()
    for c in long_video_clips:
        c.close()
    for a in long_audio_clips:
        a.close()
    for v in long_raw_keepalive:
        v.close()

    print(f"\n🎉 [VÍDEO DO PASSEIO DE TREM NA LEGOLAND CONCLUÍDO COM SUCESSO!]")
    print(f"  - Duração Final: {long_time:.1f}s ({long_time/60.0:.2f} minutos)")
    print(f"  - Arquivo: {master_path}")

if __name__ == "__main__":
    produce_train_journey_movie()
