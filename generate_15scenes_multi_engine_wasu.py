import os
import sys
import json
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
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


def engine1_wikimedia(query: str, out_path: Path) -> bool:
    """ENGINE 1: Wikimedia Commons 1280px HD Real Photo API."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}
    encoded_term = urllib.parse.quote(query)
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_term}&gsrlimit=6&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get("imageinfo", [])
                if imageinfo:
                    img_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                    if img_url and any(img_url.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                        img_req = urllib.request.Request(img_url, headers=headers)
                        with urllib.request.urlopen(img_req, timeout=12) as i_resp:
                            with open(out_path, "wb") as f:
                                f.write(i_resp.read())
                        print(f"    [ENGINE 1 - Wikimedia] Foto HD obtida: '{query}'")
                        return True
    except Exception:
        pass
    return False


def engine2_unsplash(query: str, out_path: Path) -> bool:
    """ENGINE 2: Unsplash Source Public Domain HD Photo Search."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    encoded_term = urllib.parse.quote(query)
    img_url = f"https://source.unsplash.com/1080x1920/?{encoded_term}"
    
    try:
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    [ENGINE 2 - Unsplash] Foto HD obtida: '{query}'")
                return True
    except Exception:
        pass
    return False


def engine3_pollinations(prompt: str, seed_id: int, out_path: Path) -> bool:
    """ENGINE 3: Pollinations AI High-Quality Image Engine."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    enc_p = urllib.parse.quote(prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{enc_p}?width=1080&height=1920&nologo=true&seed={8000 + seed_id}"
    
    try:
        req = urllib.request.Request(ai_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"    [ENGINE 3 - Pollinations AI] Imagem AI gerada com sucesso ({seed_id})")
                return True
    except Exception:
        pass
    return False


def engine4_procedural_canvas(scene_id: int, title_label: str, color_theme: tuple, out_path: Path):
    """ENGINE 4: High-End Procedural Canvas Engine with Cinematic Vignettes & Textured Lighting."""
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), color=color_theme)
    draw = ImageDraw.Draw(img)

    # Multi-layered textured gradient
    for y in range(h):
        factor = y / float(h)
        r = int(color_theme[0] * (1 - factor * 0.6) + 15 * factor)
        g = int(color_theme[1] * (1 - factor * 0.5) + 20 * factor)
        b = int(color_theme[2] * (1 - factor * 0.4) + 30 * factor)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Vignette Shadow
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([(0, 0), (w, h)], fill=(0, 0, 0, 0))
    s_draw.rectangle([(60, 60), (w - 60, h - 60)], fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(80))
    img.paste(shadow, (0, 0), shadow)

    # Moldura Dourada do Documentário
    draw = ImageDraw.Draw(img)
    draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)

    try:
        font = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        font = ImageFont.load_default()

    draw.text((540, 1780), f"CENA {scene_id}/15 - O MITO DE WASU (MUSA)", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    img.save(out_path, format="PNG")
    print(f"    [ENGINE 4 - Canvas HD] Imagem procedural texturizada criada para cena {scene_id}")


def get_best_image_multi_engine(sc: dict, images_dir: Path) -> Path:
    """Executa o pipeline de 4 Engines em sequência para garantir 100% imagens de altíssima qualidade."""
    scene_id = sc["scene_id"]
    query = sc["query"]
    fallback = sc["fallback"]
    prompt = sc["prompt"]
    theme = sc["theme"]

    raw_path = images_dir / f"raw_scene_{scene_id}.jpg"
    final_path = images_dir / f"scene_{scene_id}.png"

    print(f"  📸 [CENA {scene_id}/15] Buscando imagem no Pipeline Multi-Engine...")

    # Engine 1: Wikimedia Commons
    if engine1_wikimedia(query, raw_path) or engine1_wikimedia(fallback, raw_path):
        format_to_916_hd(raw_path, scene_id, final_path)
        return final_path

    # Engine 2: Unsplash
    if engine2_unsplash(query, raw_path) or engine2_unsplash(fallback, raw_path):
        format_to_916_hd(raw_path, scene_id, final_path)
        return final_path

    # Engine 3: Pollinations AI
    if engine3_pollinations(prompt, scene_id, raw_path):
        format_to_916_hd(raw_path, scene_id, final_path)
        return final_path

    # Engine 4: Procedural Canvas HD
    engine4_procedural_canvas(scene_id, sc["narration"][:30], theme, final_path)
    return final_path


def format_to_916_hd(raw_img_path: Path, scene_id: int, out_path: Path):
    """Formata qualquer imagem obtida para 9:16 HD 1080x1920 com crop perfeito e moldura."""
    w, h = 1080, 1920
    if not raw_img_path.exists():
        return

    try:
        img = Image.open(raw_img_path).convert("RGB")
        aspect_target = 9 / 16.0
        aspect_img = img.width / float(img.height)

        if aspect_img > aspect_target:
            new_w = int(img.height * aspect_target)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, img.height))
        else:
            new_h = int(img.width / aspect_target)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, img.width, top + new_h))

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(30, 30), (1050, 1890)], outline=(255, 215, 0), width=6)

        try:
            font = ImageFont.truetype("arialbd.ttf", 32)
        except Exception:
            font = ImageFont.load_default()

        draw.text((540, 1780), f"CENA {scene_id}/15 - O MITO DE WASU (MUSA)", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
        img.save(out_path, format="PNG")
    except Exception as e:
        pass


WASU_15_SCENES = [
    {
        "scene_id": 1,
        "narration": "Nas antigas e distantes terras do Rio Traíra, onde as águas cortam a floresta densa da Amazônia, vivia um ser lendário chamado Wasu.",
        "duration": 14.0,
        "motion": "zoom_in",
        "query": "Rio Uaupes Amazon river waterfall",
        "fallback": "Amazon river waterfall landscape",
        "prompt": "Vivid Amazonian watercolor painting, Rio Traira river with lush rainforest waterfalls, 9:16 vertical",
        "theme": (20, 45, 75)
    },
    {
        "scene_id": 2,
        "narration": "Wasu era um guerreiro solteirão e solitário. Ele passava seus dias subindo e descendo bravias cachoeiras, navegando de aldeia em aldeia em busca de uma esposa... mas nenhuma mulher aceitava viver com ele.",
        "duration": 15.0,
        "motion": "pan_left",
        "query": "Indigenous canoe Amazon river",
        "fallback": "Amazon river canoe paddle",
        "prompt": "Indigenous canoe paddling on Amazon river at dusk, watercolor painting, 9:16 vertical",
        "theme": (30, 50, 80)
    },
    {
        "scene_id": 3,
        "narration": "Triste e desiludido com a viagem frustrada, Wasu decidiu encostar sua canoa em um porto isolado na floresta — um local fascinante que hoje é conhecido como a Serra do Diabo sem Cu.",
        "duration": 15.0,
        "motion": "zoom_out",
        "query": "Serra do Diabo Amazon mountain",
        "fallback": "Amazon river port rainforest",
        "prompt": "Isolated Amazon river port surrounded by misty mountains, watercolor painting, 9:16 vertical",
        "theme": (45, 35, 20)
    },
    {
        "scene_id": 4,
        "narration": "Nesse porto distante morava sozinho seu primo, uma figura excentricamente famosa nas lendas regionais. Wasu decidiu pedir abrigo e ficar hospedado em sua casa por algum tempo.",
        "duration": 14.0,
        "motion": "pan_right",
        "query": "Indigenous maloca Amazon house",
        "fallback": "Indigenous village Amazon house",
        "prompt": "Traditional wooden maloca house in Amazon rainforest, watercolor painting, 9:16 vertical",
        "theme": (55, 40, 25)
    },
    {
        "scene_id": 5,
        "narration": "Não demorou para que Wasu notasse algo profundamente misterioso na rotina daquela casa. Sempre que o primo saía para beber caxiri em outras aldeias, barulhos suaves ecoavam do alto do jirau.",
        "duration": 15.0,
        "motion": "zoom_in",
        "query": "Amazonian indigenous wooden house interior",
        "fallback": "Indigenous maloca interior",
        "prompt": "Interior of traditional Amazon wooden house with wooden loft, watercolor painting, 9:16 vertical",
        "theme": (60, 45, 20)
    },
    {
        "scene_id": 6,
        "narration": "Curioso, Wasu subiu até o estrado de madeira e encontrou um grande baú trançado de palha. Ao abri-lo, para sua surpresa, uma mulher encantadora saiu de lá e começou a preparar deliciosos beijus!",
        "duration": 16.0,
        "motion": "pan_left",
        "query": "Indigenous woven basket Amazon",
        "fallback": "Amazonian indigenous craft basket",
        "prompt": "Beautiful indigenous woman stepping out of a woven straw chest, watercolor painting, 9:16 vertical",
        "theme": (70, 50, 30)
    },
    {
        "scene_id": 7,
        "narration": "Fascinado pela beleza e pelo carinho daquela mulher encantada, Wasu apaixonou-se no mesmo instante e começou a arquitetar um plano secreto para fugir com ela.",
        "duration": 14.0,
        "motion": "zoom_out",
        "query": "Amazonian indigenous woman portrait",
        "fallback": "Indigenous woman Amazon rainforest",
        "prompt": "Beautiful Amazonian indigenous woman in rainforest, mythic watercolor painting, 9:16 vertical",
        "theme": (65, 40, 35)
    },
    {
        "scene_id": 8,
        "narration": "Certo dia, o primo observou um costume de Wasu que jamais havia visto. O primo possuía um corpo diferente: seu sistema digestivo terminava bem embaixo de sua boca, sem qualquer saída posterior.",
        "duration": 16.0,
        "motion": "pan_right",
        "query": "Desana indigenous painting MUSA",
        "fallback": "Indigenous painting Amazon art",
        "prompt": "Desana indigenous mythology painting of mythic entity, MUSA style, 9:16 vertical",
        "theme": (25, 25, 40)
    },
    {
        "scene_id": 9,
        "narration": "Intrigado e invejoso, o primo perguntou: 'Meu amigo Wasu, como você consegue defecar por trás? Queria tanto ter um corpo igual ao seu...'",
        "duration": 14.0,
        "motion": "zoom_in",
        "query": "Amazonian indigenous man portrait",
        "fallback": "Indigenous man face painting",
        "prompt": "Indigenous man with curious expression in rainforest, watercolor painting, 9:16 vertical",
        "theme": (35, 30, 45)
    },
    {
        "scene_id": 10,
        "narration": "Enxergando a oportunidade perfeita para derrotar o primo e libertar a mulher do baú, Wasu mentiu astutamente: 'Foi meu pai quem fez essa abertura em mim usando varas da floresta! Não dói nada! Se você quiser, posso fazer em você agora mesmo!'",
        "duration": 18.0,
        "motion": "pan_left",
        "query": "Amazon rainforest plants reeds",
        "fallback": "Amazon rainforest jungle plants",
        "prompt": "Indigenous man collecting forest reeds in jungle, watercolor painting, 9:16 vertical",
        "theme": (30, 60, 35)
    },
    {
        "scene_id": 11,
        "narration": "Empolgado e ingênuo com a promessa, o primo aceitou na hora. Wasu então adentrou a floresta fechada e recolheu varas leves de arumã, além de selecionar sua lança-chocalho mais forte e afiada.",
        "duration": 17.0,
        "motion": "zoom_out",
        "query": "Indigenous spear Amazon weapon",
        "fallback": "Indigenous spear weapon Amazon",
        "prompt": "Indigenous warrior holding sharp wooden spear in Amazon forest, watercolor painting, 9:16 vertical",
        "theme": (45, 55, 25)
    },
    {
        "scene_id": 12,
        "narration": "Wasu pediu para o primo se agachar de costas e fechar os olhos. No início, usou as varas moles de arumã que se quebravam sem dor, enganando a confiança do primo. Mas logo em seguida... desferiu o golpe com sua lança resistente.",
        "duration": 17.0,
        "motion": "pan_right",
        "query": "Amazon rainforest dark jungle trail",
        "fallback": "Amazon forest shadow trees",
        "prompt": "Dramatic confrontation in Amazon forest, mythic watercolor painting, 9:16 vertical",
        "theme": (70, 35, 15)
    },
    {
        "scene_id": 13,
        "narration": "O primo não resistiu ao impacto mágico. Wasu então pegou os vestígios e as tripas do primo e os lançou nas águas correntes do rio. Em um piscar de olhos, um encanto poderoso aconteceu: as tripas ganharam vida e começaram a nadar!",
        "duration": 18.0,
        "motion": "zoom_in",
        "query": "Amazon river water current underwater",
        "fallback": "Amazon river water flow",
        "prompt": "Magical bioluminescent energy bursting into Amazon river water, watercolor painting, 9:16 vertical",
        "theme": (15, 65, 85)
    },
    {
        "scene_id": 14,
        "narration": "Nasceram assim diversas espécies de peixes compridos: o sarapó-cunuri, o sarapó-comprido e os ituins. É por causa desse mito ancestral que, na natureza, todos esses peixes da família Gymnotiformes possuem o ânus situado bem abaixo da cabeça!",
        "duration": 18.0,
        "motion": "pan_left",
        "query": "Gymnotus knife fish electric eel",
        "fallback": "Gymnotiformes knife fish Amazon",
        "prompt": "Group of electric knife fish Sarapos swimming in clear river, bioluminescent water, 9:16 vertical",
        "theme": (10, 80, 95)
    },
    {
        "scene_id": 15,
        "narration": "Esta rica narrativa dos povos Desana e Tuyuka, imortalizada nas telas do mestre Feliciano Lana e preservada pelo Museu da Amazônia (MUSA), une humor, biologia e o fascínio das histórias da nossa terra.",
        "duration": 16.0,
        "motion": "zoom_out",
        "query": "Museu da Amazonia MUSA Manaus",
        "fallback": "Amazon canopy tower MUSA",
        "prompt": "Museu da Amazonia MUSA exhibit with indigenous paintings, sunset rainforest view, 9:16 vertical",
        "theme": (50, 35, 20)
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


def produce_15scenes_multi_engine_video():
    topic_id = "mito_wasu_15cenas_multi_engine"
    print(f"\n==========================================")
    print(f"[VÍDEO MASTER 15 CENAS - MULTI-ENGINE FALLBACK] O Mito de Wasu (MUSA)")
    print(f"==========================================")

    output_dir = Path(__file__).resolve().parent / "output" / "videos" / topic_id
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    audio_dir = Path(__file__).resolve().parent / "output" / "audio" / topic_id

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_clips = []
    audio_clips = []
    current_time = 0.0

    for sc in WASU_15_SCENES:
        scene_id = sc["scene_id"]
        narration = sc["narration"]
        dur = sc["duration"]
        motion = sc["motion"]

        # Executar Pipeline de 4 Engines de Imagem
        img_path = get_best_image_multi_engine(sc, images_dir)

        # Estampar Título no 1º Frame
        if scene_id == 1 and img_path.exists():
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 240), (1080, 440)], fill=(0, 0, 0, 200))
            try:
                font = ImageFont.truetype("arialbd.ttf", 38)
            except Exception:
                font = ImageFont.load_default()

            line1 = "O MITO DE WASU E"
            line2 = "A ORIGEM DOS SARAPÓS (MUSA)"

            draw.text((540, 290), line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            draw.text((540, 370), line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
            img.convert("RGB").save(img_path)

        # Gerar Voz Humana Neural em Português
        voice_path = audio_dir / f"voice_scene_{scene_id}.mp3"
        asyncio.run(generate_voice(narration, str(voice_path)))

        # Renderizar Vídeo MP4 com Movimento OpenCV
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

        # Acoplar Clipes de Áudio e Vídeo
        v_clip = VideoFileClip(str(scene_mp4))
        voice_clip = AudioFileClip(str(voice_path)).with_start(current_time)
        voice_dur = voice_clip.duration + 0.1

        v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
        video_clips.append(v_clip)
        audio_clips.append(voice_clip.with_volume_scaled(1.5))

        current_time += voice_dur
        print(f"  [SCENE] Cena {scene_id}/15 renderizada ({voice_dur:.2f}s | Acumulado: {current_time:.1f}s)")

    # Adicionar Trilha BGM de Fundo
    bgm_path = Path(__file__).resolve().parent / "output" / "audio" / "bgm_tuneis_secretos_do_pelourinho.wav"
    if bgm_path.exists():
        raw_bgm = AudioFileClip(str(bgm_path))
        bgm_clip = raw_bgm.subclipped(0, min(current_time, raw_bgm.duration)).with_start(0).with_volume_scaled(0.12)
        audio_clips.append(bgm_clip)

    # Exportar Vídeo Master Final de 15 Cenas
    master_path = output_dir / f"{topic_id}_FINAL_MOVIE.mp4"
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

    print(f"[OK] VÍDEO MASTER DE 15 CENAS CONCLUÍDO COM SUCESSO ({current_time:.1f}s): {master_path}")
    return master_path


def main():
    produce_15scenes_multi_engine_video()


if __name__ == "__main__":
    main()
