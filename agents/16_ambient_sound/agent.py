import os
import sys
import wave
import struct
import math
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


def generate_sfx_wav(filepath: Path, duration_sec: float = 3.0, freq: float = 80.0):
    sample_rate = 22050
    n_samples = int(sample_rate * duration_sec)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(filepath), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            # Ruído grave / eco de túnel foley
            value = int(4000 * math.sin(2 * math.pi * freq * i / sample_rate) * math.exp(-i / (sample_rate * 1.5)))
            data = struct.pack("<h", value)
            wav_file.writeframesraw(data)


class AmbientSoundAgent(BaseAgent):
    name = "16_ambient_sound"
    input_stream = "stream:audio_music"
    output_stream = "stream:audio_sfx"

    def process(self, payload: dict) -> dict:
        self.logger.info("Adicionando efeitos sonoros de ambiente e Foley (SFX)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])
        new_scenes = []

        audio_dir = Path(__file__).resolve().parents[2] / "output" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        for scene in scenes:
            new_scene = scene.copy()
            scene_id = scene.get("scene_id", 1)
            duration = scene.get("duration_sec", 4.0)

            sfx_path = audio_dir / f"{job_id}_sfx_scene_{scene_id}.wav"
            generate_sfx_wav(sfx_path, duration_sec=duration, freq=60.0 + (scene_id * 20.0))

            new_scene["sfx_audio_path"] = str(sfx_path)
            new_scene["sfx_type"] = "underground_tunnel_echo"
            new_scene["sfx_volume_db"] = -18
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["ambient_sfx_added"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = AmbientSoundAgent(host=host)
    agent.run_forever()
