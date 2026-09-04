"""
Test Script para a Fase 2 — Pipeline de Texto Ponta-a-Ponta (Agentes 01 a 06)

Fluxo do DAG:
stream:start -> 01_trend_hunter -> stream:trends -> 02_research -> stream:research
             -> 03_fact_checker -> stream:factcheck -> 04_story_architect -> stream:script
             -> 05_emotion_optimizer -> stream:emotion -> 06_scene_planner -> stream:scenes
"""
import sys
import importlib
from pathlib import Path

from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope


def load_agent(module_path: str, class_name: str):
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def main():
    bus = RedisBus()
    print(f"🔌 RedisBus status ping: {bus.ping()}")

    # Importa dinamicanente cada um dos 6 agentes
    TrendHunterAgent = load_agent("agents.01_trend_hunter.agent", "TrendHunterAgent")
    ResearchAgent = load_agent("agents.02_research.agent", "ResearchAgent")
    FactCheckerAgent = load_agent("agents.03_fact_checker.agent", "FactCheckerAgent")
    StoryArchitectAgent = load_agent("agents.04_story_architect.agent", "StoryArchitectAgent")
    EmotionOptimizerAgent = load_agent("agents.05_emotion_optimizer.agent", "EmotionOptimizerAgent")
    ScenePlannerAgent = load_agent("agents.06_scene_planner.agent", "ScenePlannerAgent")

    # Instancia agentes utilizando o mesmo bus
    agent01 = TrendHunterAgent(bus=bus)
    agent02 = ResearchAgent(bus=bus)
    agent03 = FactCheckerAgent(bus=bus)
    agent04 = StoryArchitectAgent(bus=bus)
    agent05 = EmotionOptimizerAgent(bus=bus)
    agent06 = ScenePlannerAgent(bus=bus)

    # 1. Injeta o gatilho inicial no stream:start
    initial_topic = "Túneis Secretos do Pelourinho"
    envelope = new_envelope({"topic": initial_topic})
    print(f"\n🚀 Publicando gatilho no 'stream:start' (Job ID: {envelope['job_id']})...")
    bus.publish("stream:start", envelope)

    # 2. Executa a esteira em cadeia (passagem de bastão de 01 a 06)
    print("\n--- Executando esteira de produção (Agentes 01 a 06) ---")
    p1 = agent01.run_once(block_ms=1000)
    print(f"  [01_trend_hunter]: {p1}")

    p2 = agent02.run_once(block_ms=1000)
    print(f"  [02_research]: {p2}")

    p3 = agent03.run_once(block_ms=1000)
    print(f"  [03_fact_checker]: {p3}")

    p4 = agent04.run_once(block_ms=1000)
    print(f"  [04_story_architect]: {p4}")

    p5 = agent05.run_once(block_ms=1000)
    print(f"  [05_emotion_optimizer]: {p5}")

    p6 = agent06.run_once(block_ms=1000)
    print(f"  [06_scene_planner]: {p6}")

    # 3. Lê o resultado final no stream:scenes
    print("\n--- Verificando payload final em 'stream:scenes' ---")
    results = bus.read_last("stream:scenes", count=1)

    if not results:
        print("❌ Nenhum resultado encontrado no stream:scenes")
        sys.exit(1)

    final_envelope = results[0]
    trace = final_envelope.get("trace", [])
    payload = final_envelope.get("payload", {})

    print("\n✅ FASE 2 CONCLUÍDA COM SUCESSO!")
    print(f"  Job ID:           {final_envelope.get('job_id')}")
    print(f"  Status:           {final_envelope.get('status')}")
    print(f"  Trace da Esteira: {trace}")
    print(f"  Total de Cenas:   {len(payload.get('scenes', []))}")
    print(f"  Duração Total:    {payload.get('total_duration_sec')}s")
    print(f"  Pronto p/ Fase 3: {payload.get('ready_for_phase3')}")

    print("\n--- Exemplo de Matriz de Cenas Gerada ---")
    for scene in payload.get("scenes", []):
        print(f"  [Cena {scene['scene_id']}] {scene['section']} ({scene['duration_sec']}s)")
        print(f"    Narração: {scene['narration']}")
        print(f"    Visual Prompt: {scene['visual_prompt']}")
        print(f"    Câmera: {scene['camera_angle']}\n")

    # Asserções de validação
    expected_trace = [
        "01_trend_hunter",
        "02_research",
        "03_fact_checker",
        "04_story_architect",
        "05_emotion_optimizer",
        "06_scene_planner",
    ]
    assert trace == expected_trace, f"Trace incorreto! Esperado {expected_trace}, obtido {trace}"
    assert payload.get("ready_for_phase3") is True
    assert len(payload.get("scenes", [])) == 4


if __name__ == "__main__":
    main()
