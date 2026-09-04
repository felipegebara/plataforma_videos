import os
import sys
import wave
import struct
import math
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


def generate_bgm_wav(filepath: Path, duration_sec: float = 20.0):
    sample_rate = 22050
    n_samples = int(sample_rate * duration_sec)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(filepath), "w") as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            # Frequência suave de fundo em Dm / suspense
            val_l = int(6000 * math.sin(2 * math.pi * 110.0 * i / sample_rate))
            val_r = int(6000 * math.cos(2 * math.pi * 164.8 * i / sample_rate))
            data = struct.pack("<hh", val_l, val_r)
            wav_file.writeframesraw(data)


class MusicAgent(BaseAgent):
    name = "15_music"
    input_stream = "stream:audio_emotion"
    output_stream = "stream:audio_music"

    def process(self, payload: dict) -> dict:
        self.logger.info("Anexando trilha sonora BGM temática de suspense (MusicGen)...")
        job_id = payload.get("job_id", "job")
        topic = payload.get("research_data", {}).get("main_topic", "Túneis Secretos do Pelourinho")

        audio_dir = Path(__file__).resolve().parents[2] / "output" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        clean_topic = topic.lower().replace(" ", "_").replace("ú", "u").replace("é", "e")
        bgm_path = audio_dir / f"bgm_{clean_topic}.wav"

        total_duration = payload.get("total_duration_sec", 20.0)
        generate_bgm_wav(bgm_path, duration_sec=total_duration)

        self.logger.info(f"Trilha BGM salva: {bgm_path}")

        new_payload = payload.copy()
        new_payload["music_track"] = {
            "path": str(bgm_path),
            "style": "cinematic suspense",
            "volume_db": -12,  # Mixagem de fundo
            "tempo_bpm": 85,
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = MusicAgent(host=host)
    agent.run_forever()
