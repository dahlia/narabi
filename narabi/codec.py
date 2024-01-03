from typing import Any, Protocol

__all__ = ["Codec"]


class Codec(Protocol):
    def dumps(self, __value: Any) -> bytes | str: ...

    def loads(self, __data: bytes) -> Any: ...
