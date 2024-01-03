from asyncio import gather, sleep
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from narabi.backends.base import Backend, Session


@pytest.mark.asyncio
async def test_backend_open_session(backend: Backend) -> None:
    session = await backend.open_session("topic")
    await session.close()


@pytest_asyncio.fixture
async def session(backend: Backend) -> AsyncGenerator[Session, None]:
    session = await backend.open_session("topic")
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_session_open_subscription(session: Session) -> None:
    subscription = await session.open_subscription()
    await subscription.close()


@pytest.mark.asyncio
async def test_session_open_publisher(session: Session) -> None:
    publisher = await session.open_publisher()
    await publisher.close()


@pytest.mark.asyncio
async def test_session_pub_sub(session: Session) -> None:
    async def pub() -> None:
        await sleep(0.1)
        publisher = await session.open_publisher()
        try:
            await publisher.publish(b"message")
            await publisher.publish(b"message2")
            await publisher.publish(b"end")
        finally:
            await publisher.close()

    messages: list[bytes] = []

    async def sub() -> None:
        subscription = await session.open_subscription()
        try:
            while True:
                message = await subscription.get()
                if message is not None:
                    messages.append(message)
                if message == b"end":
                    break
        finally:
            await subscription.close()

    await gather(sub(), pub())
    assert messages == [b"message", b"message2", b"end"]
