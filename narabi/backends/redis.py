import typing
from typing import Optional, cast
from urllib.parse import ParseResult

if typing.TYPE_CHECKING:
    from redis.asyncio import Redis as RedisGeneric

    Redis: typing.TypeAlias = RedisGeneric[bytes]
else:
    from redis.asyncio import Redis

from redis.asyncio.client import PubSub

from .base import Backend, Publisher, Session, Subscription

__all__ = [
    "RedisBackend",
    "RedisPublisher",
    "RedisSession",
    "RedisSubscription",
]


class RedisBackend(Backend):
    redis: Redis

    @classmethod
    def from_url(cls, url: ParseResult) -> "RedisBackend":
        redis = Redis(
            host=url.hostname or "localhost",
            port=url.port or 6379,
            db=int(url.path[1:]) if url.path else 0,
            username=url.username,
            password=url.password,
        )
        return cls(redis)

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def open_session(self, topic: str) -> "RedisSession":
        pubsub = self.redis.pubsub()
        return RedisSession(self.redis, pubsub, topic)


class RedisSession(Session):
    redis: Redis
    pubsub: PubSub
    topic: str

    def __init__(self, redis: Redis, pubsub: PubSub, topic: str) -> None:
        self.redis = redis
        self.pubsub = pubsub
        self.topic = topic

    async def open_subscription(self) -> "RedisSubscription":
        await self.pubsub.subscribe(self.topic)
        return RedisSubscription(self.pubsub)

    async def open_publisher(self) -> "RedisPublisher":
        return RedisPublisher(self.redis, self.topic)

    async def close(self) -> None:
        await self.pubsub.aclose()  # type: ignore


class RedisSubscription(Subscription):
    pubsub: PubSub

    def __init__(self, pubsub: PubSub) -> None:
        self.pubsub = pubsub

    async def get(self) -> Optional[bytes]:
        message = await self.pubsub.get_message(ignore_subscribe_messages=True)
        if message is not None:
            return cast(Optional[bytes], message["data"])
        return None

    async def close(self) -> None:
        await self.pubsub.unsubscribe()


class RedisPublisher(Publisher):
    redis: Redis
    topic: str

    def __init__(self, redis: Redis, topic: str) -> None:
        self.redis = redis
        self.topic = topic

    async def publish(self, message: bytes) -> None:
        await self.redis.publish(self.topic, message)

    async def close(self) -> None:
        pass
