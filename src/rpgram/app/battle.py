import asyncio
from typing import Generator

from rpgram.domain.algos.loop import start_battle_loop_until_victory
from rpgram.domain.models.battle import Battle, World, BattleResult, HeroState


class BattleRunner:
    # def __init__(self, battle_service: BattleService, world: World):
    #     self.world = world
    #     self.battle_service = battle_service

    def __call__(
        self,
        battle: Battle,
        world: World,
        stream: Generator[Battle, Battle | BattleResult, BattleResult],
    ):
        battle.hero = HeroState(50, [])
        battle.opponent = HeroState(15, [])
        try:
            stream.send(battle)
        except TypeError:
            next(stream)
            stream.send(battle)
        asyncio.create_task(start_battle_loop_until_victory(battle, world, stream))
