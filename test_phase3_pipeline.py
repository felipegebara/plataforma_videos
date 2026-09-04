"""
Test Script para a Fase 3 — Produção Visual Integrada (Agentes 01 ao 11)

Fluxo do DAG Completo:
stream:start -> 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> stream:videos
"""
import sys
import importlib
from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope


def load_agent(module_path: str, class_name: str):
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def main():
    bus = RedisBus()
    print(f"🔌 RedisBus status ping: {bus.ping()}")

    # Importa dinamicanente os agentes 01 a 11
    agents = [
        load_agent("agents.01_trend_hunter.agent", "TrendHunterAgent")(bus=bus),
        load_agent("agents.02_research.agent", "ResearchAgent")(bus=bus),
        load_agent("agents.03_fact_checker.agent", "FactCheckerAgent")(bus=bus),
        load_agent("agents.04_story_architect.agent", "StoryArchitectAgent")(bus=bus),
        load_agent("agents.05_emotion_optimizer.agent", "EmotionOptimizerAgent")(bus=bus),
        load_agent("agents.06_scene_planner.agent", "ScenePlannerAgent")(bus=bus),
        load_agent("agents.07_prompt_engineer.agent", "PromptEngineerAgent")(bus=bus),
        load_agent("agents.08_character_manager.agent", "CharacterManagerAgent")(bus=bus),
        load_agent("agents.09_image_generator.agent", "ImageGeneratorAgent")(bus=bus),
        load_agent("agents.10_image_reviewer.agent", "ImageReviewerAgent")(bus=bus),
        load_agent("agents.11_motion_director.agent", "MotionDirectorAgent")(bus=bus),
    ]

    # Injeta o gatilho inicial
    envelope = new_envelope({"topic": "Misteriosa Ilha das Cobras"})
    print(f"\n🚀 Publicando gatilho no 'stream:start' (Job ID: {envelope['job_id']})...")
    bus.publish("stream:start", envelope)

    # Executa a esteira em cadeia (passagem de bastão de 01 a 11)
    print("\n--- Executando esteira de produção (Agentes 01 a 11) ---")
    for agent in agents:
        res = agent.run_once(block_ms=1000)
        print(f"  [{agent.name}]: {res}")

    # Lê o resultado no stream:videos
    print("\n--- Verificando payload final em 'stream:videos' ---")
    results = bus.read_last("stream:videos", count=1)

    if not results:
        print("❌ Nenhum resultado no stream:videos")
        sys.exit(1)

    out_envelope = results[0]
    trace = out_envelope.get("trace", [])
    payload = out_envelope.get("payload", {})

    print("\n✅ FASE 3 CONCLUÍDA COM SUCESSO!")
    print(f"  Job ID:                   {out_envelope.get('job_id')}")
    print(f"  Status:                   {out_envelope.get('status')}")
    print(f"  Revisão Visual Aprovada: {payload.get('visual_review_passed')}")
    print(f"  Vídeos Gerados:           {payload.get('videos_generated')}")
    print(f"  Trace Completo (11/11):   {trace}")

    assert len(trace) == 11
    assert payload.get("visual_review_passed") is True
    assert payload.get("phase3_complete") is True


if __name__ == "__main__":
    main()
