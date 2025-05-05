import asyncio
from contextlib import suppress

import aioconsole

from smart_connection import Connection, wrap_client_connection_handler


async def read_input(connection: Connection):
    end_value = object()
    while message := await aioconsole.ainput(">>> "):
        await connection.send(message)
        message = await connection.receive(end_value)
        if message is end_value:
            break
        print(message)


async def main():
    connection_result = await asyncio.open_connection("127.0.0.1", 8888)
    async with wrap_client_connection_handler(connection_result) as connection:
        await read_input(connection)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
