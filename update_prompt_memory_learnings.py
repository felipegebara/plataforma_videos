import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

mem_file = Path(__file__).resolve().parent / "prompt_memory.json"

learnings = {
  "top_performing_patterns": {
    "hook_formula": "HIGH_CONFLICT_OR_SECRET",
    "examples": [
      "Pelourinho Secret Tunnels & Punishment Chambers",
      "Canudos Historical War & Air Strikes",
      "Caldeirao Submerged / Destroyed Utopia"
    ],
    "retention_rate_avg": 0.92,
    "recommended_lighting": "high contrast chiaroscuro, torchlight, stormy dark sky",
    "recommended_pacing_words_per_sec": 3.2,
    "recommended_subtitles": "yellow_white_dynamic_high_contrast"
  },
  "low_performing_patterns": {
    "hook_formula": "PURE_LANDSCAPE_TOURISM",
    "examples": [
      "Chapada Diamantina scenery without conflict"
    ],
    "retention_rate_avg": 0.45,
    "issue": "Lack of immediate danger, mystery or human conflict in the first 3 seconds"
  }
}

with open(mem_file, "w", encoding="utf-8") as f:
    json.dump(learnings, f, indent=2, ensure_ascii=False)

print("[OK] Aprendizados de Retencao Salvos em prompt_memory.json com Sucesso!")
