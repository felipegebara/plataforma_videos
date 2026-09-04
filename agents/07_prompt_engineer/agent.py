import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class PromptEngineerAgent(BaseAgent):
    name = "07_prompt_engineer"
    input_stream = "stream:scenes"
    output_stream = "stream:prompts"

    def process(self, payload: dict) -> dict:
        self.logger.info("Transformando cenas em prompts cinemáticos de ambientes sem pessoas...")
        scenes = payload.get("scenes", [])
        new_scenes = []

        for scene in scenes:
            new_scene = scene.copy()
            base_prompt = scene.get("visual_prompt", "")
            
            # Expansão de prompt com reforço de ausência de pessoas
            new_scene["cinematic_prompt"] = (
                f"{base_prompt}, no people, empty deserted location, architectural photography, 8k resolution, "
                "cinematic composition, hyperrealistic, masterpiece, award winning cinematography, volumetric lighting"
            )
            new_scene["negative_prompt"] = "people, person, human, crowd, face, man, woman, silhouette, blurry, low quality, deformed, text, watermark"
            new_scene["lighting_style"] = "Chiaroscuro Volumetric Lighting"
            new_scene["aspect_ratio"] = "9:16"
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["prompts_generated"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = PromptEngineerAgent(host=host)
    agent.run_forever()
