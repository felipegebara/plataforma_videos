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
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, concatenate_videoclips, vfx

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent
arabia_dir = base_dir / "arabia"
illustrations_dir = base_dir / "output" / "images" / "arabia_illustrations"
output_shorts_dir = base_dir / "output" / "videos" / "arabia_shorts"
audio_dir = base_dir / "output" / "audio" / "arabia_suite"
artifacts_dir = Path(r"C:\Users\fgeba\\.gemini\antigravity\brain\8289ff40-6fee-4bc8-a053-70c64e03f4f7")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir.mkdir(parents=True, exist_ok=True)
illustrations_dir.mkdir(parents=True, exist_ok=True)

# 10 SHORTS VIRAIS COMBINANDO ESCULTURAS DE AREIA REAIS + ILUSTRAÇÕES HISTÓRICAS E MITOLÓGICAS DA WEB (14-17s)
ARABIA_SHORTS_DEFINITIONS = [
    {
        "short_id": "short_arabia_1",
        "title": "O Segredo da Caverna de Aladim 🪔",
        "hook": "O SEGREDO DA CAVERNA DE ALADIM! 🪔",
        "narration": "Nas Mil e Uma Noites originais, a lâmpada mágica ficava escondida numa caverna amaldiçoada que engolia quem tentasse roubá-la! Esta escultura monumental recria o momento em que o gênio colossal é despertado após séculos de prisão sob as dunas!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.55 (1).mp4", "start": 1.0, "dur": 5.5},
            {"type": "image", "file": "arabia_1_aladdin_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.57 (2).mp4", "start": 3.0, "dur": 6.4}
        ]
    },
    {
        "short_id": "short_arabia_2",
        "title": "Como Sinbad Escapou do Pássaro Roc 🦅",
        "hook": "COMO SINBAD ESCAPOU DO PÁSSARO GIGANTE? 🦅",
        "narration": "Preso numa ilha deserta, Sinbad o Marujo descobriu um ninho colossal e amarrou seu turbante nas garras do lendário Pássaro Roc para fugir voando! A criatura mitológica era tão imensa que caçava elefantes inteiros para alimentar seus filhotes!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.58 (2).mp4", "start": 0.5, "dur": 5.5},
            {"type": "image", "file": "arabia_2_roc_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.58.mp4", "start": 1.0, "dur": 6.0}
        ]
    },
    {
        "short_id": "short_arabia_3",
        "title": "A Origem Oculta dos Djinns 🧞‍♂️",
        "hook": "A ORIGEM OCULTA DOS GÊNIOS ÁRABES! 🧞‍♂️",
        "narration": "Muito antes do homem existir, as lendas árabes contam que a Terra pertencia aos Djinns, seres místicos criados a partir do fogo puro! Capazes de mudar de forma e conceder desejos perigosos, eles viviam aprisionados sob as areias do deserto!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.54 (1).mp4", "start": 0.5, "dur": 5.5},
            {"type": "image", "file": "arabia_3_djinn_1.jpg", "dur": 5.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.54.mp4", "start": 2.0, "dur": 6.4}
        ]
    },
    {
        "short_id": "short_arabia_4",
        "title": "Sinbad e a Caverna do Gigante 👁️",
        "hook": "O PESADELO NA CAVERNA DO GIGANTE! 👁️",
        "narration": "Na terceira viagem de Sinbad, sua tripulação foi capturada por um gigante canibal dentro de uma caverna amaldiçoada! Para não ser devorado vivo, o marujo forjou ferros incandescentes para cegar o monstro e escapar pelo mar!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.57.mp4", "start": 0.5, "dur": 5.0},
            {"type": "image", "file": "arabia_4_cyclops_2.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.55.29.mp4", "start": 2.0, "dur": 5.8}
        ]
    },
    {
        "short_id": "short_arabia_5",
        "title": "O Sacrifício de Scheherazade 📜",
        "hook": "ELA SALVOU AS MULHERES DO REINO! 📜",
        "narration": "O sultão vingativo executava uma noiva a cada amanhecer. Para deter a matança, a sábia Scheherazade casou-se com o rei e narrou contos fascinantes por mil e uma noites, parando sempre no clímax ao nascer do sol para impedir sua própria morte!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.53.mp4", "start": 0.5, "dur": 5.0},
            {"type": "image", "file": "arabia_5_scheherazade_1.jpg", "dur": 5.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.57 (3).mp4", "start": 1.0, "dur": 5.7}
        ]
    },
    {
        "short_id": "short_arabia_6",
        "title": "Os Cavaleiros Temidos das Dunas 🐎",
        "hook": "OS CAVALEIROS MAIS TEMIDOS DAS DUNAS! 🐎",
        "narration": "Os guerreiros beduínos consideravam seus cavalos puro-sangue como dádivas sagradas do vento sul! Capazes de cruzar tempestades de areia sem parar, eles realizavam ataques-relâmpago devastadores que nenhum exército conseguia prever!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.56.mp4", "start": 0.5, "dur": 5.0},
            {"type": "image", "file": "arabia_6_bedouin_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.56 (2).mp4", "start": 0.5, "dur": 6.0}
        ]
    },
    {
        "short_id": "short_arabia_7",
        "title": "A Cidade Perdida de Iram 🏙️",
        "hook": "A ATLÂNTIDA ESCONDIDA SOB A AREIA! 🏙️",
        "narration": "A lenda árabe de Iram das Colunas fala de uma cidade suntuosa com palácios dourados que foi engolida pelo deserto em uma única noite de tempestade! Esta escultura monumental representa a mística metrópole surgindo entre os ventos e dunas!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.58 (1).mp4", "start": 1.0, "dur": 5.0},
            {"type": "image", "file": "arabia_7_iram_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.58.mp4", "start": 1.0, "dur": 5.9}
        ]
    },
    {
        "short_id": "short_arabia_8",
        "title": "A Serpente Cósmica Falak 🐍",
        "hook": "A SERPENTE QUE PODIA ENGOLIR O MUNDO! 🐍",
        "narration": "Nos mitos árabes das Mil e Uma Noites, a serpente cósmica Falak habita as profundezas mais escuras da Terra! Ela é tão colossal e faminta que as antigas lendas diziam que seu veneno e suas mandíbulas podiam devorar o próprio planeta!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.55.31.mp4", "start": 0.5, "dur": 5.0},
            {"type": "image", "file": "arabia_8_falak_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.55.29.mp4", "start": 12.0, "dur": 6.2}
        ]
    },
    {
        "short_id": "short_arabia_9",
        "title": "O Corcel Celestial Al-Buraq 🪽",
        "hook": "O CORCEL QUE VOAVA NA VELOCIDADE DA LUZ! 🪽",
        "narration": "Al-Buraq era o lendário corcel alado de luz do Oriente Médio, cujo nome significa relâmpago! A criatura mágica conseguia dar um passo até onde o horizonte humano alcançava, transportando sábios entre os mundos celestiais!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.57 (2).mp4", "start": 1.0, "dur": 5.0},
            {"type": "image", "file": "arabia_9_buraq_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.57 (3).mp4", "start": 1.0, "dur": 5.7}
        ]
    },
    {
        "short_id": "short_arabia_10",
        "title": "O Mistério do Mar de Areia ⛵",
        "hook": "O OCEANO DE AREIA QUE ENGOLIA VIAJANTES! ⛵",
        "narration": "Os povos antigos chamavam as dunas do deserto de 'Mar de Areia', um oceano escaldante onde viajantes enfrentavam miragens, monstros subterrâneos e tempestades mortais em busca de sabedoria e relíquias sagradas!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.59.mp4", "start": 1.0, "dur": 5.0},
            {"type": "image", "file": "arabia_10_sandsea_1.jpg", "dur": 4.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-27 at 09.57.53 (1).mp4", "start": 0.5, "dur": 4.3}
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

def create_animated_illustration_clip(img_path: Path, dur: float, w_t=1080, h_t=1920) -> ImageClip:
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
    img_np = np.array(img_pil)

    base_clip = ImageClip(img_np).with_duration(dur)

    def pan_zoom_effect(get_frame, t):
        prog = t / float(dur) if dur > 0 else 0
        scale = 1.0 + 0.12 * prog
        nw, nh = int(w_t * scale), int(h_t * scale)
        f_res = cv2.resize(img_np, (nw, nh), interpolation=cv2.INTER_CUBIC)
        sx = int((nw - w_t) * 0.5)
        sy = int((nh - h_t) * 0.5)
        return f_res[sy : sy + h_t, sx : sx + w_t].copy()

    return base_clip.transform(pan_zoom_effect)

def produce_all_arabia_shorts(target_short_id=None):
    print("==================================================================")
    print(f" [PRODUZINDO SHORTS HÍBRIDOS: VÍDEOS DE AREIA + ILUSTRAÇÕES DA WEB 🌙 ({'TODOS' if not target_short_id else target_short_id})] ")
    print("==================================================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_canal = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font_hook = ImageFont.load_default()
        font_canal = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    shorts_to_process = [s for s in ARABIA_SHORTS_DEFINITIONS if target_short_id is None or s["short_id"] == target_short_id or target_short_id in s["short_id"]]

    for idx, sdef in enumerate(shorts_to_process, 1):
        short_id = sdef["short_id"]
        title = sdef["title"]
        hook_text = sdef["hook"]
        narration = sdef["narration"]
        media_seq = sdef.get("media_sequence", [])

        voice_file = audio_dir / f"voice_{short_id}_{run_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_file)))
        voice_clip = AudioFileClip(str(voice_file))
        target_dur = voice_clip.duration + 0.35

        raw_keepalive = []
        scene_parts = []
        tot_dur_planned = sum(m.get("dur", 5.0) for m in media_seq)
        scale_factor = target_dur / float(tot_dur_planned) if tot_dur_planned > 0 else 1.0

        for m_info in media_seq:
            m_type = m_info.get("type", "video")
            m_dur = m_info.get("dur", 5.0) * scale_factor

            if m_type == "video":
                v_fname = m_info["file"]
                v_st = m_info.get("start", 0.0)
                v_path = arabia_dir / v_fname
                if not v_path.exists():
                    v_path = list(arabia_dir.glob("*.mp4"))[0]
                sub_clip = prepare_subclip_9_16(v_path, v_st, m_dur, w_t, h_t, raw_keepalive)
                scene_parts.append(sub_clip)
            elif m_type == "image":
                i_fname = m_info["file"]
                i_path = illustrations_dir / i_fname
                if not i_path.exists():
                    i_path = list(illustrations_dir.glob("*.jpg"))[0]
                img_clip = create_animated_illustration_clip(i_path, m_dur, w_t, h_t)
                scene_parts.append(img_clip)

        if len(scene_parts) > 1:
            joined_scene = concatenate_videoclips(scene_parts)
        else:
            joined_scene = scene_parts[0]

        if joined_scene.duration < target_dur:
            joined_scene = joined_scene.with_effects([vfx.Loop(duration=target_dur)])
        else:
            joined_scene = joined_scene.subclipped(0, target_dur)

        # Dynamic overlay with 2-second hook and channel badge
        def add_short_overlay(get_frame, t):
            frame = get_frame(t)
            frame_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(frame_pil)

            # Hook nos primeiros 2.5 segundos (impacto viral)
            if t < 2.5:
                draw.rectangle([(0, 260), (1080, 440)], fill=(0, 0, 0, 230))
                draw.rectangle([(0, 260), (20, 440)], fill=(255, 215, 0))
                draw.text((540, 350), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

            # Barra do canal no topo
            draw.rectangle([(0, 80), (1080, 160)], fill=(0, 0, 0, 170))
            draw.text((540, 120), "ROTA CALCULADA | LENDAS DAS ARÁBIAS 🌙", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

            # Borda Dourada
            draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=5)
            return np.array(frame_pil)

        v_final = joined_scene.transform(add_short_overlay)

        # Trilha de fundo
        bgm_p = base_dir / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
        audio_mix = [voice_clip.with_start(0).with_volume_scaled(1.7)]

        if bgm_p.exists():
            bgm = AudioFileClip(str(bgm_p))
            if bgm.duration < target_dur:
                bgm = bgm.with_effects([vfx.Loop(duration=target_dur)])
            else:
                bgm = bgm.subclipped(0, target_dur)
            audio_mix.append(bgm.with_volume_scaled(0.11))

        comp_a = CompositeAudioClip(audio_mix)
        v_final = v_final.with_audio(comp_a).with_duration(target_dur)

        # Salva thumbnail
        thumb_frame = Image.fromarray(v_final.get_frame(1.2))
        thumb_path = output_shorts_dir / f"{short_id}_thumb.png"
        thumb_frame.save(thumb_path, format="PNG")
        thumb_frame.save(artifacts_dir / f"{short_id}_thumb.png", format="PNG")

        master_path = output_shorts_dir / f"{short_id}_FINAL_MOVIE.mp4"
        temp_aud = str(output_shorts_dir / f"temp_audio_{short_id}_{run_id}.m4a")

        print(f"[{idx:02d}/{len(shorts_to_process)}] Renderizando {short_id} ({title}) | {target_dur:.1f}s...")
        v_final.write_videofile(
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

        v_final.close()
        comp_a.close()
        for c in scene_parts:
            c.close()
        for v in raw_keepalive:
            v.close()

        print(f"  ✓ Concluído: {master_path} ({target_dur:.1f}s)")

    print(f"\n🎉 [SUÍTE DE SHORTS HÍBRIDOS CONCLUÍDA COM SUCESSO!]")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    produce_all_arabia_shorts(target)
