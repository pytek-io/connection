import pytest
import random
from typing import Any

from connection.connection import wrap_client_connection_handler

random.seed(10)
TEST_DATA: "list[Any]" = [1, "string", True, {"key": "value"}, [1, 2, 3], None, "another string", (1, 2, 3)]


class StreamReader:
    def __init__(self) -> None:
        self.buffer = b""

    async def read(self) -> bytes:
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


@pytest.mark.parametrize("method", [("__iter__"), ("receive")])
async def test_chuncked_messages(method: str) -> None:
    """
    Simulate receiving messages in chunks of random size.
    """
    reader_1, reader_2 = StreamReader(), StreamReader()
    writer_1, writer_2 = StreamWriter(reader_2), StreamWriter(reader_1)
    connection_1 = wrap_client_connection_handler((reader_2, writer_2))
    connection_2 = wrap_client_connection_handler((reader_1, writer_1))
    data = [random.choice(TEST_DATA) for _ in range(1000)]
    received_data: list[Any] = []
    for value in data:
        connection_1.send_no_wait(value)
    if method == "__iter__":
        async for message in connection_2:
            received_data.append(message)
    else:
        with pytest.raises(ConnectionError):
            while True:
                received_data.append(await connection_2.receive())
    assert received_data == data
