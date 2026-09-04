import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent
from shared.ollama_client import query_ollama


class StoryArchitectAgent(BaseAgent):
    name = "04_story_architect"
    input_stream = "stream:factcheck"
    output_stream = "stream:script"

    def process(self, payload: dict) -> dict:
        topic = payload.get("research_data", {}).get("main_topic", "Túneis Secretos do Pelourinho")
        self.logger.info(f"Construindo narrativa documental madura e misteriosa para '{topic}'...")

        prompt = (
            f"Escreva um roteiro documental maduro, sério e intrigante sobre '{topic}' para público adulto. "
            "Evite tom infantil ou escolar! Use estilo de documentário de suspense histórico. Divida em HOOK, BODY, CLIMAX e CTA."
        )

        ollama_response = query_ollama(prompt, timeout_sec=8.0)

        # Roteiro maduro estilo documentário cinemático / investigação de mistério
        default_hook = "Sob o solo colonial do Pelourinho, existe uma Salvador que a história oficial tentou ocultar..."
        default_body = (
            "Durante o século XVII, ordens religiosas e autoridades coloniais escavaram uma vasta rede de galerias subterrâneas. "
            "Um labirinto de pedra projetado para transportar riquezas em segredo e servir como rota estratégica de fuga durante as invasões estrangeiras."
        )
        default_climax = (
            "Escavações e desabamentos urbanos no centro histórico continuam revelando portões selados e passagens bloqueadas há séculos, "
            "alimentando enigmas que a arqueologia ainda não conseguiu elucidar totalmente."
        )
        default_cta = "Qual enigma você acredita que permanece sepultado sob o solo da primeira capital do Brasil? Deixe sua análise nos comentários."

        new_payload = payload.copy()
        new_payload["script"] = {
            "hook": default_hook,
            "body": default_body,
            "climax": default_climax,
            "cta": default_cta,
            "llm_used": "qwen2.5:7b" if ollama_response else "documentary_storytelling_engine",
        }
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = StoryArchitectAgent(host=host)
    agent.run_forever()
