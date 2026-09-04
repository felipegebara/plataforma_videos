import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from shared.base_agent import BaseAgent


def format_srt_timestamp(seconds: float) -> str:
    millis = int((seconds % 1) * 1000)
    total_sec = int(seconds)
    secs = total_sec % 60
    mins = (total_sec // 60) % 60
    hrs = total_sec // 3600
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def format_ass_timestamp(seconds: float) -> str:
    centis = int((seconds % 1) * 100)
    total_sec = int(seconds)
    secs = total_sec % 60
    mins = (total_sec // 60) % 60
    hrs = total_sec // 3600
    return f"{hrs:1d}:{mins:02d}:{secs:02d}.{centis:02d}"


class SubtitleAgent(BaseAgent):
    name = "17_subtitle"
    input_stream = "stream:audio_sfx"
    output_stream = "stream:subtitles"

    def process(self, payload: dict) -> dict:
        self.logger.info("Gerando legendas de alto contraste e máxima legibilidade (.SRT e .ASS)...")
        job_id = payload.get("job_id", "job")
        scenes = payload.get("scenes", [])

        sub_dir = Path(__file__).resolve().parents[2] / "output" / "subtitles"
        sub_dir.mkdir(parents=True, exist_ok=True)

        srt_path = sub_dir / f"{job_id}_subtitles.srt"
        ass_path = sub_dir / f"{job_id}_subtitles.ass"

        srt_lines = []
        ass_events = []

        current_time = 0.0

        for i, scene in enumerate(scenes):
            narration = scene.get("narration", "").replace("⚡", "").replace("🚨", "").replace("👇", "").strip()
            duration = scene.get("duration_sec", 5.0)

            start_t = current_time
            end_t = current_time + duration
            current_time = end_t

            srt_start = format_srt_timestamp(start_t)
            srt_end = format_srt_timestamp(end_t)
            srt_lines.append(f"{i + 1}\n{srt_start} --> {srt_end}\n{narration}\n")

            ass_start = format_ass_timestamp(start_t)
            ass_end = format_ass_timestamp(end_t)
            
            # Formata estilo de legenda ASS com alto contraste (texto amarelo/branco com borda preta espessa)
            highlighted_text = f"{{\\b1\\c&H00FFFFFF&\\3c&H00000000&\\bord5}}{narration}"
            ass_events.append(f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{highlighted_text}")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

        # Estilo ASS: Fonte em negrito, borda preta espessa (Outline=5), fundo nítido (MarginV=180)
        ass_header = (
            "[Script Info]\nTitle: Antigravity High Readability Subtitles\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Outfit,54,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,40,40,180,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(ass_events) + "\n")

        self.logger.info(f"Legendas de alto contraste geradas: {srt_path} e {ass_path}")

        new_payload = payload.copy()
        new_payload["subtitles"] = {
            "srt_path": str(srt_path),
            "ass_path": str(ass_path),
            "style": "high_contrast_bold",
            "language": "pt-BR",
        }
        new_payload["phase4_complete"] = True
        return new_payload


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "localhost")
    agent = SubtitleAgent(host=host)
    agent.run_forever()
