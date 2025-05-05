# Smart Connection

## What is it?

Smart Connection is a a lightweight wrapper around asyncio TCP connection for building distributed systems. It provides a higher level API in the spirit of [ZeroMQ](https://zeromq.org/). In a nutshell it allows to send and receive Python data between processes.

## Main features

### Framing
TCP is a streaming protocol, this library is a messaging protocol. That is, each message send will be received separately.

### Transparent serialization / deserialization
Each message is serialized and deserialized, allowing to send and receive python data.

### Syntactic sugar
Messages can be pumped out of a connection object through an async for loop.

## A simple echo server example

### Server

```python
from __future__ import annotations

import asyncio

from smart_connection import Connection, wrap_server_connection_handler


@wrap_server_connection_handler
async def handle_connection(connection: Connection):
    async for message in connection:
        await connection.send(message)


async def main():
    async with await asyncio.start_server(handle_connection, "127.0.0.1", 8888) as server:
        await server.serve_forever()
```
### Client

```python
async def read_input(connection: Connection):
    while True:
        message = await aioconsole.ainput(">>> ")  # type: ignore
        await connection.send(message)
        message = await connection.receive(ConnectionEnded)
        if message is ConnectionEnded:
            break
        print(message)

async def main():
    connection_result = await asyncio.open_connection("127.0.0.1", 8888)
    async with wrap_client_connection_handler(connection_result) as connection:
        await read_input(connection)
```
