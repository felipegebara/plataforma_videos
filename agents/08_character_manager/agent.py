import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class CharacterManagerAgent(BaseAgent):
    name = "08_character_manager"
    input_stream = "stream:prompts"
    output_stream = "stream:character_consistency"

    def process(self, payload: dict) -> dict:
        self.logger.info("Injetando âncoras e tags de consistência de personagem/estilo...")
        scenes = payload.get("scenes", [])
        new_scenes = []

        character_anchor = "<lora:antigravity_historian_v2:0.8>, 35yo mysterious investigator with leather jacket, dark eyes"

        for scene in scenes:
            new_scene = scene.copy()
            orig_prompt = scene.get("cinematic_prompt", "")
            
            # Injeta âncora visual de personagem
            new_scene["consistent_prompt"] = f"{character_anchor}, {orig_prompt}"
            new_scene["character_lora"] = "antigravity_historian_v2"
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["character_consistency_applied"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = CharacterManagerAgent(host=host)
    agent.run_forever()
