from typing import Protocol

"""
These abstract classes enable test code type checking.
"""


class AbstractStreamReader(Protocol):
    async def read(self, n: int) -> bytes: ...  # pragma: no cover


class AbstractStreamWriter(Protocol):
    def write(self, data: bytes) -> None: ...  # pragma: no cover

    async def drain(self) -> None: ...  # pragma: no cover

    def close(self) -> None: ...  # pragma: no cover

    async def wait_closed(self) -> None: ...  # pragma: no cover
