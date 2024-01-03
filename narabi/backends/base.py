from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from typing import Awaitable, Optional, Protocol, Self
from urllib.parse import ParseResult, urlparse

__all__ = ["Backend", "Publisher", "Session", "Subscription", "from_url"]


class Backend(ABC):
    @classmethod
    @abstractmethod
    def from_url(cls, url: ParseResult) -> Self: ...

    @abstractmethod
    def open_session(self, topic: str) -> Awaitable["Session"]: ...


class Session(Protocol):
    def open_subscription(self) -> Awaitable["Subscription"]: ...
    def open_publisher(self) -> Awaitable["Publisher"]: ...
    def close(self) -> Awaitable[None]: ...


class Subscription(Protocol):
    def get(self) -> Awaitable[Optional[bytes]]: ...
    def close(self) -> Awaitable[None]: ...


class Publisher(Protocol):
    def publish(self, message: bytes) -> Awaitable[None]: ...
    def close(self) -> Awaitable[None]: ...


def from_url(url: ParseResult | str) -> Backend:
    parsed: ParseResult = urlparse(url) if isinstance(url, str) else url
    backends = entry_points(group="narabi.backend")
    try:
        backend = backends[parsed.scheme]
    except KeyError:
        raise ValueError(f"unsupported backend: {parsed.scheme}")
    else:
        cls: type[Backend] = backend.load()
        return cls.from_url(parsed)
