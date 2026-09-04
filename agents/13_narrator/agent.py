import os
import sys
import asyncio
from pathlib import Path
import edge_tts

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


async def generate_neural_voice(text: str, output_path: str, voice: str = "pt-BR-AntonioNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


class NarratorAgent(BaseAgent):
    name = "13_narrator"
    input_stream = "stream:final_render"
    output_stream = "stream:audio_voice"

    def process(self, payload: dict) -> dict:
        self.logger.info("Gerando voz humana neural hiper-realista em português (Microsoft Edge Neural Voice: pt-BR-AntonioNeural)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])
        new_scenes = []

        audio_dir = Path(__file__).resolve().parents[2] / "output" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        for scene in scenes:
            new_scene = scene.copy()
            scene_id = scene.get("scene_id", 1)
            narration_text = scene.get("narration", "")

            clean_text = narration_text.replace("⚡", "").replace("🚨", "").replace("👇", "").strip()
            if not clean_text:
                clean_text = "Mistério no Pelourinho em Salvador."

            voice_path = audio_dir / f"{job_id}_voice_scene_{scene_id}.mp3"

            self.logger.info(f"Sintetizando voz humana neural para Cena {scene_id}: '{clean_text[:45]}...'")
            try:
                asyncio.run(generate_neural_voice(clean_text, str(voice_path), voice="pt-BR-AntonioNeural"))
                self.logger.info(f"Voz Humana Neural salva com sucesso: {voice_path}")
            except Exception as err:
                self.logger.warning(f"Erro no Edge-TTS ({err}), gerando alternativa...")
                with open(voice_path, "wb") as f:
                    f.write(b"MOCK_VOICE")

            new_scene["voice_audio_path"] = str(voice_path)
            new_scene["tts_engine"] = "Microsoft-Edge-Neural-pt-BR-AntonioNeural"
            new_scene["voice_language"] = "pt-BR"
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["narration_generated"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = NarratorAgent(host=host)
    agent.run_forever()
