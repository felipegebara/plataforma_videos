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
from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent
legohouse_dir = base_dir / "legohouse"
output_shorts_dir = base_dir / "output" / "videos" / "legohouse_shorts"
audio_dir = base_dir / "output" / "audio" / "legohouse_suite"
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\8289ff40-6fee-4bc8-a053-70c64e03f4f7")

output_shorts_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
artifacts_dir.mkdir(parents=True, exist_ok=True)

# 17 SHORTS VIRAIS COBRINDO 100% DO ACERVO DA LEGO HOUSE (13-17s)
LEGOHOUSE_SHORTS_DEFINITIONS = [
    {
        "short_id": "short_legohouse_01",
        "title": "O T-Rex que Pisou no Lego 🦖",
        "hook": "ATÉ O T-REX GRITA DE DOR NO LEGO! 🦖",
        "narration": "Você sabia que até o Tiranossauro Rex sofre ao pisar numa peça de Lego? Na Masterpiece Gallery da Lego House, este dinossauro verde gigante ruge de dor após pisar descalço num bloco vermelho! A cena é uma das piadas mais famosas do mundo!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.26 (1).mp4", "start": 0.5, "dur": 6.5},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.26.mp4", "start": 0.5, "dur": 7.5}
        ]
    },
    {
        "short_id": "short_legohouse_02",
        "title": "O Dinossauro Robótico de Technic ⚙️",
        "hook": "O DINOSSAURO DE MOTORES E ENGRENAGENS! ⚙️",
        "narration": "Olha a complexidade desta obra-prima! Este dinossauro colossal foi construído com quase trezentas mil peças de Lego Technic, incluindo engrenagens, pistões e motores mecânicos ao lado de um ovo gigante prestes a chocar!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.25 (1).mp4", "start": 0.5, "dur": 8.5}
        ]
    },
    {
        "short_id": "short_legohouse_03",
        "title": "A Maior Cachoeira de Lego do Mundo 🌊",
        "hook": "A MAIOR CACHOEIRA DE LEGO DO MUNDO! 🌊",
        "narration": "Na Red Zone da Lego House fica esta cascata colossal com mais de dois milhões de peças que parecem escorrer do teto como água líquida! Os blocos multicoloridos caem direto em piscinas infinitas onde visitantes do mundo todo podem construir!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.22 (1).mp4", "start": 0.5, "dur": 8.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.22.mp4", "start": 0.5, "dur": 6.0}
        ]
    },
    {
        "short_id": "short_legohouse_04",
        "title": "O Vulcão Ativo com Lava de Lego 🌋",
        "hook": "O VULCÃO DE LEGO EM ERUPÇÃO! 🌋",
        "narration": "No coração da maquete tropical de World Explorer, este vulcão imenso solta fumaça real e jorra rios de lava feitos com blocos translúcidos iluminados por dentro! Uma obra épica cercada por florestas tropicais e parques de diversão!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.20.mp4", "start": 0.5, "dur": 11.0}
        ]
    },
    {
        "short_id": "short_legohouse_05",
        "title": "A Montanha Nevada e o Castelo Secreto 🏔️",
        "hook": "O CASTELO SECRETO NO TOPO DO GELO! 🏔️",
        "narration": "Uma cadeia de montanhas alpinas esculpida em Lego com pistas de esqui, teleféricos e túneis ferroviários! No topo dos picos rochosos ergue-se um castelo de conto de fadas medieval com iluminação mágica e vilarejos nórdicos nos vales!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.20 (3).mp4", "start": 0.5, "dur": 4.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.21 (2).mp4", "start": 0.5, "dur": 5.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.21.mp4", "start": 0.5, "dur": 3.5}
        ]
    },
    {
        "short_id": "short_legohouse_06",
        "title": "A Metrópole Urbana de Skyscrappers 🏙️",
        "hook": "A CIDADE VIVA DE ARRANHA-CÉUS! 🏙️",
        "narration": "Esta maquete urbana colossal recria uma metrópole moderna com arranha-céus gigantescos, metrô subterrâneo em movimento, quadras de tênis nos terraços e milhares de minifiguras vivendo seu dia a dia com iluminação noturna dinâmica!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.20 (2).mp4", "start": 1.0, "dur": 14.5}
        ]
    },
    {
        "short_id": "short_legohouse_07",
        "title": "Robôs Exploradores no Gelo Ártico 🤖",
        "hook": "PROGRAME SEU PRÓPRIO ROBÔ DE LEGO! 🤖",
        "narration": "No Robo Lab da Blue Zone, você assume o controle de veículos robóticos autônomos no Ártico! Os visitantes usam programação por blocos para guiar os robôs pelo gelo e resgatar mamutes e pesquisadores congelados!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.21 (1).mp4", "start": 0.5, "dur": 5.2},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.19 (3).mp4", "start": 0.5, "dur": 7.0}
        ]
    },
    {
        "short_id": "short_legohouse_08",
        "title": "O Rosto Misterioso em Mosaico 3D 🎭",
        "hook": "A OBRA DE ARTE MAIS INSANA DE LEGO! 🎭",
        "narration": "Olhe bem de perto: esta obra de arte monumental utiliza milhares de pecinhas, ferramentas e acessórios aleatórios de Lego em camadas tridimensionais para formar um rosto humano expressionista com profundidade hiper-realista!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.25.mp4", "start": 1.0, "dur": 14.0}
        ]
    },
    {
        "short_id": "short_legohouse_09",
        "title": "Guitarras e Sintetizadores em Tamanho Real 🎸",
        "hook": "INSTRUMENTOS DE VERDADE FEITOS DE LEGO? 🎸",
        "narration": "Na Masterpiece Gallery, artistas adultos de Lego recriaram guitarras lendárias como a Fender Stratocaster e a Gibson Les Paul em escala real! Cada tarracha, captador e até o teclado sintetizador foram moldados com precisão milimétrica!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.23.mp4", "start": 0.5, "dur": 10.0}
        ]
    },
    {
        "short_id": "short_legohouse_10",
        "title": "O Quadro de Museu em Relevo 3D 🎨",
        "hook": "O QUADRO QUE SALTOU DA MOLDURA! 🎨",
        "narration": "Este quadro clássico de tosquia de ovelhas foi totalmente transformado numa escultura tridimensional de Lego! A lã das ovelhas e a moldura barroca dourada saltam para fora do vidro, misturando pintura a óleo com engenharia de blocos!",
        "media_sequence": [
            {"type": "image", "file": "WhatsApp Image 2026-08-31 at 22.03.24.jpeg", "dur": 7.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.23 (1).mp4", "start": 0.5, "dur": 7.5}
        ]
    },
    {
        "short_id": "short_legohouse_11",
        "title": "O Cofre dos Sets Mais Raros da História 🏛️",
        "hook": "O COFRE SECRETO DOS SETS MAIS RAROS! 🏛️",
        "narration": "No subsolo da Lego House fica a History Collection, um cofre blindado que guarda todos os sets históricos já fabricados! Desde o foguete Apollo Saturn V e o Yellow Submarine dos Beatles até relíquias clássicas dos anos setenta e oitenta!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 21.57.13.mp4", "start": 0.5, "dur": 6.8},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.19.mp4", "start": 0.5, "dur": 7.5}
        ]
    },
    {
        "short_id": "short_legohouse_12",
        "title": "A Evolução do Primeiro Minifigure de 1974 👥",
        "hook": "COMO ERA O 1º BONECO DE LEGO EM 1974? 👥",
        "narration": "Você sabia que os primeiros bonecos de Lego não tinham braços nem pernas móveis? Esta vitrine histórica mostra a evolução desde as primeiras figuras primitivas de 1974 até o nascimento da icônica minifigura amarela com rostinho feliz em 1978!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.19 (2).mp4", "start": 0.5, "dur": 5.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.19 (1).mp4", "start": 0.5, "dur": 7.2}
        ]
    },
    {
        "short_id": "short_legohouse_13",
        "title": "O Tigre de Bengala Hiper-Realista 🐅",
        "hook": "O TIGRE DE LEGO MAIS REALISTA DO MUNDO! 🐅",
        "narration": "Criado por mestres de montagem, este Tigre de Bengala esculpido em Lego possui musculatura anatômica e articulações perfeitas! Ele espreita sobre rochas detalhadas sob galhos de cerejeira em flor com impressionante realismo!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.25 (2).mp4", "start": 0.5, "dur": 7.5}
        ]
    },
    {
        "short_id": "short_legohouse_14",
        "title": "A Pagoda Japonesa e as Cerejeiras Sakura 🏯",
        "hook": "O TEMPLO JAPONÊS ESCULPIDO EM LEGO! 🏯",
        "narration": "Uma tradicional pagoda oriental de três andares cercada por cerejeiras de sakura e pontes curvas sobre lagos zen! Cada telhado curvado e ornamento dourado foi construído utilizando técnicas avançadas de encaixe de peças!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.24.mp4", "start": 1.0, "dur": 13.5}
        ]
    },
    {
        "short_id": "short_legohouse_15",
        "title": "A Parede Gigante de Pixel Art & Emojis 👾",
        "hook": "A PAREDE DE EMOJIS E PIXEL ART! 👾",
        "narration": "Centenas de pequenos quadros de pixel art feitos com plaquinhas de Lego cobrem esta parede colossal! De emojis e personagens de videogame até heróis de quadrinhos e retratos criativos desenhados por visitantes do mundo inteiro!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.19 (3).mp4", "start": 0.5, "dur": 7.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.21 (1).mp4", "start": 0.5, "dur": 5.0}
        ]
    },
    {
        "short_id": "short_legohouse_16",
        "title": "O Aspirador que Engole Bonecos de Lego 🧹",
        "hook": "O ASPIRADOR QUE DEVORA BONECOS! 🧹",
        "narration": "Quem nunca teve medo de aspirar uma peça de Lego por engano? Esta escultura surrealista em tamanho real mostra um aspirador de pó transparente sugando dezenas de minifiguras em pânico! Uma crítica hilária e criativa à vida real!",
        "media_sequence": [
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.23 (2).mp4", "start": 0.5, "dur": 14.5}
        ]
    },
    {
        "short_id": "short_legohouse_17",
        "title": "Crie Criaturas Vivas no Aquário Digital 🐟",
        "hook": "SUA CRIAÇÃO GANHA VIDA NO AQUÁRIO! 🐟",
        "narration": "Na Yellow Zone da Lego House, você constrói seu próprio peixe ou monstro marinho com blocos coloridos, coloca na esteira do scanner óptico e vê sua criação ganhar vida instantaneamente nadando num aquário digital gigante!",
        "media_sequence": [
            {"type": "image", "file": "WhatsApp Image 2026-08-31 at 22.03.22.jpeg", "dur": 7.0},
            {"type": "video", "file": "WhatsApp Video 2026-08-31 at 22.03.20 (1).mp4", "start": 5.0, "dur": 7.5}
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

def create_animated_image_clip(img_path: Path, dur: float, w_t=1080, h_t=1920) -> ImageClip:
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

def produce_all_legohouse_shorts(target_short_id=None):
    print("==================================================================")
    print(f" [PRODUZINDO SUÍTE DE SHORTS: LEGO HOUSE BILLUND 🧱 ({'TODOS' if not target_short_id else target_short_id})] ")
    print("==================================================================")

    w_t, h_t = 1080, 1920

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 46)
        font_canal = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font_hook = ImageFont.load_default()
        font_canal = ImageFont.load_default()

    run_id = int(time.time() * 1000)

    shorts_to_process = [s for s in LEGOHOUSE_SHORTS_DEFINITIONS if target_short_id is None or s["short_id"] == target_short_id or target_short_id in s["short_id"]]

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
                v_path = legohouse_dir / v_fname
                if not v_path.exists():
                    v_path = list(legohouse_dir.glob("*.mp4"))[0]
                sub_clip = prepare_subclip_9_16(v_path, v_st, m_dur, w_t, h_t, raw_keepalive)
                scene_parts.append(sub_clip)
            elif m_type == "image":
                i_fname = m_info["file"]
                i_path = legohouse_dir / i_fname
                if not i_path.exists():
                    i_path = list(legohouse_dir.glob("*.jpeg"))[0]
                img_clip = create_animated_image_clip(i_path, m_dur, w_t, h_t)
                scene_parts.append(img_clip)

        if len(scene_parts) > 1:
            joined_scene = concatenate_videoclips(scene_parts)
        else:
            joined_scene = scene_parts[0]

        if joined_scene.duration < target_dur:
            joined_scene = joined_scene.with_effects([vfx.Loop(duration=target_dur)])
        else:
            joined_scene = joined_scene.subclipped(0, target_dur)

        # Dynamic overlay with 2-second viral hook and channel badge
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
            draw.text((540, 120), "ROTA CALCULADA | LEGO HOUSE 🧱", fill=(255, 255, 255), font=font_canal, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

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
            audio_mix.append(bgm.with_volume_scaled(0.10))

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

    print(f"\n🎉 [SUÍTE DE 17 SHORTS DA LEGO HOUSE CONCLUÍDA COM SUCESSO!]")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    produce_all_legohouse_shorts(target)
