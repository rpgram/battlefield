import abc
from typing import Protocol

from rpgram.domain.models.battle import Battle

#
# class BattleRepo(Protocol):
#
#     @abc.abstractmethod
#     def start_battle(self, hero, opponent): ...
#
#     @abc.abstractmethod
#     def make_turn(self, battle_state): ...
#
#     @abc.abstractmethod
#     def get_battle(self, hero_id) -> Battle: ...
