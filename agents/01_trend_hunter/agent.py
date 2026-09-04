import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class TrendHunterAgent(BaseAgent):
    name = "01_trend_hunter"
    input_stream = "stream:start"
    output_stream = "stream:trends"

    def process(self, payload: dict) -> dict:
        topic = payload.get("topic", "Lendas e Histórias Secretas do Brasil")
        self.logger.info(f"Identificando tendência para o tópico: '{topic}'")

        new_payload = payload.copy()
        new_payload["trend_data"] = {
            "main_topic": topic,
            "category": "MISTERY_HISTORY",
            "search_volume": "HIGH",
            "virality_score": 94.5,
            "target_audience": "Curiosos, Jovens e Fãs de Histórias Obscuras",
            "keywords": [topic, "lendas urbanas", "mistérios", "segredos ocultos"],
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = TrendHunterAgent(host=host)
    agent.run_forever()
