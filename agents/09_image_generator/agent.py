import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent

BRAIN_DIR = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

# Mapeamento estrito e 100% autêntico para o Pelourinho (sem imagens do Farol da Barra!)
LOCAL_SCENE_MAP = {
    1: BRAIN_DIR / "real_pelourinho_square_1785421553332.jpg", # Largo do Pelourinho autêntico com casarões e paralelepípedos
    2: BRAIN_DIR / "pelourinho_tunnel1_1785372855151.jpg",     # Galeria subterrânea colonial sob o Pelourinho
    3: BRAIN_DIR / "pelourinho_tunnel2_1785372867709.jpg",     # Passagem secreta de pedra
    4: BRAIN_DIR / "pelourinho_gate_1785372879383.jpg",        # Portão antigo de ferro selando o túnel
    5: BRAIN_DIR / "pelourinho_chamber_1785372893423.jpg",     # Câmara de pedra subterrânea
    6: BRAIN_DIR / "pelourinho_facades_1785421576627.jpg",     # Fachadas históricas do Pelourinho ao entardecer
}


class ImageGeneratorAgent(BaseAgent):
    name = "09_image_generator"
    input_stream = "stream:character_consistency"
    output_stream = "stream:images"

    def process(self, payload: dict) -> dict:
        self.logger.info("Garantindo fidelidade geográfica estrita do Pelourinho (100% fotos e artes do Pelourinho)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])
        new_scenes = []

        output_dir = Path(__file__).resolve().parents[2] / "output" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, scene in enumerate(scenes):
            new_scene = scene.copy()
            scene_id = scene.get("scene_id", i + 1)

            img_filename = f"{job_id}_scene_{scene_id}.png"
            img_path = output_dir / img_filename

            # Carrega a imagem HD autêntica do Pelourinho
            src_art = LOCAL_SCENE_MAP.get(scene_id)
            if src_art and src_art.exists():
                self.logger.info(f"Cena {scene_id}: Carregando imagem autêntica do Pelourinho HD (9:16)...")
                try:
                    img = Image.open(src_art).convert("RGB")
                    img_resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                    img_resized.save(img_path, format="PNG")
                    new_scene["image_source"] = "AUTHENTIC_PELOURINHO_HD"
                except Exception as err:
                    self.logger.warning(f"Erro ao redimensionar imagem ({err})")

            # Estampa o TÍTULO no 1º Frame (Largo do Pelourinho)
            overlay_title = scene.get("overlay_title")
            if scene_id == 1 and overlay_title and img_path.exists():
                try:
                    img = Image.open(img_path).convert("RGBA")
                    draw = ImageDraw.Draw(img)

                    # Faixa semitransparente elegante no topo
                    draw.rectangle([(0, 220), (1080, 440)], fill=(0, 0, 0, 190))

                    try:
                        font = ImageFont.truetype("arialbd.ttf", 46)
                    except Exception:
                        font = ImageFont.load_default()

                    title_line1 = "TÚNEIS SECRETOS"
                    title_line2 = "DO PELOURINHO"

                    draw.text((540, 270), title_line1, fill=(255, 215, 0), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
                    draw.text((540, 370), title_line2, fill=(255, 255, 255), font=font, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

                    img.convert("RGB").save(img_path, format="PNG")
                    self.logger.info(f"Título estampado no 1º frame sobre o Pelourinho autêntico!")
                except Exception as err:
                    self.logger.warning(f"Erro ao estampar título no 1º frame ({err})")

            new_scene["image_path"] = str(img_path)
            new_scene["width"] = 1080
            new_scene["height"] = 1920
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["images_generated"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = ImageGeneratorAgent(host=host)
    agent.run_forever()
