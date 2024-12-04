import asyncio
import time
from asyncio import sleep

from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleRepository
from rpgram.domain.apis import StatisticsGateway
from rpgram.domain.models.battle import (
    Battle,
    World,
    EffectState,
    HeroState,
    BattleResult,
    RunningBattle,
    RelatedBattleResult,
    SSEEvent,
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

    world.move.opponent.opponent_health_delta = 0
    world.move.hero.opponent_health_delta = 0

    if battle_state.hero.unit_state.health <= 0:
        return False
    if battle_state.opponent.unit_state.health <= 0:
        return True
    return None


async def battle_loop_until_victory_or_timeout(
    battle_state: RunningBattle,
    world: World,
    streamer: Streamer,
    battle_repo: BattleRepository,
    stats_gate: StatisticsGateway,
    npc: bool = False,
) -> None:
    # if battle_state.opponent is None:
    #     return
    if not npc:
        await asyncio.sleep(world.battle_preparation)
    ts = time.time()
    deadline = ts + world.battle_timeout_sec
    while True:
        finish = tick(battle_state, world)
        time_is_over = time.time() > deadline
        result_event = None
        battle_event = None
        if isinstance(finish, bool) or time_is_over:
            hero_result = RelatedBattleResult(
                battle_state.hero.player_id,
                is_hero=True,
                win=finish or time_is_over,
            )
            opponent_result = RelatedBattleResult(
                battle_state.opponent.player_id,
                is_hero=False,
                win=not finish or time_is_over,
            )
            result_event = BattleResult(
                battle_state.battle_id, hero_result, opponent_result
            )
            battle_repo.set_battle_result(battle_state.battle_id, hero_result)
            battle_repo.set_battle_result(battle_state.battle_id, opponent_result)
            battle_repo.remove_battle(battle_state.battle_id)
        else:
            battle_event = battle_state
        hero_streaming = battle_state.hero.player_id in streamer.battle_streams
        opponent_streaming = (
            npc is False and battle_state.opponent.player_id in streamer.battle_streams
        )
        if result_event is not None:
            if hero_streaming:
                streamer.send_battle(battle_state.hero.player_id, result_event)
            if opponent_streaming:
                streamer.send_battle(battle_state.opponent.player_id, result_event)
            await stats_gate.battle_finished(result_event)
            return
        if battle_event is not None:
            if hero_streaming:
                streamer.send_battle(battle_state.hero.player_id, battle_event)
            if opponent_streaming:
                streamer.send_battle(battle_state.opponent.player_id, battle_event)
        sleep_time = time.time() - ts + world.turn_time
        if sleep_time > 0:
            await sleep(sleep_time)
        ts = time.time()
