"""
Runner local para demonstrar o pipeline Fase 1 rodando localmente.
Inicia o MockEchoAgent e executa a publicação/recebimento de mensagens.
"""
import importlib
import threading
import time

from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope

mock_agent_mod = importlib.import_module("agents.00_mock_echo.agent")
MockEchoAgent = mock_agent_mod.MockEchoAgent


def start_agent(agent: MockEchoAgent, stop_event: threading.Event):
    while not stop_event.is_set():
        agent.run_once(block_ms=500)


def main():
    bus = RedisBus()
    print(f"RedisBus conectado! (Ping: {bus.ping()})")

    agent = MockEchoAgent(bus=bus)
    stop_event = threading.Event()

    # Inicia agente mock em background thread
    t = threading.Thread(target=start_agent, args=(agent, stop_event), daemon=True)
    t.start()
    print("🤖 MockEchoAgent iniciado ouvindo 'stream:test_in'...")

    time.sleep(0.5)

    cursor = bus.get_cursor("stream:test_out")
    envelope = new_envelope({"text": "Túneis Secretos do Pelourinho"})
    print(f"📤 Publicando job {envelope['job_id']} em 'stream:test_in'...")
    bus.publish("stream:test_in", envelope)

    print("⏳ Aguardando resposta em 'stream:test_out'...")
    result = bus.wait_for_new("stream:test_out", last_id=cursor, timeout_s=5.0)

    stop_event.set()
    t.join(timeout=1.0)

    if result:
        print("\n✅ Resposta recebida com SUCESSO:")
        print(f"  job_id:    {result.get('job_id')}")
        print(f"  agent:     {result.get('agent')}")
        print(f"  status:    {result.get('status')}")
        print(f"  trace:     {result.get('trace')}")
        print(f"  payload:   {result.get('payload')}")
    else:
        print("\n❌ Nenhum resultado recebido no tempo limite.")


if __name__ == "__main__":
    main()
