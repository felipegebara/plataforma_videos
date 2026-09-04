import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


class ScenePlannerAgent(BaseAgent):
    name = "06_scene_planner"
    input_stream = "stream:emotion"
    output_stream = "stream:scenes"

    def process(self, payload: dict) -> dict:
        self.logger.info("Fatiando roteiro documental em 6 cenas dinâmicas com corte rápido de câmera...")

        scenes = [
            {
                "scene_id": 1,
                "section": "HOOK_TITLE",
                "narration": "Sob o solo colonial do Pelourinho, existe uma Salvador que a história oficial tentou ocultar.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, historic colonial cobblestone square, empty street at dusk, dramatic lighting, no people, architectural photo",
                "duration_sec": 3.8,
                "overlay_title": "OS TÚNEIS SECRETOS DO PELOURINHO",
                "motion_type": "zoom_in",
            },
            {
                "scene_id": 2,
                "section": "HISTORICAL_CONTEXT",
                "narration": "Durante o século XVII, ordens religiosas e autoridades coloniais escavaram uma vasta rede de galerias subterrâneas.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, colonial underground stone tunnel, ancient archways, dim lantern light, empty passage, no people, 8k",
                "duration_sec": 4.2,
                "motion_type": "pan_left",
            },
            {
                "scene_id": 3,
                "section": "TACTICAL_PURPOSE",
                "narration": "Um labirinto de pedra projetado para transportar riquezas em segredo e servir como rota estratégica de fuga durante as invasões estrangeiras.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, secret underground passage, stone walls, flickering torches, empty, no people, cinematic 8k",
                "duration_sec": 4.5,
                "motion_type": "zoom_out",
            },
            {
                "scene_id": 4,
                "section": "ARCHAEOLOGICAL_DISCOVERY",
                "narration": "Escavações e desabamentos urbanos no centro histórico continuam revelando portões selados e passagens bloqueadas há séculos.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, old iron gate blocking secret underground stone tunnel, dusty atmosphere, dramatic shadows, no people",
                "duration_sec": 4.2,
                "motion_type": "pan_right",
            },
            {
                "scene_id": 5,
                "section": "CLIMAX_UNSOLVED",
                "narration": "Alimentando enigmas profundos que a arqueologia ainda não conseguiu elucidar totalmente.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, mysterious dark underground stone chamber, ancient symbols engraved, empty room, no people, dramatic lighting",
                "duration_sec": 3.8,
                "motion_type": "zoom_in",
            },
            {
                "scene_id": 6,
                "section": "CTA",
                "narration": "Qual enigma você acredita que permanece sepultado sob o solo da primeira capital do Brasil? Deixe sua análise nos comentários.",
                "visual_prompt": "Pelourinho, Salvador, Bahia, historic colonial architecture at sunset, golden hour light, majestic view, no people, 8k",
                "duration_sec": 4.5,
                "motion_type": "zoom_out",
            },
        ]

        new_payload = payload.copy()
        new_payload["scenes"] = scenes
        new_payload["scene_count"] = len(scenes)
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = ScenePlannerAgent(host=host)
    agent.run_forever()
