from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from sse_starlette import EventSourceResponse
from starlette import status

from rpgram.app.services.action import ActionInteractor
from rpgram.app.services.battle import BattleService
from rpgram.app.sse import Streamer
from rpgram.domain.errors import AlreadyInBattle, NoPlayer, NoBattle
from rpgram.domain.models.battle import RunningBattle, SSEEvent
from rpgram.domain.utypes import PlayerId, BattleId
from rpgram.presentation.models.converter import (
    convert_battle_to_field_dto,
)
from rpgram.presentation.models.pure_reality import BattleFieldDTO

battle_router = APIRouter(prefix="/battle")


@battle_router.post("")
@inject
async def start_battle(
    player_id: PlayerId,
    opponent_id: PlayerId,
    streamer: FromDishka[Streamer[SSEEvent]],
    battle_service: FromDishka[BattleService],
) -> BattleId:
    try:
        return battle_service.start_battle(player_id, opponent_id, streamer)
    except AlreadyInBattle as aib_exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(aib_exc))
    except NoPlayer as np_exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(np_exc))
    except NoBattle:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create battle"
        )


# @battle_router.get("")
# @inject
# async def get_battle(
#     player_id: PlayerId, battle_service: FromDishka[BattleService]
# ) -> BattleDTO:
#     try:
#         battle = battle_service.get_battle(player_id)
#     except NoBattle as nb_exc:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, str(nb_exc))
#     return convert_battle_to_dto(battle)


# @battle_router.get("/sse")
# @inject
# async def get_battle_sse(
#     battle: FromDishka[Battle],
#     world: FromDishka[World],
# ) -> EventSourceResponse:
#
#     last_sent = copy.deepcopy(battle)
#
#     async def stream(sleep_time: float) -> AsyncGenerator[BattleDTO, None]:
#         yield convert_battle_to_dto(battle)
#         while True:
#             if battle != last_sent:
#                 yield convert_battle_to_dto(battle)
#                 last_sent.hero = copy.deepcopy(battle.hero)
#                 last_sent.opponent = copy.deepcopy(battle.opponent)
#             await asyncio.sleep(sleep_time)
#
#     return EventSourceResponse(stream(world.turn_time))


@battle_router.post("/{key}")
@inject
async def act_in_battle(
    key: str, player_id: PlayerId, action_interactor: FromDishka[ActionInteractor]
) -> None:
    # todo return response
    try:
        action_interactor(key, player_id)
    except NoBattle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No battle.")


@battle_router.get("/client")
@inject
async def clients_battle(
    player_id: PlayerId, battle_service: FromDishka[BattleService]
) -> BattleFieldDTO:
    try:
        battle = battle_service.get_battle(player_id)
    except NoBattle as nb_exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(nb_exc))
    return convert_battle_to_field_dto(battle)


@battle_router.get("/client/sse")
@inject
async def get_battle_sse_client(
    player_id: PlayerId, streamer: FromDishka[Streamer[SSEEvent]]
) -> EventSourceResponse:
    async def event_streamer():
        with streamer.streamer_context(player_id):
            while True:
                try:
                    event = await streamer.get_battle_state(player_id)
                except NoBattle:
                    break
                if event is None:
                    break
                if isinstance(event, RunningBattle):
                    yield {
                        "event": "state",
                        "data": asdict(convert_battle_to_field_dto(event)),
                    }
                else:
                    side = "left" if event.hero_victory is True else "right"
                    yield {"event": "congrats", "data": f"{side} side wins"}
                    break

    return EventSourceResponse(event_streamer())
