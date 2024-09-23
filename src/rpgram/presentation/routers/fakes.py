from fastapi import APIRouter

from rpgram.app.fake.field_generator import generate_field
from rpgram.presentation.models.battle import BattleField

fake_router = APIRouter(prefix="/fake")


@fake_router.get("/battle")
async def fake_battle_events() -> BattleField:
    return generate_field()
