import json
from typing import TypeVar

from .backends.base import Backend, from_url
from .codec import Codec
from .topic import Topic

__all__ = ["Queue"]


T = TypeVar("T")


class Queue:
    backend: Backend
    codec: Codec

    def __init__(self, backend: Backend | str, codec: Codec = json) -> None:
        self.backend = (
            from_url(backend) if isinstance(backend, str) else backend
        )
        self.codec = codec

    def topic(self, name: str, message_type: type[T]) -> Topic[T]:
        return Topic(self.backend, self.codec, name)
