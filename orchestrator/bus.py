"""
RedisBus — wrapper fino sobre Redis Streams.

Cada "stream" é uma fila (ex: "stream:research"). Cada agente consome
como parte de um "consumer group" (normalmente o próprio nome do agente),
o que garante:
  - entrega garantida (mensagem só some da fila pendente quando dá ACK)
  - reprocessamento automático se o worker cair no meio (via claim)
  - múltiplas réplicas do mesmo agente podem consumir em paralelo
"""
import json
import time
from typing import Iterator, Optional

import redis

try:
    import fakeredis
    _SHARED_FAKE_SERVER = fakeredis.FakeServer()
except ImportError:
    _SHARED_FAKE_SERVER = None


class RedisBus:
    DLQ_SUFFIX = ":dlq"  # dead-letter queue: envelopes que falharam

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        use_fake_on_error: bool = True,
        connect_timeout: float = 0.5,
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=connect_timeout,
            socket_timeout=connect_timeout,
            decode_responses=True,
        )
        try:
            self.client.ping()
        except Exception:
            if use_fake_on_error and _SHARED_FAKE_SERVER is not None:
                self.client = fakeredis.FakeRedis(server=_SHARED_FAKE_SERVER, decode_responses=True)
            else:
                raise

    def ping(self) -> bool:
        return self.client.ping()

    # ---------- Publicação ----------

    def publish(self, stream: str, envelope: dict) -> str:
        """Publica um envelope (dict) num stream. Retorna o ID da entrada no Redis."""
        return self.client.xadd(stream, {"data": json.dumps(envelope)})

    def publish_to_dlq(self, stream: str, envelope: dict) -> str:
        return self.publish(stream + self.DLQ_SUFFIX, envelope)

    # ---------- Consumo ----------

    def ensure_group(self, stream: str, group: str) -> None:
        """Cria o consumer group se ele ainda não existir. Idempotente."""
        try:
            self.client.xgroup_create(name=stream, groupname=group, id="0", mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    def consume(
        self,
        stream: str,
        group: str,
        consumer: str,
        block_ms: int = 5000,
        count: int = 1,
    ) -> Iterator[tuple[str, dict]]:
        """
        Bloqueia até `block_ms` esperando novas mensagens.
        Gera tuplas (stream_id, envelope_dict). Não dá ACK automaticamente —
        quem chama é responsável por chamar ack() após processar com sucesso.
        """
        resp = self.client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=count,
            block=block_ms,
        )
        if not resp:
            return
        for _stream_name, entries in resp:
            for stream_id, fields in entries:
                try:
                    envelope = json.loads(fields["data"])
                except (KeyError, json.JSONDecodeError):
                    envelope = {"payload": fields, "status": "error", "error": "malformed envelope"}
                yield stream_id, envelope

    def ack(self, stream: str, group: str, stream_id: str) -> None:
        self.client.xack(stream, group, stream_id)

    def claim_stale(
        self, stream: str, group: str, consumer: str, min_idle_ms: int = 60_000
    ) -> Iterator[tuple[str, dict]]:
        """
        Reivindica mensagens que ficaram pendentes (worker anterior caiu antes do ACK)
        há mais de `min_idle_ms`. Útil pra rodar periodicamente num processo de manutenção.
        """
        pending = self.client.xpending_range(stream, group, min="-", max="+", count=100)
        stale_ids = [p["message_id"] for p in pending if p["time_since_delivered"] >= min_idle_ms]
        if not stale_ids:
            return
        claimed = self.client.xclaim(stream, group, consumer, min_idle_ms, stale_ids)
        for stream_id, fields in claimed:
            envelope = json.loads(fields["data"])
            yield stream_id, envelope

    # ---------- Leitura simples (sem grupo, útil para debug/testes) ----------

    def read_last(self, stream: str, count: int = 5) -> list[dict]:
        entries = self.client.xrevrange(stream, count=count)
        return [json.loads(fields["data"]) for _id, fields in entries]

    def get_cursor(self, stream: str) -> str:
        """
        Retorna o ID da última entrada do stream (ou '0-0' se ele ainda não existir/estiver vazio).
        Capture isso ANTES de publicar o job que você quer aguardar, e passe como
        `last_id` para wait_for_new — evita a race condition de usar '$' depois
        que a resposta já pode ter chegado.
        """
        entries = self.client.xrevrange(stream, count=1)
        if not entries:
            return "0-0"
        return entries[0][0]

    def wait_for_new(self, stream: str, last_id: str = "$", timeout_s: float = 15.0) -> Optional[dict]:
        """
        Bloqueia até aparecer uma mensagem em `stream` com ID maior que `last_id`.
        Útil em testes. Para evitar perder mensagens rápidas, capture o cursor
        com get_cursor(stream) ANTES de publicar o job, em vez de usar o default '$'.
        """
        deadline = time.time() + timeout_s
        cursor = last_id
        while time.time() < deadline:
            remaining_ms = max(int((deadline - time.time()) * 1000), 100)
            resp = self.client.xread({stream: cursor}, count=1, block=min(remaining_ms, 1000))
            if resp:
                _stream_name, entries = resp[0]
                stream_id, fields = entries[0]
                return json.loads(fields["data"])
        return None
