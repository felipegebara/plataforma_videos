import os
import sys
from pathlib import Path
import cv2

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class VideoComposerAgent(BaseAgent):
    name = "12_video_composer"
    input_stream = "stream:videos"
    output_stream = "stream:final_render"

    def process(self, payload: dict) -> dict:
        self.logger.info("Unificando todas as cenas no vídeo final completo (MP4 Render)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])

        output_dir = Path(__file__).resolve().parents[2] / "output" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_video_path = output_dir / f"{job_id}_FINAL_COMPLETE_VIDEO.mp4"

        width, height = 1080, 1920
        fps = 24
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(final_video_path), fourcc, fps, (width, height))

        total_frames_written = 0

        for scene in scenes:
            scene_video = scene.get("video_path")
            if scene_video and Path(scene_video).exists():
                cap = cv2.VideoCapture(scene_video)
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                    total_frames_written += 1
                cap.release()

        out.release()
        self.logger.info(f"VÍDEO FINAL UNIFICADO GERADO COM SUCESSO: {final_video_path} ({total_frames_written} frames)")

        new_payload = payload.copy()
        new_payload["final_video_path"] = str(final_video_path)
        new_payload["pipeline_complete"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = VideoComposerAgent(host=host)
    agent.run_forever()
