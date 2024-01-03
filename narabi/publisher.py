from types import TracebackType
from typing import (
    AsyncContextManager,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Self,
    TypeVar,
)

from .backends.base import Publisher
from .codec import Codec

__all__ = ["PublisherContext", "PublisherContextError"]

T = TypeVar("T")


class PublisherContext(Generic[T], AsyncContextManager["PublisherContext[T]"]):
    open_publisher: Callable[[], Awaitable[Publisher]]
    publisher: Optional[Publisher]
    codec: Codec

    def __init__(
        self,
        publisher_opener: Callable[[], Awaitable[Publisher]],
        codec: Codec,
    ) -> None:
        self.open_publisher = publisher_opener
        self.codec = codec
        self.publisher = None

    async def __aenter__(self) -> Self:
        if self.publisher is not None:
            raise PublisherContextError("publisher context is already opened")
        self.publisher = await self.open_publisher()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self.publisher is None:
            raise PublisherContextError("no publisher context is opened")
        await self.publisher.close()

    async def publish(self, value: T) -> None:
        if self.publisher is None:
            raise PublisherContextError("no publisher context is opened")
        message = self.codec.dumps(value)
        await self.publisher.publish(
            message.encode("utf-8") if isinstance(message, str) else message
        )


class PublisherContextError(RuntimeError):
    pass
