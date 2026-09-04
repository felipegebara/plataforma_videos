import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip


class FinalMultiplexerAgent(BaseAgent):
    name = "18_final_multiplexer"
    input_stream = "stream:subtitles"
    output_stream = "stream:complete_movie"

    def process(self, payload: dict) -> dict:
        self.logger.info("Mixando voz humana neural (pt-BR-AntonioNeural) e trilha BGM no vídeo final...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])

        output_dir = Path(__file__).resolve().parents[2] / "output" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_movie_path = output_dir / f"{job_id}_FINAL_MOVIE_WITH_AUDIO.mp4"

        video_clips = []
        audio_clips = []
        current_time = 0.0

        for scene in scenes:
            scene_video_path = scene.get("video_path")
            voice_path = scene.get("voice_audio_path")

            voice_dur = 5.0
            if voice_path and Path(voice_path).exists() and Path(voice_path).stat().st_size > 100:
                try:
                    # Carrega a voz humana neural na velocidade natural com timbre autêntico
                    raw_voice = AudioFileClip(voice_path)
                    voice_clip = raw_voice.with_start(current_time)
                    voice_dur = voice_clip.duration + 0.1
                    audio_clips.append(voice_clip.with_volume_scaled(1.5))
                    self.logger.info(f"Cena {scene.get('scene_id')}: Voz Humana Neural encadeada com timbre natural ({voice_dur:.2f}s)")
                except Exception as err:
                    self.logger.warning(f"Erro ao carregar voz da cena ({err})")
                    voice_dur = scene.get("duration_sec", 5.0)

            if scene_video_path and Path(scene_video_path).exists():
                try:
                    v_clip = VideoFileClip(scene_video_path)
                    v_clip = v_clip.with_duration(voice_dur).with_start(current_time)
                    video_clips.append(v_clip)
                except Exception as err:
                    self.logger.warning(f"Erro ao processar clipe de vídeo ({err})")

            current_time += voice_dur

        # Trilha BGM de Fundo Suave
        bgm_path = payload.get("music_track", {}).get("path")
        if bgm_path and Path(bgm_path).exists() and Path(bgm_path).stat().st_size > 100:
            try:
                raw_bgm = AudioFileClip(bgm_path)
                bgm_dur = min(current_time, raw_bgm.duration)
                bgm_clip = raw_bgm.subclipped(0, bgm_dur).with_start(0).with_volume_scaled(0.12)
                audio_clips.append(bgm_clip)
                self.logger.info("Trilha BGM acoplada suavemente sob a voz neural.")
            except Exception as err:
                self.logger.warning(f"Erro ao mixar BGM ({err})")

        try:
            if video_clips:
                composite_video = CompositeVideoClip(video_clips)
                if audio_clips:
                    composite_audio = CompositeAudioClip(audio_clips)
                    composite_video = composite_video.with_audio(composite_audio)

                composite_video.write_videofile(
                    str(final_movie_path),
                    codec="libx264",
                    audio_codec="aac",
                    fps=24,
                    logger=None
                )
                self.logger.info(f"VÍDEO FINAL COM VOZ HUMANA NEURAL EXPORTADO COM SUCESSO: {final_movie_path}")
        except Exception as err:
            self.logger.error(f"Erro ao exportar vídeo final ({err})")

        new_payload = payload.copy()
        new_payload["final_movie_with_audio"] = str(final_movie_path)
        new_payload["all_phases_complete"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = FinalMultiplexerAgent(host=host)
    agent.run_forever()
