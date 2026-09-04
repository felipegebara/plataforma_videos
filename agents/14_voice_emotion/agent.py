import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class VoiceEmotionAgent(BaseAgent):
    name = "14_voice_emotion"
    input_stream = "stream:audio_voice"
    output_stream = "stream:audio_emotion"

    def process(self, payload: dict) -> dict:
        self.logger.info("Aplicando modulação emocional e estilo à voz (Suspense/Empolgado)...")
        scenes = payload.get("scenes", [])
        new_scenes = []

        for scene in scenes:
            new_scene = scene.copy()
            section = scene.get("section", "BODY")

            # Aplica modulação de estilo emocional baseada na seção do roteiro
            if section == "HOOK":
                emotion_style = "suspense_intense"
                pitch_shift = "+1.2st"
            elif section == "CLIMAX":
                emotion_style = "dramatic_climax"
                pitch_shift = "+2.0st"
            elif section == "CTA":
                emotion_style = "enthusiastic_energetic"
                pitch_shift = "+0.5st"
            else:
                emotion_style = "mysterious_narrative"
                pitch_shift = "0.0st"

            new_scene["voice_emotion_style"] = emotion_style
            new_scene["pitch_shift"] = pitch_shift
            new_scene["emotion_applied"] = True
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["voice_emotion_complete"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = VoiceEmotionAgent(host=host)
    agent.run_forever()
