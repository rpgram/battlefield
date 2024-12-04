import abc
from typing import Protocol

from rpgram.domain.models.battle import BattleResult


class StatisticsGateway(Protocol):

    @abc.abstractmethod
    async def battle_finished(self, battle_result: BattleResult) -> None: ...
