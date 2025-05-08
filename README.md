[![Coverage](https://codecov.io/gh/pytek-io/async-stream-processing/branch/main/graph/badge.svg)](https://codecov.io/gh/pytek-io/smart-connection)
[![CI](https://github.com/pytek-io/smart-connection/actions/workflows/ci.yml/badge.svg)](https://github.com/pytek-io/smart-connection/actions)
[![Test suite](https://github.com/pytek-io/smart-connection/actions/workflows/test-suite.yml/badge.svg)](https://github.com/pytek-io/smart-connection/actions)

<a href="https://pypi.org/project/smart-connection" target="_blank">
<img src="https://img.shields.io/pypi/v/smart-connection?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

# Smart Connection

## What is it?

Smart Connection (SC) is a a lightweight wrapper around asyncio TCP connection for building distributed systems. It provides a higher level API in the spirit of [ZeroMQ](https://zeromq.org/).

## Main features

### Exchange message, not bytes
In contrast to TCP, which is a stream-oriented protocol, SC is a message-based protocol. This means that SC guarantees the delivery of each message as a distinct unit and in the correct order. In practice, each message is encapsulated within a frame that ensures its integrity. The protocol is simple and can be easily implemented in any other modern programming language.

### User friendly API
Users can send and receive messages directly. Serialization and deserialization are handled transparently by the library. Messages can be received from a connection object using an async for loop, allowing for elegant user code.

## A simple echo server example

### Server

```python
import asyncio
from smart_connection import Connection, wrap_server_connection_handler


@wrap_server_connection_handler
async def handle_connection(connection: Connection):
    async for message in connection:
        await connection.send(f"server replied: {message}")


async def main():
    async with await asyncio.start_server(handle_connection, "127.0.0.1", 8888) as server:
        await server.serve_forever()
```
### Client

```python
import asyncio
import aioconsole
from smart_connection import wrap_client_connection_handler


async def main():
    connection_ends = await asyncio.open_connection("127.0.0.1", 8888)
    async with wrap_client_connection_handler(connection_ends) as connection:
        while True:
            message = await aioconsole.ainput(">>> ")
            await connection.send(message)
            print(await connection.receive())
```
