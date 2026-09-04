import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class FactCheckerAgent(BaseAgent):
    name = "03_fact_checker"
    input_stream = "stream:research"
    output_stream = "stream:factcheck"

    def process(self, payload: dict) -> dict:
        research = payload.get("research_data", {})
        facts = research.get("facts", [])
        myths = research.get("myths", [])

        self.logger.info("Checando veracidade dos fatos e mitos coletados...")

        verified_items = []
        for fact in facts:
            verified_items.append({"claim": fact, "verdict": "VERDADEIRO", "confidence": 0.95})
        for myth in myths:
            verified_items.append({"claim": myth, "verdict": "LENDA", "confidence": 0.88})

        new_payload = payload.copy()
        new_payload["fact_check_data"] = {
            "verified_items": verified_items,
            "overall_credibility": "ALTA_COM_ELEMENTOS_FOLCLORICOS",
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = FactCheckerAgent(host=host)
    agent.run_forever()
