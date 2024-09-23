from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from rpgram.app.battle import BattleRunner
from rpgram.app.services.action import ActionInteractor
from rpgram.domain.models.battle import Battle, World
from rpgram.presentation.models.converter import convert_battle_to_dto
from rpgram.presentation.models.pure_reality import BattleDTO

battle_router = APIRouter(prefix="/battle")


@battle_router.post("")
@inject
async def start_battle(
    battle_runner: FromDishka[BattleRunner],
    battle: FromDishka[Battle],
    world: FromDishka[World],
):
    battle_runner(battle, world)


@battle_router.get("")
@inject
async def get_battle(battle: FromDishka[Battle]) -> BattleDTO:
    return convert_battle_to_dto(battle)


@battle_router.post("/{key}")
@inject
async def act_in_battle(
    key: str, action_interactor: FromDishka[ActionInteractor], by_hero: bool
):
    action_interactor(key, by_hero)
