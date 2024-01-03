from asyncio import TaskGroup
from base64 import b64encode
from random import randbytes
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from narabi.backends.base import Backend
from narabi.queue import Queue
from narabi.topic import Topic


@pytest_asyncio.fixture
async def topic(
    backend: Backend,
) -> AsyncGenerator[Topic[dict[str, str]], None]:
    queue = Queue(backend)
    topic_name = b64encode(randbytes(16)).decode("ascii")
    async with queue.topic(topic_name, dict[str, str]) as topic:
        yield topic


@pytest.mark.asyncio
async def test_topic_pub_sub(topic: Topic[dict[str, str]]) -> None:
    async def pub() -> None:
        async with topic.publisher() as publisher:
            await publisher.publish({"foo": "hello"})
            await publisher.publish({"bar": "world"})
            await publisher.publish({})

    messages: list[dict[str, str]] = []

    async def sub() -> None:
        async for message in topic.subscribe():
            messages.append(message)
            if not message:
                break

    async with TaskGroup() as tg:
        tg.create_task(sub())
        tg.create_task(pub())

    assert messages == [{"foo": "hello"}, {"bar": "world"}, {}]
