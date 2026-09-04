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
        # Fase 2
        load_agent("agents.01_trend_hunter.agent", "TrendHunterAgent")(bus=bus),
        load_agent("agents.02_research.agent", "ResearchAgent")(bus=bus),
        load_agent("agents.03_fact_checker.agent", "FactCheckerAgent")(bus=bus),
        load_agent("agents.04_story_architect.agent", "StoryArchitectAgent")(bus=bus),
        load_agent("agents.05_emotion_optimizer.agent", "EmotionOptimizerAgent")(bus=bus),
        load_agent("agents.06_scene_planner.agent", "ScenePlannerAgent")(bus=bus),
        # Fase 3
        load_agent("agents.07_prompt_engineer.agent", "PromptEngineerAgent")(bus=bus),
        load_agent("agents.08_character_manager.agent", "CharacterManagerAgent")(bus=bus),
        load_agent("agents.09_image_generator.agent", "ImageGeneratorAgent")(bus=bus),
        load_agent("agents.10_image_reviewer.agent", "ImageReviewerAgent")(bus=bus),
        load_agent("agents.11_motion_director.agent", "MotionDirectorAgent")(bus=bus),
        load_agent("agents.12_video_composer.agent", "VideoComposerAgent")(bus=bus),
        # Fase 4 (Áudio, Narração & Legendas)
        load_agent("agents.13_narrator.agent", "NarratorAgent")(bus=bus),
        load_agent("agents.14_voice_emotion.agent", "VoiceEmotionAgent")(bus=bus),
        load_agent("agents.15_music.agent", "MusicAgent")(bus=bus),
        load_agent("agents.16_ambient_sound.agent", "AmbientSoundAgent")(bus=bus),
        load_agent("agents.17_subtitle.agent", "SubtitleAgent")(bus=bus),
        load_agent("agents.18_final_multiplexer.agent", "FinalMultiplexerAgent")(bus=bus),
    ]

    envelope = new_envelope({"topic": "Túneis Secretos do Pelourinho"})
    job_id = envelope["job_id"]
    print(f"🚀 Publicando gatilho no 'stream:start' (Job ID: {job_id})...")
    bus.publish("stream:start", envelope)

    for agent in agents:
        time.sleep(0.1)
        res = agent.run_once(block_ms=1000)
        print(f"  [{agent.name}]: {res}")

    print("\n--- Verificando payload final em 'stream:complete_movie' ---")
    results = bus.read_last("stream:complete_movie", count=1)
    if results:
        payload = results[0].get("payload", {})
        print("\n✅ VÍDEO FINAL COM ÁUDIO DUBLADO E TRILHA BGM CONCLUÍDO COM SUCESSO!")
        print(f"  Job ID:                   {payload.get('job_id')}")
        print(f"  Vídeo Master com Áudio:   {payload.get('final_movie_with_audio')}")
        print(f"  Música BGM:               {payload.get('music_track', {}).get('path')}")
        print(f"  Legendas SRT:             {payload.get('subtitles', {}).get('srt_path')}")
        print(f"  Todas Fases Concluídas:   {payload.get('all_phases_complete')}")


if __name__ == "__main__":
    main()
