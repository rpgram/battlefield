import asyncio
import copy
from dataclasses import asdict
from typing import Generator

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from rpgram.app.battle import BattleRunner
from rpgram.app.services.action import ActionInteractor
from rpgram.app.sse import BattleStream
from rpgram.domain.models.battle import Battle, World, BattleResult
from rpgram.presentation.models.converter import convert_battle_to_dto
from rpgram.presentation.models.pure_reality import BattleDTO

battle_router = APIRouter(prefix="/battle")


@battle_router.post("")
@inject
async def start_battle(
    battle_runner: FromDishka[BattleRunner],
    battle: FromDishka[Battle],
    world: FromDishka[World],
    sse_gen: FromDishka[BattleStream],
):
    battle_runner(battle, world, sse_gen)


@battle_router.get("")
@inject
async def get_battle(battle: FromDishka[Battle]) -> BattleDTO:
    return convert_battle_to_dto(battle)


@battle_router.get("/sse")
@inject
async def get_battle_sse(
    battle: FromDishka[Battle],
    world: FromDishka[World],
):

    last_sent = copy.deepcopy(battle)

    async def stream(sleep_time: float):
        # battle_updater = (
        #     convert_battle_to_dto(e) if isinstance(e, Battle) else e for e in sse_gen
        # )
        yield convert_battle_to_dto(battle)
        while True:
            if battle != last_sent:
                yield convert_battle_to_dto(battle)
                last_sent.hero = copy.deepcopy(battle.hero)
                last_sent.opponent = copy.deepcopy(battle.opponent)
            await asyncio.sleep(sleep_time)

    return EventSourceResponse(stream(world.turn_time))


@battle_router.post("/{key}")
@inject
async def act_in_battle(
    key: str, action_interactor: FromDishka[ActionInteractor], by_hero: bool
):
    action_interactor(key, by_hero)
