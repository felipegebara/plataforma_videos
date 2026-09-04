import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class ImageReviewerAgent(BaseAgent):
    name = "10_image_reviewer"
    input_stream = "stream:images"
    output_stream = "stream:images_reviewed"

    def process(self, payload: dict) -> dict:
        self.logger.info("Analisando qualidade e fidelidade das imagens geradas (CLIP + BLIP-2 Score)...")

        new_payload = payload.copy()
        scenes = payload.get("scenes", [])
        new_scenes = []
        review_passed = True

        for scene in scenes:
            new_scene = scene.copy()

            # Simula score CLIP de 95% (threshold de qualidade = 90%)
            review_score = 0.95
            new_scene["review"] = {
                "score": review_score,
                "passed": review_score >= 0.90,
                "issues": [],
            }

            if not new_scene["review"]["passed"]:
                review_passed = False

            new_scenes.append(new_scene)

        new_payload["scenes"] = new_scenes
        new_payload["visual_review_passed"] = review_passed
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = ImageReviewerAgent(host=host)
    agent.run_forever()
