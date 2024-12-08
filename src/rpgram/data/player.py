import abc
from contextlib import suppress
from typing import Any, Protocol, Never

from dishka import AnyOf

from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.interfaces.memory_storage import (
    IMemoryEntityStorage,
    IPlayerStorage,
    ID,
)
from rpgram.domain.player import Player, Hero
from rpgram.domain.utypes import PlayerId


class InMemoryPlayers(IMemoryEntityStorage[PlayerId], IPlayerStorage):

    @property
    def generated_id(self) -> PlayerId:
        return PlayerId(0)

    @abc.abstractmethod
    def _next_id(self) -> None:
        pass

    @abc.abstractmethod
    def _reset_id(self) -> None:
        pass


class PlayerStorage(InMemoryPlayers):
    def __init__(self) -> None:
        self.players: list[Player] = []
        self._reset_id()

    def _reset_id(self) -> None:
        self._id = PlayerId(0)

    def _next_id(self) -> None:
        if self._id == 2**16 - 1:
            self._reset_id()
        self._id = PlayerId(self._id + 1)

    @property
    def generated_id(self) -> PlayerId:
        self._next_id()
        return self._id


class FakeStorage(InMemoryPlayers):
    def __init__(self) -> None:
        self.players: list[Player] = [
            Player(PlayerId(1), "Usix", Hero(10, COMBO_ROOT)),
            Player(PlayerId(2), "Gentle", Hero(10, COMBO_ROOT)),
        ]

    @property
    def generated_id(self) -> PlayerId:
        raise NotImplemented

    def _next_id(self) -> None:
        pass

    def _reset_id(self) -> None:
        pass


class PlayerRepo:

    def __init__(self, storage: InMemoryPlayers) -> None:
        self._storage = storage

    def add_player(self, username: str, hero: Hero) -> PlayerId:
        _id = self._storage.generated_id
        player = Player(_id, username, hero)
        self._storage.players[_id] = player
        return _id

    def get_player(self, param: PlayerId | str) -> Player | None:
        with suppress(StopIteration):
            if isinstance(param, str):
                return next(p for p in self._storage.players if p.username == param)
            return next(p for p in self._storage.players if p.player_id == param)
        return None

    def get_players(self) -> list[Player]:
        return self._storage.players
