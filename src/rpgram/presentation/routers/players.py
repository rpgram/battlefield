from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from rpgram.app.services.players import get_players
from rpgram.data.player import PlayerRepo
from rpgram.presentation.models.players import PlayerDTO

players_router = APIRouter(prefix="/battle/players")


@players_router.get("")
@inject
async def get_all_players(players_repo: FromDishka[PlayerRepo]) -> list[PlayerDTO]:
    return get_players(players_repo)
