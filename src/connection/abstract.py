from typing import Protocol

"""
These abstract classes enable test code type checking.
"""

class AbstractStreamReader(Protocol):
    async def read(self) -> bytes:
        ...


class AbstractStreamWriter(Protocol):

    def write(self, data: bytes) -> None:
        pass

    async def drain(self) -> None:
        pass

    def close(self) -> None:
        pass

    async def wait_closed(self) -> None:
        pass