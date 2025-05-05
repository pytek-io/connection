import pickle
import random
from typing import Any

from smart_connection.connection import FrameBuffer, create_frame

random.seed(10)


def test_buffer_feed() -> None:
    buffer = FrameBuffer()
    original_data = [random.random() for _ in range(100)]
    serialized_data = b"".join(create_frame(pickle.dumps(value)) for value in original_data)
    result: Any = []
    while serialized_data:
        chunk = random.randint(1, 10)
        buffer.feed(serialized_data[:chunk])
        serialized_data = serialized_data[chunk:]
        for message in buffer:
            result.append(pickle.loads(message))
    assert result == original_data
