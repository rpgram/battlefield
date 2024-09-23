import asyncio

from rpgram.domain.algos.loop import start_battle_loop_until_victory


class BattleRunner:
    # def __init__(self, battle_service: BattleService, world: World):
    #     self.world = world
    #     self.battle_service = battle_service

    def __call__(self, battle, world):
        asyncio.create_task(start_battle_loop_until_victory(battle, world))
