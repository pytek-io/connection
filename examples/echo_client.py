import asyncio
from contextlib import suppress

import aioconsole

from smart_connection import wrap_client_connection_handler


async def main():
    connection_ends = await asyncio.open_connection("127.0.0.1", 8888)
    end_value = object()
    async with wrap_client_connection_handler(connection_ends) as connection:
        while message := await aioconsole.ainput(">>> "):
            await connection.send(message)
            message = await connection.receive(end_value)
            if message is end_value:
                break
            print(message)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
