import asyncio

from rpgram.domain.algos.loop import start_battle_loop_until_victory
from rpgram.domain.models.battle import (
    Battle,
    World,
    HeroState,
    PlayInfo,
    PlayerState,
)


class BattleRunner:

    def __call__(
        self,
        battle: Battle,
        world: World,
    ) -> None:
        battle.hero = PlayerState(HeroState(50, []), PlayInfo())
        battle.opponent = PlayerState(HeroState(50, []), PlayInfo())
        asyncio.create_task(start_battle_loop_until_victory(battle, world))
