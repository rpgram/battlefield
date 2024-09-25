import abc
from typing import Protocol, Any


class IMemoryEntityStorage(Protocol):

    @abc.abstractmethod
    def _reset_id(self) -> None: ...

    @property
    @abc.abstractmethod
    def generate_id(self) -> Any: ...

    @abc.abstractmethod
    def _next_id(self) -> None: ...
