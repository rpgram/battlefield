import asyncio

from rpgram.domain.algos.loop import start_battle_loop_until_victory
from rpgram.domain.models.battle import (
    Battle,
    World,
    BattleResult,
    HeroState,
    PlayInfo,
    PlayerState,
)


class BattleRunner:
    # def __init__(self, battle_service: BattleService, world: World):
    #     self.world = world
    #     self.battle_service = battle_service

    def __call__(
        self,
        battle: Battle,
        world: World,
    ):
        battle.hero = PlayerState(HeroState(50, []), PlayInfo())
        battle.opponent = PlayerState(HeroState(50, []), PlayInfo())
        asyncio.create_task(start_battle_loop_until_victory(battle, world))
