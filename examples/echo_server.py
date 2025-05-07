import asyncio

from smart_connection import Connection, wrap_server_connection_handler
from contextlib import suppress


@wrap_server_connection_handler
async def handle_connection(connection: Connection):
    counter = 1
    async for message in connection:
        if counter > 3:
            await connection.close()
            break
        counter += 1
        await connection.send(f"server replied: {message}")


async def main():
    async with await asyncio.start_server(handle_connection, "127.0.0.1", 8888) as server:
        await server.serve_forever()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
