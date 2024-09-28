from dataclasses import dataclass

from rpgram.domain.utypes import PlayerId


@dataclass
class PlayerDTO:
    username: str
    player_id: PlayerId
