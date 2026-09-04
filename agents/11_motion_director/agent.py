import os
import sys
from pathlib import Path
import cv2
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class MotionDirectorAgent(BaseAgent):
    name = "11_motion_director"
    input_stream = "stream:images_reviewed"
    output_stream = "stream:videos"

    def process(self, payload: dict) -> dict:
        self.logger.info("Renderizando movimento cinemático dinâmico de câmera para 6 cenas (OpenCV 24 FPS)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])
        new_scenes = []

        output_dir = Path(__file__).resolve().parents[2] / "output" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, scene in enumerate(scenes):
            new_scene = scene.copy()
            scene_id = scene.get("scene_id", i + 1)
            img_path = scene.get("image_path")
            duration_sec = scene.get("duration_sec", 4.0)
            motion_type = scene.get("motion_type", "zoom_in")

            video_filename = f"{job_id}_scene_{scene_id}.mp4"
            video_path = output_dir / video_filename

            if img_path and Path(img_path).exists():
                try:
                    img = cv2.imread(img_path)
                    if img is not None:
                        h, w, _ = img.shape
                        fps = 24
                        total_frames = int(duration_sec * fps)

                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        out = cv2.VideoWriter(str(video_path), fourcc, fps, (w, h))

                        for frame_idx in range(total_frames):
                            progress = frame_idx / float(total_frames)

                            if motion_type == "zoom_in":
                                scale = 1.0 + (0.08 * progress)
                            elif motion_type == "zoom_out":
                                scale = 1.08 - (0.08 * progress)
                            else:
                                scale = 1.04

                            new_w, new_h = int(w * scale), int(h * scale)
                            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

                            if motion_type == "pan_left":
                                start_x = int((new_w - w) * (1.0 - progress))
                            elif motion_type == "pan_right":
                                start_x = int((new_w - w) * progress)
                            else:
                                start_x = (new_w - w) // 2

                            start_y = (new_h - h) // 2
                            frame = resized[start_y : start_y + h, start_x : start_x + w]
                            out.write(frame)

                        out.release()
                        self.logger.info(f"Vídeo cinemático da Cena {scene_id} renderizado: {video_path}")
                except Exception as err:
                    self.logger.warning(f"Erro ao renderizar vídeo com OpenCV ({err})")

            new_scene["video_path"] = str(video_path)
            new_scene["fps"] = 24
            new_scene["motion_mode"] = motion_type
            new_scenes.append(new_scene)

        new_payload = payload.copy()
        new_payload["scenes"] = new_scenes
        new_payload["videos_rendered"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = MotionDirectorAgent(host=host)
    agent.run_forever()
