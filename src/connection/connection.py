from __future__ import annotations
import pickle
import struct
from asyncio import StreamReader, StreamWriter
from typing import Any, AsyncGenerator, Callable, Coroutine, Generator, Optional, Tuple
from .abstract import AbstractStreamReader, AbstractStreamWriter
from contextlib import asynccontextmanager


Serializer = Callable[[Any], bytes]
Deserializer = Callable[[bytearray], Any]


class FrameBuffer:
    def __init__(self) -> None:
        self.buffer = bytearray()

    def feed(self, data: bytes) -> None:
        self.buffer.extend(data)

    def __iter__(self) -> Generator[bytearray, None, None]:
        while len(self.buffer) >= 4:
            message_length = struct.unpack(">I", self.buffer[:4])[0]
            if len(self.buffer) < 4 + message_length:
                break
            message = self.buffer[4 : 4 + message_length]
            del self.buffer[: 4 + message_length]
            yield message


def create_frame(data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + data


class Connection:
    def __init__(
        self,
        reader: AbstractStreamReader,
        writer: AbstractStreamWriter,
        serializer: Serializer,
        deserializer: Deserializer,
    ):
        self.writer = writer
        self.reader = reader
        self.serializer = serializer
        self.deserializer = deserializer
        self.buffer = FrameBuffer()

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        while data := await self.reader.read():
            self.buffer.feed(data)
            for message in self.buffer:
                yield self.deserializer(message)

    async def receive(self, end_value: Optional[Any]=None) -> Any:
        if data := next(iter(self.buffer), None):
            return self.deserializer(data)
        while True:
            if serialized_data := await self.reader.read():
                self.buffer.feed(serialized_data)
                if data := next(iter(self.buffer), None):
                    return self.deserializer(data)
            else:
                if end_value is not None:
                    return end_value
                raise ConnectionError("Connection closed")

    async def send(self, data: Any) -> None:
        self.send_no_wait(data)
        await self.writer.drain()

    def send_no_wait(self, data: Any) -> None:
        self.send_frame_no_wait(create_frame(self.serializer(data)))

    def send_frame_no_wait(self, message: Any) -> None:
        self.writer.write(message)

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()

    async def __aenter__(self) -> Connection:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


def wrap_server_connection_handler(
    handler: Callable[[Connection], Coroutine[None, None, None]],
    serializer: Serializer = pickle.dumps,
    deserializer: Deserializer = pickle.loads,
) -> Callable[[StreamReader, StreamWriter], Coroutine[None, None, None]]:
    """Decorator to transform a coroutine that accepts a coroutine that accepts
    a Connection into a coroutine that accepts a StreamReader and
    StreamWriter."""

    async def wrapped(reader: StreamReader, writer: StreamWriter) -> None:
        async with Connection(reader, writer, serializer, deserializer) as connection:
            await handler(connection)

    return wrapped

def wrap_client_connection_handler(
    connection_ends: Tuple[AbstractStreamReader, AbstractStreamWriter],
    serializer: Serializer = pickle.dumps,
    deserializer: Deserializer = pickle.loads,
) -> Connection:
    """Wraps `asyncio.open_connection` result into a Connection object.

    connection_ends: Tuple[StreamReader, StreamWriter]
    serialization: Serializer
    """
    return Connection(*connection_ends, serializer, deserializer)


@asynccontextmanager
async def wrap_and_manage_client_connection(
    connection_ends: Tuple[AbstractStreamReader, AbstractStreamWriter],
    serializer: Serializer = pickle.dumps,
    deserializer: Deserializer = pickle.loads,

) -> AsyncGenerator[Connection, None]:
    connection = wrap_client_connection_handler(connection_ends, serializer, deserializer)
    async with connection as connection:
        yield connection
