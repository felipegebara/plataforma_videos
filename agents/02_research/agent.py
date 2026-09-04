import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name = "02_research"
    input_stream = "stream:trends"
    output_stream = "stream:research"

    def process(self, payload: dict) -> dict:
        trend = payload.get("trend_data", {})
        topic = trend.get("main_topic", "Lendas e Histórias")
        self.logger.info(f"Pesquisando dados profundos para: '{topic}'")

        new_payload = payload.copy()
        new_payload["research_data"] = {
            "main_topic": topic,
            "facts": [
                f"Relatos históricos apontam construções ocultas relacionadas a {topic} no século XIX.",
                "Documentos de arquivos locais registram acontecimentos inexplicáveis na região.",
            ],
            "myths": [
                f"Dizem que quem visita os locais de {topic} à meia-noite ouve sussurros nas paredes.",
                "A lenda conta que existe um tesouro escondido protegido por uma maldição.",
            ],
            "quotes": [
                "O passado guarda segredos que o tempo não conseguiu apagar.",
                "Nem tudo o que está enterrado deve ser esquecido.",
            ],
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = ResearchAgent(host=host)
    agent.run_forever()
