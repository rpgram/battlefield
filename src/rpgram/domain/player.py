from dataclasses import dataclass

from rpgram.domain.models.battle import ComboNode
from rpgram.domain.types import PlayerId


@dataclass
class Hero:
    health: int
    combo_tree: ComboNode


@dataclass
class Player:
    player_id: PlayerId
    username: str
    hero: Hero
