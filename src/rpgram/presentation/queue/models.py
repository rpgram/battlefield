from adaptix.conversion import get_converter
from pydantic import BaseModel

from rpgram.app.interactors.create_battle import StartBattlePlayerDTO
from rpgram.domain.utypes import PlayerId


class HeroDTO(BaseModel):
    health: int
    combo_root_id: int


class PlayerDTO(BaseModel):
    name: str
    player_id: PlayerId
    hero: HeroDTO


from_stream_player_converter = get_converter(PlayerDTO, StartBattlePlayerDTO)
