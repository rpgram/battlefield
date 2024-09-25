import time
from asyncio import sleep

from rpgram.app.sse import Streamer
from rpgram.domain.models.battle import (
    Battle,
    World,
    EffectState,
    HeroState,
    BattleResult,
    RunningBattle,
)


def effects_tick(hero_state: HeroState) -> None:
    for effect_state in hero_state.effect_states:
        hero_state.health += effect_state.effect.ticks[effect_state.tick].health_delta
        if len(effect_state.effect.ticks) - 1 > effect_state.tick:
            effect_state.tick += 1
        else:
            hero_state.effect_states.remove(effect_state)


def tick(battle_state: RunningBattle, world: World) -> bool | None:

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
    battle_state: RunningBattle,
    world: World,
    streamer: Streamer,
    npc: bool = False,
) -> None:
    if battle_state.opponent is None:
        return
    while True:
        ts = time.time()
        finish = tick(battle_state, world)
        if isinstance(finish, bool):
            event: RunningBattle | BattleResult = BattleResult(finish)
        else:
            event = battle_state
        if battle_state.hero.player_id in streamer.battle_streams:
            streamer.send_battle(battle_state.hero.player_id, event)
        if npc is False and battle_state.opponent.player_id in streamer.battle_streams:
            streamer.send_battle(battle_state.opponent.player_id, event)
        # todo make victories

        sleep_time = time.time() - ts + world.turn_time
        if sleep_time > 0:
            await sleep(sleep_time)
