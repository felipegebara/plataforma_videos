import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import cv2
import numpy as np

# Adiciona a raiz do projeto ao path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    from shared.base_agent import BaseAgent
except Exception:
    class BaseAgent:
        def __init__(self, *args, **kwargs):
            import logging
            self.logger = logging.getLogger("ViralPackagingAgent")


class ViralPackagingAgent(BaseAgent):
    """
    Agente 19: Viral Packaging & High-CTR Optimizer.
    Gera automaticamente títulos de alta virilidade, thumbnails chamativas
    com inteligência de seleção de frames e descrições com hashtags (#) otimizadas.
    """
    name = "19_viral_packaging"
    input_stream = "stream:complete_movie"
    output_stream = "stream:packaged_video"

    def process(self, payload: dict) -> dict:
        video_path = payload.get("final_movie_with_audio") or payload.get("video_path")
        topic = payload.get("topic") or payload.get("title") or "Mistérios e Lendas Incríveis"
        narration = payload.get("narration") or payload.get("script") or ""
        format_type = payload.get("format_type", "short")
        category = payload.get("category", "MISTERY_HISTORY")

        self.logger.info(f"Gerando pacote viral para: '{topic}' ({format_type.upper()})...")

        package = create_viral_package(
            video_path=video_path,
            topic=topic,
            narration=narration,
            format_type=format_type,
            category=category,
            output_dir=Path(video_path).parent if video_path else None
        )

        new_payload = payload.copy()
        new_payload["viral_package"] = package
        new_payload["titles"] = package["titles"]
        new_payload["selected_title"] = package["titles"]["viral_curiosity"]
        new_payload["thumbnail_path"] = package["thumbnail_path"]
        new_payload["description"] = package["description"]
        new_payload["hashtags"] = package["hashtags"]
        return new_payload


# =====================================================================
# MOTOR DE TÍTULOS VIRAIS (ALGORITMO DE CTR)
# =====================================================================
def generate_viral_titles(topic: str, narration: str = "", format_type: str = "short") -> Dict[str, str]:
    """
    Gera 3 variantes estratégicas de títulos de alta conversão:
    1. Viral / Curiosity Gap (Maior CTR e retenção)
    2. High Stakes / Mistério (Impacto emocional)
    3. Search / SEO (Buscas orgânicas no YouTube)
    """
    clean_topic = topic.strip().title()

    # Detecta elementos-chave
    is_lego = "lego" in topic.lower()
    is_arabia = any(k in topic.lower() for k in ["arábia", "arabia", "aladim", "sinbad", "djinn", "scheherazade", "deserto"])
    is_historia = any(k in topic.lower() for k in ["brasil", "túneis", "guerra", "ouro", "segredo", "antigo"])

    if is_lego:
        viral_1 = f"O SEGREDO QUE NINGUÉM CONTOU SOBRE A LEGOLAND! 🧱"
        viral_2 = f"A Cidade Viva de 20 MILHÕES de Peças de Lego! 🇩🇰"
        seo = f"Legoland Billund: Guia Completo e Tour pelo Parque Original"
    elif is_arabia:
        viral_1 = f"A VERDADE SOMBRIA QUE ESCONDERAM SOBRE AS ARÁBIAS! 🌙"
        viral_2 = f"O Monstro das Dunas que Poucos Conhecem! 🦅"
        seo = f"Lendas das Mil e Uma Noites: Mitos e Mistérios do Oriente"
    else:
        viral_1 = f"O Segredo Obscuro de {clean_topic}! 😱"
        viral_2 = f"O Que Aconteceu em {clean_topic} Vai Te Chocar! ⚠️"
        seo = f"{clean_topic}: A História Completa e Segredos Revelados"

    # Ajusta para formato Short (< 55 caracteres)
    if format_type.lower() == "short":
        short_title = viral_1 if len(viral_1) <= 55 else viral_2
        if len(short_title) > 55:
            short_title = f"{clean_topic}: O Segredo Revelado! ⚠️"
    else:
        short_title = f"{viral_1} | {clean_topic}"

    return {
        "viral_curiosity": viral_1,
        "high_stakes": viral_2,
        "search_seo": seo,
        "recommended_short_title": short_title
    }


# =====================================================================
# MOTOR DE DESCRIÇÕES & HASHTAGS (#)
# =====================================================================
def generate_viral_description(topic: str, narration: str = "", format_type: str = "short") -> Dict[str, Any]:
    """
    Cria uma descrição magnética estruturada com gancho, resumo,
    pergunta para gerar comentários da comunidade e hashtags (#) estratégicas.
    """
    clean_topic = topic.strip()

    hashtags = [
        f"#{clean_topic.replace(' ', '')}",
        "#RotaCalculada",
        "#Curiosidades",
        "#Historia",
        "#Misterios",
        "#Viagem",
        "#FatosDesconhecidos",
        "#Shorts",
        "#YouTubeShorts",
        "#Viral"
    ]

    if "lego" in topic.lower():
        hashtags.extend(["#Legoland", "#LegolandBillund", "#LegoWorld", "#Dinamarca"])
    elif any(k in topic.lower() for k in ["arábia", "arabia", "aladim", "sinbad"]):
        hashtags.extend(["#MilEUmaNoites", "#Arabia", "#Mitologia", "#Deserto", "#LendasArabes"])

    hashtag_str = " ".join(hashtags[:10])

    if format_type.lower() == "short":
        desc = (
            f"🌟 Descubra o mistério por trás de {clean_topic} com o canal Rota Calculada!\n\n"
            f"👉 Você já conhecia essa história? Deixe sua opinião nos comentários!\n"
            f"🔔 Inscreva-se no canal para acompanhar mais expedições e lendas pelo mundo!\n\n"
            f"{hashtag_str}"
        )
    else:
        desc = (
            f"🗺️ Bem-vindo ao canal Rota Calculada! Hoje exploramos em detalhes todos os segredos e a história de {clean_topic}.\n\n"
            f"{narration[:200]}...\n\n"
            f"👇 Deixe nos comentários: O que mais te impressionou nessa história?\n\n"
            f"🔔 INSCREVA-SE NO ROTA CALCULADA e ative as notificações para mais conteúdos de história, turismo e mistérios!\n"
            f"👍 Deixe seu Like e compartilhe com seus amigos!\n\n"
            f"{hashtag_str}"
        )

    return {
        "description": desc,
        "hashtags": hashtags,
        "hashtag_string": hashtag_str
    }


# =====================================================================
# MOTOR DE THUMBNAILS DE ALTO CTR (FRAME INTELLIGENCE + DESIGN)
# =====================================================================
def extract_best_video_frame(video_path: str) -> np.ndarray:
    """
    Varre o vídeo buscando o frame com maior nitidez (Laplacian variance),
    contraste e riqueza visual para a melhor thumbnail.
    """
    resolved_path = str(Path(video_path).resolve())
    try:
        from moviepy import VideoFileClip
        clip = VideoFileClip(resolved_path)
        dur = clip.duration
        sample_points = np.linspace(max(0.5, 0.1 * dur), min(dur - 0.5, 0.9 * dur), min(12, max(3, int(dur))))
        best_frame = None
        best_score = -1.0

        for sec in sample_points:
            try:
                frame_rgb = clip.get_frame(sec)
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
                sat_mean = np.mean(hsv[:, :, 1])
                val_std = np.std(hsv[:, :, 2])
                score = lap_var * 0.4 + sat_mean * 1.5 + val_std * 2.0

                if score > best_score:
                    best_score = score
                    best_frame = frame_bgr.copy()
            except Exception:
                continue

        clip.close()
        if best_frame is not None:
            return best_frame
    except Exception:
        pass

    cap = cv2.VideoCapture(resolved_path)
    if not cap.isOpened():
        return np.zeros((1920, 1080, 3), dtype=np.uint8)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / fps if fps else 0
    best_frame = None

    for sec in np.linspace(1.0, max(1.0, dur - 1.0), 8):
        cap.set(cv2.CAP_PROP_POS_MSEC, int(sec * 1000))
        ret, frame = cap.read()
        if ret and frame is not None:
            best_frame = frame.copy()
            break
    cap.release()
    return best_frame if best_frame is not None else np.zeros((1920, 1080, 3), dtype=np.uint8)


def generate_high_ctr_thumbnail(
    image_input: Any,
    topic: str,
    output_path: Path,
    format_type: str = "short",
    custom_badge: Optional[str] = None
) -> str:
    """
    Gera uma thumbnail profissional de alta conversão:
    - Realce de contraste e saturação
    - Vinheta escura de borda para foco no assunto principal
    - Tipografia bold com stroke grosso e amarelo ouro (#FFD700)
    - Selo de autoridade do canal Rota Calculada
    """
    if isinstance(image_input, (str, Path)):
        if str(image_input).endswith(".mp4"):
            frame_np = extract_best_video_frame(str(image_input))
            # Converte BGR para RGB
            frame_rgb = cv2.cvtColor(frame_np, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
        else:
            img_pil = Image.open(str(image_input)).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        img_pil = Image.fromarray(image_input)
    else:
        img_pil = image_input

    # Define dimensões
    if format_type.lower() == "short":
        w_t, h_t = 1080, 1920
    else:
        w_t, h_t = 1920, 1080

    # Crop e redimensionamento proporcional
    aspect_t = w_t / float(h_t)
    aspect_img = img_pil.width / float(img_pil.height)

    if aspect_img > aspect_t:
        new_w = int(img_pil.height * aspect_t)
        left = (img_pil.width - new_w) // 2
        img_pil = img_pil.crop((left, 0, left + new_w, img_pil.height))
    else:
        new_h = int(img_pil.width / aspect_t)
        top = (img_pil.height - new_h) // 2
        img_pil = img_pil.crop((0, top, img_pil.width, top + new_h))

    img_pil = img_pil.resize((w_t, h_t), Image.Resampling.LANCZOS)

    # 1. REALCE DE SATURAÇÃO E CONTRASTE (POPPING COLORS)
    enhancer_sat = ImageEnhance.Color(img_pil)
    img_pil = enhancer_sat.enhance(1.25)

    enhancer_con = ImageEnhance.Contrast(img_pil)
    img_pil = enhancer_con.enhance(1.15)

    # 2. APLICA VINHETA SUAVE E GRADIENTE ESCURO NO TOPO E BASE
    draw = ImageDraw.Draw(img_pil)

    # Fontes
    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 52 if format_type == "short" else 72)
        font_sub = ImageFont.truetype("arialbd.ttf", 36 if format_type == "short" else 48)
        font_badge = ImageFont.truetype("arialbd.ttf", 28 if format_type == "short" else 36)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Badge de topo do canal
    if format_type == "short":
        draw.rectangle([(0, 80), (1080, 160)], fill=(0, 0, 0, 190))
        draw.text((540, 120), "ROTA CALCULADA 🌟", fill=(255, 255, 255), font=font_badge, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

        # Texto viral central / inferior
        hook_text = custom_badge or topic.upper()
        if len(hook_text) > 30:
            words = hook_text.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])

            draw.rectangle([(0, 320), (1080, 520)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 320), (25, 520)], fill=(255, 215, 0))
            draw.text((540, 380), line1, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
            draw.text((540, 460), line2, fill=(255, 255, 255), font=font_hook, anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
        else:
            draw.rectangle([(0, 340), (1080, 480)], fill=(0, 0, 0, 220))
            draw.rectangle([(0, 340), (25, 480)], fill=(255, 215, 0))
            draw.text((540, 410), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))

        # Borda Dourada
        draw.rectangle([(20, 20), (1060, 1900)], outline=(255, 215, 0), width=6)

    else:
        # Formato 16:9 Horizontal
        draw.rectangle([(0, 50), (1920, 140)], fill=(0, 0, 0, 190))
        draw.text((960, 95), "ROTA CALCULADA | DOCUMENTÁRIO OFICIAL 🌟", fill=(255, 255, 255), font=font_badge, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

        hook_text = custom_badge or topic.upper()
        draw.rectangle([(0, 780), (1920, 980)], fill=(0, 0, 0, 220))
        draw.rectangle([(0, 780), (35, 980)], fill=(255, 215, 0))
        draw.text((960, 880), hook_text, fill=(255, 215, 0), font=font_hook, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))

        # Borda Dourada
        draw.rectangle([(25, 25), (1895, 1055)], outline=(255, 215, 0), width=8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_pil.save(str(output_path), format="PNG", quality=95)
    return str(output_path)


# =====================================================================
# FUNÇÃO PRINCIPAL DE EMBALAGEM VIRAL
# =====================================================================
def create_viral_package(
    video_path: Optional[str] = None,
    topic: str = "Mistérios do Mundo",
    narration: str = "",
    format_type: str = "short",
    category: str = "MISTERY_HISTORY",
    output_dir: Optional[Path] = None,
    custom_hook_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função tudo-em-um para criar o pacote viral completo:
    1. Títulos de alto CTR
    2. Thumbnail de alto contraste e legibilidade
    3. Descrição com hashtags (#)
    """
    titles = generate_viral_titles(topic=topic, narration=narration, format_type=format_type)
    desc_info = generate_viral_description(topic=topic, narration=narration, format_type=format_type)

    out_dir = Path(output_dir) if output_dir else Path(project_root) / "output" / "thumbnails"
    out_dir.mkdir(parents=True, exist_ok=True)

    clean_name = topic.lower().replace(" ", "_").replace(":", "").replace("!", "").replace("?", "")[:30]
    thumb_file = out_dir / f"thumb_{clean_name}_{format_type}.png"

    if video_path and Path(video_path).exists():
        thumb_path = generate_high_ctr_thumbnail(
            image_input=video_path,
            topic=custom_hook_text or titles["viral_curiosity"],
            output_path=thumb_file,
            format_type=format_type
        )
    else:
        # Se não houver vídeo fornecido, cria com imagem gerada/placeholder
        blank = Image.new("RGB", (1080, 1920) if format_type == "short" else (1920, 1080), (25, 25, 30))
        thumb_path = generate_high_ctr_thumbnail(
            image_input=blank,
            topic=custom_hook_text or titles["viral_curiosity"],
            output_path=thumb_file,
            format_type=format_type
        )

    return {
        "topic": topic,
        "format_type": format_type,
        "titles": titles,
        "selected_title": titles["recommended_short_title"] if format_type == "short" else titles["viral_curiosity"],
        "thumbnail_path": str(thumb_path),
        "description": desc_info["description"],
        "hashtags": desc_info["hashtags"],
        "hashtag_string": desc_info["hashtag_string"]
    }


# =====================================================================
# CLI RUNNER
# =====================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente 19 - Viral Packaging & Thumbnail Generator")
    parser.add_argument("--video", type=str, help="Caminho do arquivo de vídeo")
    parser.add_argument("--topic", type=str, default="Mistérios da Legoland", help="Tópico ou assunto do vídeo")
    parser.add_argument("--narration", type=str, default="", help="Texto da narração")
    parser.add_argument("--format", type=str, choices=["short", "long"], default="short", help="Formato (short ou long)")
    parser.add_argument("--hook", type=str, default=None, help="Texto personalizado para a thumbnail")

    args = parser.parse_args()

    pkg = create_viral_package(
        video_path=args.video,
        topic=args.topic,
        narration=args.narration,
        format_type=args.format,
        custom_hook_text=args.hook
    )

    print("\n==================================================")
    print(" 🎉 PACOTE VIRAL GERADO COM SUCESSO! 🎉")
    print("==================================================")
    print(f"📌 Título Viral 1 (Curiosidade): {pkg['titles']['viral_curiosity']}")
    print(f"📌 Título Viral 2 (Impacto):     {pkg['titles']['high_stakes']}")
    print(f"📌 Título 3 (SEO / Busca):       {pkg['titles']['search_seo']}")
    print(f"🖼️ Thumbnail de Alto CTR:       {pkg['thumbnail_path']}")
    print(f"🏷️ Hashtags (#):                 {pkg['hashtag_string']}")
    print("==================================================\n")
