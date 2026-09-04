"""
Teste manual da Fase 1.

Uso:
  1. docker compose up -d redis
  2. Num terminal:  python agents/00_mock_echo/agent.py
  3. Noutro terminal: python test_pipeline.py

Publica um envelope em stream:test_in e espera a resposta em stream:test_out.
"""
from orchestrator.bus import RedisBus
from shared.base_agent import new_envelope


def main():
    bus = RedisBus(host="localhost", port=6379)
    assert bus.ping(), "Não consegui conectar no Redis. Ele está rodando? (docker compose up -d redis)"

    # captura o cursor ANTES de publicar, pra não perder uma resposta rápida
    cursor = bus.get_cursor("stream:test_out")

    envelope = new_envelope({"text": "Túneis Secretos do Pelourinho"})
    print(f"Publicando job {envelope['job_id']} em stream:test_in...")
    bus.publish("stream:test_in", envelope)

    print("Aguardando resposta em stream:test_out (timeout 15s)...")
    result = bus.wait_for_new("stream:test_out", last_id=cursor, timeout_s=15.0)

    if result is None:
        print("Nenhuma resposta recebida. O agente 00_mock_echo está rodando?")
        return

    print("\nResposta recebida:")
    print(f"  job_id:    {result['job_id']}")
    print(f"  agent:     {result['agent']}")
    print(f"  status:    {result['status']}")
    print(f"  trace:     {result['trace']}")
    print(f"  payload:   {result['payload']}")


if __name__ == "__main__":
    main()
