import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator, Callable

logger = logging.getLogger("core.broker")

class MessageBroker(ABC):
    """Contrato abstrato de Message Broker para suportar Desktop (asyncio) e SaaS (Redis)."""

    @abstractmethod
    async def publish(self, stream_name: str, payload: Dict[str, Any]) -> str:
        """Publica uma mensagem em um tópico/stream."""
        pass

    @abstractmethod
    async def subscribe(self, stream_name: str, group: str, consumer: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Consome mensagens de um tópico/stream."""
        pass

    @abstractmethod
    async def ack(self, stream_name: str, group: str, message_id: str) -> None:
        """Confirma o processamento de uma mensagem."""
        pass


class AsyncQueueBroker(MessageBroker):
    """
    Message Broker 100% em memória para Desktop e execução local sem dependência do Redis.
    Utiliza asyncio.Queue e pub-sub leve.
    """
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, list[Callable]] = {}
        self._msg_counter = 0

    def _get_queue(self, stream_name: str) -> asyncio.Queue:
        if stream_name not in self._queues:
            self._queues[stream_name] = asyncio.Queue()
        return self._queues[stream_name]

    async def publish(self, stream_name: str, payload: Dict[str, Any]) -> str:
        self._msg_counter += 1
        msg_id = f"msg_{self._msg_counter}"
        envelope = {
            "id": msg_id,
            "stream": stream_name,
            "payload": payload
        }
        queue = self._get_queue(stream_name)
        await queue.put(envelope)
        logger.debug(f"[AsyncQueue] Publicado em '{stream_name}' | ID: {msg_id}")
        return msg_id

    async def subscribe(self, stream_name: str, group: str = "default", consumer: str = "worker") -> AsyncGenerator[Dict[str, Any], None]:
        queue = self._get_queue(stream_name)
        while True:
            envelope = await queue.get()
            yield envelope

    async def ack(self, stream_name: str, group: str, message_id: str) -> None:
        logger.debug(f"[AsyncQueue] ACK recebido para '{stream_name}' | ID: {message_id}")


class RedisStreamsBroker(MessageBroker):
    """Message Broker para SaaS / Nuvem utilizando Redis Streams."""
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis = None

    async def _connect(self):
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)

    async def publish(self, stream_name: str, payload: Dict[str, Any]) -> str:
        await self._connect()
        data = {"data": json.dumps(payload, ensure_ascii=False)}
        msg_id = await self._redis.xadd(stream_name, data)
        return msg_id

    async def subscribe(self, stream_name: str, group: str = "default_group", consumer: str = "worker_1") -> AsyncGenerator[Dict[str, Any], None]:
        await self._connect()
        try:
            await self._redis.xgroup_create(stream_name, group, id="0", mkstream=True)
        except Exception:
            pass

        while True:
            try:
                entries = await self._redis.xreadgroup(group, consumer, {stream_name: ">"}, count=1, block=5000)
                if entries:
                    for stream, messages in entries:
                        for msg_id, raw_data in messages:
                            payload = json.loads(raw_data.get("data", "{}"))
                            yield {"id": msg_id, "stream": stream, "payload": payload}
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[RedisBroker] Erro ao consumir stream {stream_name}: {e}")
                await asyncio.sleep(2.0)

    async def ack(self, stream_name: str, group: str, message_id: str) -> None:
        await self._connect()
        await self._redis.xack(stream_name, group, message_id)


def get_broker(mode: str = "desktop", redis_url: Optional[str] = None) -> MessageBroker:
    """Factory que retorna o Broker apropriado para Desktop ou SaaS."""
    if mode.lower() == "saas" and redis_url:
        return RedisStreamsBroker(redis_url=redis_url)
    return AsyncQueueBroker()
