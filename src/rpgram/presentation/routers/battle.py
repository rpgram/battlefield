import logging
import time
from dataclasses import asdict
from typing import AsyncGenerator, Any

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from sse_starlette import EventSourceResponse
from starlette import status
from starlette.responses import JSONResponse

from rpgram.app.interactors.create_battle import StartBattleMicroservices
from rpgram.presentation.queue import models

from rpgram.app.interactors.process import BattlePollInteractor
from rpgram.app.services.action import ActionInteractor
from rpgram.app.services.battle import BattleService
from rpgram.app.sse import Streamer
from rpgram.domain.errors import AlreadyInBattle, NoPlayer, NoBattle
from rpgram.domain.models.battle import (
    RunningBattle,
    BattleResult,
    Battle,
    BattleStarted,
)
from rpgram.domain.utypes import PlayerId, BattleId
from rpgram.presentation.models.battle import WaitingBattle
from rpgram.presentation.models.converter import (
    convert_battle_to_field_dto,
    waiting_battles_converter,
    convert_battle_to_dto_by_side,
)
from rpgram.presentation.models.pure_reality import BattleFieldDTO
from rpgram.presentation.queue.models import from_stream_player_converter


logger = logging.getLogger(__name__)

battle_router = APIRouter(prefix="/battle")


@battle_router.post("")
@inject
async def start_battle(
    player_id: PlayerId,
    streamer: FromDishka[Streamer],
    battle_service: FromDishka[BattleService],
    opponent_id: PlayerId | None = None,
) -> BattleStarted:
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


@battle_router.get("")
@inject
async def get_battles(battle_service: FromDishka[BattleService]) -> list[WaitingBattle]:
    return [waiting_battles_converter(b) for b in battle_service.get_all_battles()]


@battle_router.delete("/leave")
@inject
async def leave_battle(
    player_id: PlayerId, battle_service: FromDishka[BattleService]
) -> bool:
    try:
        battle_service.leave_battle(player_id)
        return True
    except NoBattle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No battle for player")


@battle_router.post("/connect")
@inject
async def connect_to_battle(
    player_id: PlayerId,
    battle_id: BattleId,
    battle_service: FromDishka[BattleService],
    streamer: FromDishka[Streamer],
) -> int:
    return battle_service.connect(player_id, battle_id, streamer)


@battle_router.post("/instant")
@inject
async def start_by_micro(
    player: models.PlayerDTO,
    opponent: models.PlayerDTO,
    interactor: FromDishka[StartBattleMicroservices],
):
    return interactor.execute(
        from_stream_player_converter(player), from_stream_player_converter(opponent)
    )


@battle_router.post("/{key}")
@inject
async def act_in_battle(
    key: str, user_key: str, action_interactor: FromDishka[ActionInteractor]
) -> None:
    try:
        logger.debug("In try...")
        action_interactor.execute(key, user_key)
    except NoBattle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No battle.")


@battle_router.get("/client")
@inject
async def clients_battle(
    player_id: PlayerId, interactor: FromDishka[BattlePollInteractor]
) -> BattleFieldDTO:
    try:
        dto = interactor.execute(player_id)
    except (NoBattle, NoPlayer) as nb_exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(nb_exc))
    if dto.opponent is None:
        raise HTTPException(status.HTTP_202_ACCEPTED, "Not started yet")
    return dto


@battle_router.get("/result")
@inject
async def get_battle_result(
    player_id: PlayerId, battle_service: FromDishka[BattleService]
) -> BattleResult:
    try:
        battle_result = battle_service.check_battle_result(player_id)
    except NoBattle as nb_exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(nb_exc))
    return battle_result


@battle_router.get("/client/sse")
@inject
async def get_battle_sse_client(
    player_id: PlayerId, streamer: FromDishka[Streamer]
) -> EventSourceResponse:

    async def event_streamer() -> AsyncGenerator[dict[str, Any], None]:
        with streamer.streamer_context(player_id):
            while True:
                try:
                    event = await streamer.get_battle_state(player_id)
                except NoBattle:
                    break
                if isinstance(event, RunningBattle):
                    yield {
                        "event": "state",
                        "data": asdict(convert_battle_to_field_dto(event)),
                    }
                elif isinstance(event, BattleResult):
                    side = "left" if event.hero_result.win is True else "right"
                    yield {"event": "congrats", "data": f"{side} side wins"}
                    break
                else:
                    break

    return EventSourceResponse(event_streamer())
