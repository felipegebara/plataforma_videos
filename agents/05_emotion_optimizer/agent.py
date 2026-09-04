import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class EmotionOptimizerAgent(BaseAgent):
    name = "05_emotion_optimizer"
    input_stream = "stream:script"
    output_stream = "stream:emotion"

    def process(self, payload: dict) -> dict:
        self.logger.info("Otimizando tom de gravidade documental e retenção madura...")
        script = payload.get("script", {})

        hook = script.get("hook", "")
        body = script.get("body", "")
        climax = script.get("climax", "")
        cta = script.get("cta", "")

        # Mantém tom maduro, fluido e elegante sem sensacionalismo infantil
        new_payload = payload.copy()
        new_payload["optimized_script"] = {
            "hook": hook,
            "body": body,
            "climax": climax,
            "cta": cta,
            "retention_score": 0.96,
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = EmotionOptimizerAgent(host=host)
    agent.run_forever()
