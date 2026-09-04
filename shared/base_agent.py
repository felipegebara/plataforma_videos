"""
BaseAgent — contrato comum a todos os 23 agentes do Antigravity.

Cada agente concreto só precisa:
  1. Definir `name`, `input_stream`, `output_stream` (ou passar no super().__init__)
  2. Implementar `process(self, payload: dict) -> dict`

Tudo o resto (consumo do Redis, envelope, ACK, retries, DLQ, logging)
é tratado aqui, uma única vez.
"""
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from orchestrator.bus import RedisBus
from shared.logging import get_logger

MAX_RETRIES = 3


def new_envelope(payload: dict, pipeline_id: Optional[str] = None) -> dict:
    """Helper para criar o primeiro envelope de um pipeline novo (usado pelo agente 01)."""
    return {
        "job_id": str(uuid.uuid4()),
        "pipeline_id": pipeline_id or str(uuid.uuid4()),
        "agent": "seed",
        "status": "pending",
        "timestamp": _now_iso(),
        "payload": payload,
        "trace": [],
        "retry_count": 0,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseAgent(ABC):
    name: str
    input_stream: str
    output_stream: str

    def __init__(
        self,
        bus: Optional[RedisBus] = None,
        host: str = "localhost",
        port: int = 6379,
        redis_host: Optional[str] = None,
        agent_name: Optional[str] = None,
        input_stream: Optional[str] = None,
        output_stream: Optional[str] = None,
    ):
        if agent_name:
            self.name = agent_name
        elif hasattr(self, "agent_name") and not getattr(self, "name", None):
            self.name = getattr(self, "agent_name")

        if input_stream:
            self.input_stream = input_stream
        if output_stream:
            self.output_stream = output_stream

        if not getattr(self, "name", None) or not getattr(self, "input_stream", None) or not getattr(
            self, "output_stream", None
        ):
            raise ValueError("Agentes concretos devem definir name, input_stream e output_stream")

        actual_host = redis_host or host
        self.bus = bus or RedisBus(host=actual_host, port=port)
        self.group = self.name  # consumer group = nome do agente
        self.bus.ensure_group(self.input_stream, self.group)
        self.logger = get_logger(self.name)

    @property
    def agent_name(self) -> str:
        return self.name

    @abstractmethod
    def process(self, payload: dict) -> dict:
        """
        Lógica de negócio do agente. Recebe o payload do envelope de entrada
        e retorna o payload que será publicado no stream de saída.
        Deve lançar uma exceção se não conseguir processar — o BaseAgent
        cuida do retry/DLQ automaticamente.
        """
        raise NotImplementedError

    def run_forever(self, block_ms: int = 5000) -> None:
        self.logger.info(f"Ouvindo '{self.input_stream}' (grupo '{self.group}')...")
        while True:
            for stream_id, envelope in self.bus.consume(
                self.input_stream, self.group, consumer=self.name, block_ms=block_ms
            ):
                self._handle(stream_id, envelope)

    def run(self, block_ms: int = 5000) -> None:
        """Alias para run_forever."""
        self.run_forever(block_ms=block_ms)

    def run_once(self, block_ms: int = 5000) -> bool:
        """Processa no máximo uma mensagem. Útil para testes. Retorna True se processou algo."""
        for stream_id, envelope in self.bus.consume(
            self.input_stream, self.group, consumer=self.name, block_ms=block_ms, count=1
        ):
            self._handle(stream_id, envelope)
            return True
        return False

    # ---------- internals ----------

    def _handle(self, stream_id: str, envelope: dict) -> None:
        job_id = envelope.get("job_id", "unknown")
        try:
            self.logger.info(f"Processando job {job_id}")
            output_payload = self.process(envelope.get("payload", {}))

            envelope["payload"] = output_payload
            envelope["agent"] = self.name
            envelope["status"] = "success"
            envelope["timestamp"] = _now_iso()
            envelope.setdefault("trace", []).append(self.name)

            self.bus.publish(self.output_stream, envelope)
            self.logger.info(f"Job {job_id} concluído -> '{self.output_stream}'")

        except Exception as exc:
            envelope["retry_count"] = envelope.get("retry_count", 0) + 1
            envelope["error"] = str(exc)
            envelope["timestamp"] = _now_iso()

            if envelope["retry_count"] <= MAX_RETRIES:
                envelope["status"] = "retry"
                self.logger.warning(
                    f"Job {job_id} falhou (tentativa {envelope['retry_count']}/{MAX_RETRIES}): {exc}"
                )
                self.bus.publish(self.input_stream, envelope)  # reenfileira
            else:
                envelope["status"] = "error"
                self.logger.error(f"Job {job_id} esgotou tentativas, indo para DLQ: {exc}")
                self.bus.publish_to_dlq(self.output_stream, envelope)

        finally:
            self.bus.ack(self.input_stream, self.group, stream_id)
