"""
Teste síncrono local da Fase 1.
"""
import sys
import importlib

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope

mock_agent_mod = importlib.import_module("agents.00_mock_echo.agent")
MockEchoAgent = mock_agent_mod.MockEchoAgent


def main():
    bus = RedisBus()
    print(f"RedisBus status ping: {bus.ping()}")

    envelope = new_envelope({"text": "Túneis Secretos do Pelourinho"})
    print(f"Publicando envelope (job_id: {envelope['job_id']})...")
    bus.publish("stream:test_in", envelope)

    print("Executando MockEchoAgent...")
    agent = MockEchoAgent(bus=bus)
    processed = agent.run_once(block_ms=1000)
    print(f"Mensagem processada pelo agente: {processed}")

    print("Lendo resultado em 'stream:test_out'...")
    results = bus.read_last("stream:test_out", count=1)

    if results:
        res = results[0]
        print("\nTESTE LOCAL CONCLUÍDO COM SUCESSO!")
        print(f"  job_id:    {res.get('job_id')}")
        print(f"  agent:     {res.get('agent')}")
        print(f"  status:    {res.get('status')}")
        print(f"  trace:     {res.get('trace')}")
        print(f"  payload:   {res.get('payload')}")
    else:
        print("Nenhum resultado encontrado.")


if __name__ == "__main__":
    main()
