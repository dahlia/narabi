from asyncio import gather, sleep
from base64 import b64encode
from random import randbytes

import pytest

from narabi.backends.base import Backend
from narabi.pubsub import PubSub


@pytest.fixture
def topic_name() -> str:
    return b64encode(randbytes(16)).decode("ascii")


@pytest.mark.asyncio
async def test_topic_pub_sub(backend: Backend, topic_name: str) -> None:
    async def pub() -> None:
        await sleep(0.1)
        pubsub = PubSub(backend)
        async with (
            pubsub.topic(topic_name, dict[str, str]) as topic,
            topic.publisher() as publisher,
        ):
            await publisher.publish({"foo": "hello"})
            await publisher.publish({"bar": "world"})
            await publisher.publish({})

    async def sub(messages: list[dict[str, str]]) -> None:
        pubsub = PubSub(backend)
        async with pubsub.topic(topic_name, dict[str, str]) as topic:
            async for message in topic.subscribe():
                messages.append(message)
                if not message:
                    break

    messages_a: list[dict[str, str]] = []
    messages_b: list[dict[str, str]] = []
    await gather(sub(messages_a), sub(messages_b), pub())
    assert messages_a == messages_b == [{"foo": "hello"}, {"bar": "world"}, {}]
