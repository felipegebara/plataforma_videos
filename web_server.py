"""
Antigravity Web Pipeline Server (Flask App)
Dashboard web para visualização e execução do pipeline (Fases 1, 2, 3 e 4 com Áudio Integrado).
"""
import sys
import json
import importlib
import threading
import time
from pathlib import Path

# Safe UTF-8 reconfiguration for Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, jsonify, request, send_from_directory

from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope

ROOT_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=str(ROOT_DIR), static_url_path="")

PIPELINE_STATE = {
    "current_job_id": None,
    "current_topic": None,
    "status": "idle",  # idle, running, completed, error
    "active_agent": None,
    "trace": [],
    "logs": [],
    "last_payload": {},
}

bus = RedisBus()


def load_agent(module_path: str, class_name: str):
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


ALL_AGENTS_CONFIG = [
    # Fase 2: Roteiro & Texto
    ("01_trend_hunter", "agents.01_trend_hunter.agent", "TrendHunterAgent", "stream:start", "stream:trends"),
    ("02_research", "agents.02_research.agent", "ResearchAgent", "stream:trends", "stream:research"),
    ("03_fact_checker", "agents.03_fact_checker.agent", "FactCheckerAgent", "stream:research", "stream:factcheck"),
    ("04_story_architect", "agents.04_story_architect.agent", "StoryArchitectAgent", "stream:factcheck", "stream:script"),
    ("05_emotion_optimizer", "agents.05_emotion_optimizer.agent", "EmotionOptimizerAgent", "stream:script", "stream:emotion"),
    ("06_scene_planner", "agents.06_scene_planner.agent", "ScenePlannerAgent", "stream:emotion", "stream:scenes"),

    # Fase 3: Imagens & Vídeo
    ("07_prompt_engineer", "agents.07_prompt_engineer.agent", "PromptEngineerAgent", "stream:scenes", "stream:prompts"),
    ("08_character_manager", "agents.08_character_manager.agent", "CharacterManagerAgent", "stream:prompts", "stream:character_consistency"),
    ("09_image_generator", "agents.09_image_generator.agent", "ImageGeneratorAgent", "stream:character_consistency", "stream:images"),
    ("10_image_reviewer", "agents.10_image_reviewer.agent", "ImageReviewerAgent", "stream:images", "stream:images_reviewed"),
    ("11_motion_director", "agents.11_motion_director.agent", "MotionDirectorAgent", "stream:images_reviewed", "stream:videos"),
    ("12_video_composer", "agents.12_video_composer.agent", "VideoComposerAgent", "stream:videos", "stream:final_render"),

    # Fase 4: Áudio, Narração, Trilha BGM & Legendas
    ("13_narrator", "agents.13_narrator.agent", "NarratorAgent", "stream:final_render", "stream:audio_voice"),
    ("14_voice_emotion", "agents.14_voice_emotion.agent", "VoiceEmotionAgent", "stream:audio_voice", "stream:audio_emotion"),
    ("15_music", "agents.15_music.agent", "MusicAgent", "stream:audio_emotion", "stream:audio_music"),
    ("16_ambient_sound", "agents.16_ambient_sound.agent", "AmbientSoundAgent", "stream:audio_music", "stream:audio_sfx"),
    ("17_subtitle", "agents.17_subtitle.agent", "SubtitleAgent", "stream:audio_sfx", "stream:subtitles"),
    ("18_final_multiplexer", "agents.18_final_multiplexer.agent", "FinalMultiplexerAgent", "stream:subtitles", "stream:complete_movie"),
]


def log_event(message: str):
    timestamp = time.strftime("%H:%M:%S")
    PIPELINE_STATE["logs"].append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")


def run_pipeline_worker(topic: str):
    PIPELINE_STATE["status"] = "running"
    PIPELINE_STATE["trace"] = []
    PIPELINE_STATE["logs"] = []
    PIPELINE_STATE["current_topic"] = topic

    envelope = new_envelope({"topic": topic})
    job_id = envelope["job_id"]
    PIPELINE_STATE["current_job_id"] = job_id

    log_event(f"Novo Job iniciado: ID={job_id} | Topico='{topic}'")
    bus.publish("stream:start", envelope)

    for name, mod_path, cls_name, in_str, out_str in ALL_AGENTS_CONFIG:
        PIPELINE_STATE["active_agent"] = name
        log_event(f"Agente {name} consumindo de '{in_str}'...")
        time.sleep(0.35)

        try:
            AgentCls = load_agent(mod_path, cls_name)
            agent = AgentCls(bus=bus)
            success = agent.run_once(block_ms=1000)

            if success:
                PIPELINE_STATE["trace"].append(name)
                log_event(f"Agente {name} concluiu -> '{out_str}'")
            else:
                log_event(f"Agente {name} nao encontrou mensagem para processar.")
        except Exception as err:
            log_event(f"Erro no agente {name}: {err}")
            PIPELINE_STATE["status"] = "error"
            return

    results = bus.read_last("stream:complete_movie", count=1)
    if not results:
        results = bus.read_last("stream:subtitles", count=1)

    if results:
        PIPELINE_STATE["last_payload"] = results[0].get("payload", {})
        PIPELINE_STATE["status"] = "completed"
        PIPELINE_STATE["active_agent"] = None
        log_event("Pipeline completo! Todas as 18 etapas da esteira (Fases 1 a 4) foram executadas com sucesso.")
    else:
        PIPELINE_STATE["status"] = "error"


@app.route("/")
def index():
    return send_from_directory(str(ROOT_DIR), "index.html")


@app.route("/output/<path:filename>")
def serve_output(filename):
    output_dir = ROOT_DIR / "output"
    return send_from_directory(str(output_dir), filename)


@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(PIPELINE_STATE)


@app.route("/api/streams", methods=["GET"])
def get_streams():
    streams_summary = {}
    for name, _, _, in_str, out_str in ALL_AGENTS_CONFIG:
        entries = bus.read_last(out_str, count=1)
        streams_summary[out_str] = entries[0] if entries else None
    return jsonify(streams_summary)


@app.route("/api/trigger", methods=["POST"])
def trigger_pipeline():
    if PIPELINE_STATE["status"] == "running":
        return jsonify({"error": "Pipeline ja esta em execucao"}), 400

    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "Tuneis Secretos de Salvador")

    t = threading.Thread(target=run_pipeline_worker, args=(topic,), daemon=True)
    t.start()

    return jsonify({"message": "Pipeline iniciado!", "topic": topic})


if __name__ == "__main__":
    print("Dashboard Antigravity rodando em http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)
