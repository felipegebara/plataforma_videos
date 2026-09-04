"""
00_mock_echo — agente de teste.

Não usa nenhum LLM. Só recebe {"text": "..."} e devolve
{"text": "...", "echoed_by": "00_mock_echo"}.

Serve para validar que bus.py + base_agent.py funcionam de ponta a ponta
antes de plugar os agentes de verdade (que dependem de Ollama, FLUX, etc).
"""
import sys
from pathlib import Path

# permite rodar `python agents/00_mock_echo/agent.py` a partir da raiz do projeto
sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent  # noqa: E402


class MockEchoAgent(BaseAgent):
    name = "00_mock_echo"
    input_stream = "stream:test_in"
    output_stream = "stream:test_out"

    def process(self, payload: dict) -> dict:
        text = payload.get("text", "")
        return {
            "text": text,
            "echoed_by": self.name,
            "length": len(text),
        }


if __name__ == "__main__":
    agent = MockEchoAgent(host="localhost", port=6379)
    agent.run_forever()
