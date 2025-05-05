import random
from itertools import product
from typing import Any, List

import pytest

from smart_connection import Connection, wrap_client_connection_handler, wrap_server_connection_handler

random.seed(10)
TEST_DATA: List[Any] = [1, "string", True, {"key": "value"}, [1, 2, 3], None, "another string", (1, 2, 3)]


class StreamReader:
    def __init__(self) -> None:
        self.buffer = b""

    async def read(self, n: int) -> bytes:
        n = random.randint(1, 10)
        data = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return data


class StreamWriter:
    def __init__(self, reader: StreamReader) -> None:
        self.reader = reader

    def write(self, data: bytes) -> None:
        self.reader.buffer += data

    async def drain(self) -> None:
        pass

    def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass


@pytest.mark.parametrize("no_wait,method", product([True, False], ["__iter__", "receive", "handle_connection"]))
async def test_chunked_messages(no_wait: bool, method: str) -> None:
    """
    Simulate receiving messages in chunks of random size.
    """
    reader_1, reader_2 = StreamReader(), StreamReader()
    writer_1, writer_2 = StreamWriter(reader_2), StreamWriter(reader_1)
    connection_1 = wrap_client_connection_handler((reader_2, writer_2))
    async with wrap_client_connection_handler((reader_1, writer_1)) as connection_2:
        data = [random.choice(TEST_DATA) for _ in range(1000)]
        received_data: List[Any] = []
        for value in data:
            if no_wait:
                connection_1.send_no_wait(value)
            else:
                await connection_1.send(value)
        await connection_1.close()
        if method == "__iter__":
            async for message in connection_2:
                received_data.append(message)
        elif method == "receive":
            end_value = object()
            while (msg := await connection_2.receive(end_value)) is not end_value:
                received_data.append(msg)
        else:

            async def handle_connection(connection: Connection) -> None:
                async for message in connection:
                    received_data.append(message)

            await wrap_server_connection_handler(connection_handler=handle_connection)(reader_1, writer_2)
        assert received_data == data
