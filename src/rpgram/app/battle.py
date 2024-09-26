import asyncio

from rpgram.domain.algos.loop import battle_loop_until_victory_or_timeout
from rpgram.domain.models.battle import (
    Battle,
    World,
    HeroState,
    PlayInfo,
    PlayerState,
)

#
# class BattleRunner:
#
#     def __call__(
#         self,
#         battle: Battle,
#         world: World,
#     ) -> None:
#         battle.hero = PlayerState(HeroState(50, []), PlayInfo())
#         battle.opponent = PlayerState(HeroState(50, []), PlayInfo())
#         asyncio.create_task(battle_loop_until_victory_or_timeout(battle, world))
