import time
from asyncio import sleep
from contextlib import suppress
from typing import Generator

from rpgram.domain.models.battle import (
    Battle,
    World,
    EffectState,
    HeroState,
    BattleResult,
)
from rpgram.domain.models.errors import BattleFinished


def effects_tick(hero_state: HeroState):
    for effect_state in hero_state.effect_states:
        hero_state.health += effect_state.effect.ticks[effect_state.tick].health_delta
        if len(effect_state.effect.ticks) - 1 > effect_state.tick:
            effect_state.tick += 1
        else:
            hero_state.effect_states.remove(effect_state)


def tick(battle_state: Battle, world: World) -> bool | None:
    battle_state.hero.health += world.move.opponent.opponent_health_delta
    battle_state.opponent.health += world.move.hero.opponent_health_delta
    if eh := world.move.hero.opponent_effect:
        battle_state.opponent.effect_states.append(EffectState(eh, 0))
        world.move.hero.opponent_effect = None
    if eo := world.move.opponent.opponent_effect:
        battle_state.hero.effect_states.append(EffectState(eo, 0))
        world.move.opponent.opponent_effect = None
    effects_tick(battle_state.hero)
    effects_tick(battle_state.opponent)
    if battle_state.hero.health <= 0:
        return False
    if battle_state.opponent.health <= 0:
        return True
    world.move.opponent.opponent_health_delta = 0
    world.move.hero.opponent_health_delta = 0
    return None


async def start_battle_loop_until_victory(
    battle_state: Battle,
    world: World,
    battle_stream: Generator[Battle, BattleResult | Battle, BattleResult],
):
    while True:
        ts = time.time()
        finish = tick(battle_state, world)
        if isinstance(finish, bool):
            battle_stream.send(BattleResult(finish))
            return
        battle_stream.send(battle_state)
        sleep_time = time.time() - ts + world.turn_time
        if sleep_time > 0:
            await sleep(sleep_time)
