from __future__ import annotations
import asyncio
from contextlib import suppress

import aioconsole

from connection.connection import Connection, wrap_and_manage_client_connection


class ConnectionEnded:
    pass


async def read_input(connection: Connection):
    while True:
        message = await aioconsole.ainput(">>> ")  # type: ignore
        if message == "exit":
            break
        await connection.send(message)
        message = await connection.receive(ConnectionEnded)
        if message is ConnectionEnded:
            break
        print(message)


async def main():
    connection_result = await asyncio.open_connection("127.0.0.1", 8888)
    async with wrap_and_manage_client_connection(connection_result) as connection:
        await read_input(connection)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
