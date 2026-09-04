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
audio_dir = base_dir / "output" / "audio" / "legoland_extended_doc"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\8289ff40-6fee-4bc8-a053-70c64e03f4f7")

output_long_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir.mkdir(parents=True, exist_ok=True)

# 17 CENAS DETALHADAS COBRINDO TODAS AS ÁREAS DA LEGOLAND BILLUND (> 3.5 MINUTOS)
LEGOLAND_EXTENDED_DOC_SCENES = [
    {
        "scene_id": "01_intro_billund",
        "badge": "BEM-VINDO A BILLUND 🇩🇰",
        "topic": "A CAPITAL MUNDIAL DO LEGO",
        "narration": "Seja muito bem-vindo a Billund, na Dinamarca, a capital mundial dos blocos de montar e o berço sagrado da Lego! Neste documentário especial do canal Rota Calculada, você vai fazer um tour completo e detalhado pelo primeiro e mais icônico parque Legoland do planeta.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.46.18.mp4", "start": 0.5, "dur": 4.5},
            {"file": "WhatsApp Video 2026-08-12 at 18.46.21.mp4", "start": 0.5, "dur": 6.5},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (3).mp4", "start": 0.5, "dur": 4.0}
        ]
    },
    {
        "scene_id": "02_historia_fundacao",
        "badge": "HISTÓRIA & ORIGEM 🧱",
        "topic": "FUNDAÇÃO EM 1968",
        "narration": "Tudo começou quando Ole Kirk Christiansen fundou a Lego na década de trinta, inspirando-se na expressão dinamarquesa 'Leg Godt', que significa brincar bem. Em mil novecentos e sessenta e oito, seu filho Godtfred inaugurou este parque monumental exatamente ao lado da fábrica original para receber fãs do mundo inteiro.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 5.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "03_miniland_visao_geral",
        "badge": "MINILAND 🏙️",
        "topic": "O CORAÇÃO DO PARQUE",
        "narration": "O coração pulsante e a atração mais famosa da Legoland é a lendária Miniland! Um universo fascinante construído inteiramente com mais de vinte milhões de peças Lego em escala de um para vinte, recriando cidades inteiras com um nível de realismo inacreditável.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44.mp4", "start": 1.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "04_miniland_copenhague",
        "badge": "MINILAND: COPENHAGUE 🇩🇰",
        "topic": "PORTO DE NYHAVN & CANAIS",
        "narration": "Entre as réplicas mais deslumbrantes da Miniland está Copenhague, com o famoso porto de Nyhavn. Mais de três milhões de pecinhas foram usadas para esculpir os edifícios históricos coloridos, pontes levadiças e os navios mercantes que navegam em águas de verdade.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (6).mp4", "start": 1.0, "dur": 14.5}
        ]
    },
    {
        "scene_id": "05_miniland_aeroporto",
        "badge": "MINILAND: AEROPORTO ✈️",
        "topic": "AEROPORTO DE BILLUND",
        "narration": "Outro prodígio da engenharia do parque é a réplica exata do Aeroporto Internacional de Billund. Aviões comerciais e jatos executivos taxiam pelas pistas em movimento contínuo, acionados por motores elétricos de precisão e sistemas sincronizados.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (5).mp4", "start": 2.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "06_miniland_vida_rural",
        "badge": "MINILAND: VILA RURAL 🚜",
        "topic": "MOINHOS E FAZENDAS NÓRDICAS",
        "narration": "A área rural da Miniland retrata vilarejos nórdicos tradicionais. Moinhos de vento clássicos giram com a brisa, tratores cultivam os campos e celeiros artesanais abrigam dezenas de animais de fazenda esculpidos tijolo por tijolo.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (7).mp4", "start": 1.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "07_miniland_canais_eclusas",
        "badge": "MINILAND: ENGENHARIA 🚤",
        "topic": "CANAIS E ECLUSAS REAIS",
        "narration": "A hidrovia da Miniland conta com um complexo sistema de eclusas aquáticas reais. As embarcações sobem e descem os níveis da água automaticamente enquanto atravessam canais navegáveis cercados por vegetação real podada no estilo bonsai.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (3).mp4", "start": 2.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "08_miniland_transito_inteligente",
        "badge": "MINILAND: TRÂNSITO 🚗",
        "topic": "VEÍCULOS ELÉTRICOS AUTÔNOMOS",
        "narration": "O dinamismo urbano impressiona qualquer um: carros, ônibus e caminhões circulam pelas ruas parando nos semáforos e faixas de pedestres. Esse tráfego autônomo é controlado por cabos condutores subterrâneos que guiam cada mini veículo.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (4).mp4", "start": 2.0, "dur": 15.0}
        ]
    },
    {
        "scene_id": "09_pirate_land_banda",
        "badge": "PIRATE LAND 🏴‍☠️",
        "topic": "BANDA DO JACK SPARROW",
        "narration": "Ao entrar em Pirate Land, somos recebidos pela divertida banda de piratas animatrônicos de Lego inspirada no Capitão Jack Sparrow! Eles tocam instrumentos musicais e cantam canções marítimas, criando uma energia contagiante para os visitantes.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.44 (5).mp4", "start": 0.5, "dur": 14.5}
        ]
    },
    {
        "scene_id": "10_pirate_land_batalhas",
        "badge": "PIRATE LAND: AVENTURA 🏴‍☠️",
        "topic": "SHOWS & BATALHAS NAVAIS",
        "narration": "A zona dos piratas também oferece navios temáticos gigantescos, cavernas secretas com baús repletos de ouro e atrações com canhões de água interativos onde crianças e adultos podem participar de autênticas batalhas navais!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (8).mp4", "start": 1.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "11_ninjago_world",
        "badge": "LEGO NINJAGO® WORLD 🥷",
        "topic": "TEMPLO DOS ELEMENTOS",
        "narration": "Em LEGO Ninjago World, a experiência ganha ares de artes marciais orientais. Aqui os visitantes treinam seus reflexos no templo sagrado e encaram uma atração interativa em Quatro D com sensores de movimento que permitem lançar poderes ninja com as próprias mãos!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (2).mp4", "start": 0.5, "dur": 5.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (1).mp4", "start": 0.5, "dur": 4.5},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (7).mp4", "start": 0.5, "dur": 5.5}
        ]
    },
    {
        "scene_id": "12_knights_kingdom_dragao",
        "badge": "KNIGHT'S KINGDOM 🏰",
        "topic": "DRAGON COASTER MEDIEVAL",
        "narration": "No Reino dos Cavaleiros, ergue-se um imponente castelo medieval guardado por sentinelas de Lego. O grande destaque é o Dragon Coaster, uma montanha-russa eletrizante que mergulha nas profundezas do castelo e no covil de um dragão gigante!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (11).mp4", "start": 0.5, "dur": 10.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (4).mp4", "start": 0.5, "dur": 6.0}
        ]
    },
    {
        "scene_id": "13_polar_land_caverna_gelo",
        "badge": "POLAR LAND & GELO 🧊",
        "topic": "EXPEDIÇÕES ÁRTICAS & SPLASH",
        "narration": "Na área Polar Land e na Caverna de Gelo, exploramos expedições polares com esculturas em tamanho real de pinguins e animais árticos. Para os dias mais quentes, as Splash Zones garantem diversão refrescante com brinquedos aquáticos interativos.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46.mp4", "start": 1.0, "dur": 10.0},
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (1).mp4", "start": 0.5, "dur": 4.5}
        ]
    },
    {
        "scene_id": "14_miniland_cruise_monumentos",
        "badge": "MINILAND CRUISE 🚤",
        "topic": "MARAVILHAS DO MUNDO",
        "narration": "Um dos passeios mais relaxantes do parque é o Miniland Cruise. Embarcando em pequenas balsas elétricas, navegamos por canais que passam ao lado de monumentos mundiais como a Estátua da Liberdade, palácios asiáticos e templos históricos.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.45 (3).mp4", "start": 2.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "15_imersao_panoramica",
        "badge": "IMERSÃO NO PARQUE 🌳",
        "topic": "ARQUITETURA & EXPERIÊNCIA",
        "narration": "Caminhar pela Legoland Billund é uma verdadeira viagem sensorial. Cada alameda, restaurante temático e praça é planejado para unir gerações em torno da arte do Lego, transformando blocos plásticos em arquitetura de nível internacional.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 50.0, "dur": 15.5}
        ]
    },
    {
        "scene_id": "16_dicas_viagem_rota_calculada",
        "badge": "DICAS DE VIAGEM 🇩🇰",
        "topic": "COMO VISITAR A LEGOLAND",
        "narration": "Se você planeja viajar para a Dinamarca, nossa recomendação é reservar ao menos um dia inteiro para explorar o parque com tranquilidade. Billund fica a cerca de duas horas e meia de Copenhague e possui hotéis temáticos incríveis ao redor da Legoland.",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (6).mp4", "start": 1.0, "dur": 16.0}
        ]
    },
    {
        "scene_id": "17_encerramento_comunidade",
        "badge": "ROTA CALCULADA 🌟",
        "topic": "DEBATE & INSCRIÇÃO",
        "narration": "A Legoland nos ensina que a criatividade humana não tem limites. Você já visitou ou sonha em conhecer a Legoland na Dinamarca? Deixe sua história nos comentários, compartilhe este vídeo com seus amigos e inscreva-se no canal Rota Calculada para não perder os próximos destinos!",
        "video_clips": [
            {"file": "WhatsApp Video 2026-08-12 at 18.49.46 (8).mp4", "start": 130.0, "dur": 17.0}
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

def produce_extended_documentary():
    print("==================================================================")
    print(" [PRODUZINDO DOCUMENTÁRIO COMPLETO E ESTENDIDO DA LEGOLAND > 3 MIN] ")
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

    for idx, sc in enumerate(LEGOLAND_EXTENDED_DOC_SCENES, 1):
        scene_id = sc["scene_id"]
        badge_text = sc["badge"]
        topic_text = sc["topic"]
        narration = sc["narration"]
        v_clips_def = sc.get("video_clips", [])

        voice_file = audio_dir / f"voice_scene_{idx:02d}_{scene_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.35

        # Prepara a sequência de vídeos da cena
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

        # Se faltar tempo para cobrir a voz, estende com vfx.Loop de forma segura
        if joined_scene.duration < target_dur:
            joined_scene = joined_scene.with_effects([vfx.Loop(duration=target_dur)])
        else:
            joined_scene = joined_scene.subclipped(0, target_dur)

        # Overlay dinâmico e elegante para cada cena
        def create_scene_overlay(b_txt, t_txt, sc_idx, total_sc):
            def overlay_func(get_frame, t):
                frame = get_frame(t)
                frame_pil = Image.fromarray(frame)
                draw = ImageDraw.Draw(frame_pil)

                # Cabeçalho Superior Fixo
                draw.rectangle([(0, 70), (1080, 160)], fill=(0, 0, 0, 180))
                draw.text((540, 115), "ROTA CALCULADA | GUIA COMPLETO LEGOLAND 🧱", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

                # Placa de Destaque da Área (Primeiros 5.5 segundos de cada cena)
                if t < 5.5:
                    draw.rectangle([(0, 240), (1080, 430)], fill=(0, 0, 0, 220))
                    draw.rectangle([(0, 240), (25, 430)], fill=(255, 215, 0))
                    draw.text((540, 300), f"[{sc_idx:02d}/{total_sc}] {b_txt}", fill=(255, 215, 0), font=font_badge, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
                    draw.text((540, 370), t_txt, fill=(255, 255, 255), font=font_topic, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

                # Moldura Dourada Cinematográfica
                draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
                return np.array(frame_pil)
            return overlay_func

        final_scene_clip = joined_scene.transform(create_scene_overlay(badge_text, topic_text, idx, len(LEGOLAND_EXTENDED_DOC_SCENES))).with_start(long_time)
        long_video_clips.append(final_scene_clip)

        long_audio_clips.append(voice_clip.with_start(long_time).with_volume_scaled(1.7))
        long_time += target_dur

        print(f"  ✓ Cena {idx:02d}/{len(LEGOLAND_EXTENDED_DOC_SCENES)}: [{badge_text}] | Duração: {target_dur:.1f}s | Acumulado: {long_time:.1f}s ({long_time/60.0:.2f} min)")

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

    # Thumbnail da capa do vídeo longo
    first_frame = Image.fromarray(v_long_final.get_frame(2.0))
    first_frame.save(artifacts_dir / "legoland_guia_completo_thumb.png", format="PNG")
    first_frame.save(output_long_dir / "legoland_guia_completo_thumb.png", format="PNG")

    master_path = output_long_dir / "legoland_billund_master_doc_FINAL_MOVIE.mp4"
    guia_path = output_long_dir / "legoland_billund_guia_completo_FINAL_MOVIE.mp4"
    temp_aud = str(output_long_dir / f"temp_audio_ext_doc_{run_id}.m4a")

    print(f"\n[RENDERIZANDO VÍDEO FINAL: {long_time:.1f}s ({long_time/60.0:.2f} min)]...")
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

    # Salva também a cópia com nome amigável
    try:
        shutil.copy2(str(master_path), str(guia_path))
    except Exception:
        pass

    v_long_final.close()
    comp_a_long.close()
    for c in long_video_clips:
        c.close()
    for a in long_audio_clips:
        a.close()
    for v in long_raw_keepalive:
        v.close()

    print(f"\n🎉 [DOCUMENTÁRIO EXTENDIDO DA LEGOLAND CONCLUÍDO COM SUCESSO!]")
    print(f"  - Duração Final: {long_time:.1f}s ({long_time/60.0:.2f} minutos)")
    print(f"  - Arquivo Master: {master_path}")
    print(f"  - Arquivo Guia Completo: {guia_path}")

if __name__ == "__main__":
    produce_extended_documentary()
