from typing import NewType, TypeVar

from rpgram.domain.models.battle import BattleResult, RunningBattle

PlayerId = NewType("PlayerId", int)
BattleId = NewType("BattleId", int)
SSEEvent = TypeVar("SSEEvent", RunningBattle, BattleResult)
