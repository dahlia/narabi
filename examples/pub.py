from contextlib import suppress
from sys import argv

from narabi.queue import Queue


async def main() -> None:
    if len(argv) < 2:
        print(f"Usage: {argv[0]} TOPIC")
        raise SystemExit(1)
    queue = Queue("redis://")
    async with (
        queue.topic(argv[1], str) as topic,
        topic.publisher() as publisher,
    ):
        while True:
            try:
                msg = input("PUB: ")
            except EOFError:
                break
            await publisher.publish(msg)


if __name__ == "__main__":
    from asyncio import run

    with suppress(KeyboardInterrupt):
        run(main())
