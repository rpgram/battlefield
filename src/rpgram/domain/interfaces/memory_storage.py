import abc
from typing import Protocol, Any, TypeVar

from rpgram.domain.player import Player


class IPlayerStorage(Protocol):
    """Dependency hint"""

    players: list[Player]


ID = TypeVar("ID", covariant=True)


class IMemoryEntityStorage(Protocol[ID]):

    @abc.abstractmethod
    def _reset_id(self) -> None: ...

    @property
    @abc.abstractmethod
    def generated_id(self) -> ID: ...

    @abc.abstractmethod
    def _next_id(self) -> None: ...
