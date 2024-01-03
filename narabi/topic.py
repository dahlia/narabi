from types import TracebackType
from typing import AsyncIterable, Generic, Optional, Self, TypeVar

from narabi.publisher import PublisherContext

from .backends.base import Backend, Session, Subscription
from .codec import Codec

__all__ = ["Topic", "TopicSessionError"]


T = TypeVar("T")


class Topic(Generic[T]):
    backend: Backend
    codec: Codec
    name: str
    session: Optional[Session]
    subscription: Optional[Subscription]

    def __init__(self, backend: Backend, codec: Codec, name: str) -> None:
        self.backend = backend
        self.codec = codec
        self.name = name
        self.session = None
        self.subscription = None

    async def __aenter__(self) -> Self:
        self.session = await self.backend.open_session(self.name)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self.session is None:
            raise TopicSessionError("no topic context is opened")
        if self.subscription is not None:
            await self.subscription.close()
            self.subscription = None
        await self.session.close()
        self.session = None

    async def subscribe(self) -> AsyncIterable[T]:
        if self.session is None:
            raise TopicSessionError("no topic context is opened")
        self.subscription = await self.session.open_subscription()
        while True:
            message = await self.subscription.get()
            if message is not None:
                yield self.codec.loads(message)

    def publisher(self) -> PublisherContext[T]:
        if self.session is None:
            raise TopicSessionError("no topic context is opened")
        return PublisherContext[T](self.session.open_publisher, self.codec)

    async def publish(self, value: T) -> None:
        async with self.publisher() as publisher:
            await publisher.publish(value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r}>"


class TopicSessionError(RuntimeError):
    pass
