import importlib
import time
from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope


def load_agent(module_path: str, class_name: str):
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def main():
    bus = RedisBus()
    assert bus.ping(), "RedisBus offline!"
    print("🔌 RedisBus conectado!")

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
        load_agent("agents.12_video_composer.agent", "VideoComposerAgent")(bus=bus),
    ]

    envelope = new_envelope({"topic": "Túneis Secretos do Pelourinho"})
    job_id = envelope["job_id"]
    print(f"🚀 Publicando gatilho no 'stream:start' (Job ID: {job_id})...")
    bus.publish("stream:start", envelope)

    for agent in agents:
        time.sleep(0.1)
        res = agent.run_once(block_ms=1000)
        print(f"  [{agent.name}]: {res}")

    print("\n--- Verificando payload final em 'stream:final_render' ---")
    results = bus.read_last("stream:final_render", count=1)
    if results:
        payload = results[0].get("payload", {})
        print("\n✅ VÍDEO FINAL RENDERIZADO COM SUCESSO!")
        print(f"  Job ID:            {payload.get('job_id')}")
        print(f"  Caminho do Vídeo:  {payload.get('final_video_path')}")
        print(f"  Pipeline Completo: {payload.get('pipeline_complete')}")


if __name__ == "__main__":
    main()
