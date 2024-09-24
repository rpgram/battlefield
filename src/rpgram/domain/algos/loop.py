import time
from asyncio import sleep

from rpgram.domain.models.battle import (
    Battle,
    World,
    EffectState,
    HeroState,
)


def effects_tick(hero_state: HeroState) -> None:
    for effect_state in hero_state.effect_states:
        hero_state.health += effect_state.effect.ticks[effect_state.tick].health_delta
        if len(effect_state.effect.ticks) - 1 > effect_state.tick:
            effect_state.tick += 1
        else:
            hero_state.effect_states.remove(effect_state)


def tick(battle_state: Battle, world: World) -> bool | None:
    battle_state.hero.unit_state.health += world.move.opponent.opponent_health_delta
    battle_state.opponent.unit_state.health += world.move.hero.opponent_health_delta
    if eh := world.move.hero.opponent_effect:
        battle_state.opponent.unit_state.effect_states.append(EffectState(eh, 0))
        world.move.hero.opponent_effect = None
    if eo := world.move.opponent.opponent_effect:
        battle_state.hero.unit_state.effect_states.append(EffectState(eo, 0))
        world.move.opponent.opponent_effect = None
    effects_tick(battle_state.hero.unit_state)
    effects_tick(battle_state.opponent.unit_state)
    if battle_state.hero.unit_state.health <= 0:
        return False
    if battle_state.opponent.unit_state.health <= 0:
        return True
    world.move.opponent.opponent_health_delta = 0
    world.move.hero.opponent_health_delta = 0
    return None


async def start_battle_loop_until_victory(
    battle_state: Battle,
    world: World,
) -> None:
    while True:
        ts = time.time()
        finish = tick(battle_state, world)
        # todo make victories
        if isinstance(finish, bool):
            break
        sleep_time = time.time() - ts + world.turn_time
        if sleep_time > 0:
            await sleep(sleep_time)
