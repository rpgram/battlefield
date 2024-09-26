from dataclasses import dataclass

from rpgram.domain.models.battle import EffectState, Hint
from rpgram.domain.utypes import BattleId
from rpgram.presentation.models import battle


@dataclass
class PlayerStateDTO:
    hints: list[Hint]
    previous: str | None = None


@dataclass
class HeroStateDTO:
    health: int
    effect_states: list[EffectState]
    # maybe better to move it to the world? or even to PureFabrication?
    plays: PlayerStateDTO


@dataclass
class BattleDTO:
    hero: HeroStateDTO
    opponent: HeroStateDTO


@dataclass
class PlayerDTO:
    username: str
    health_points: int
    effects: list[str]
    state: battle.PlayerState = battle.PlayerState(0)


@dataclass
class BattleFieldDTO:
    """Already done client conversions"""

    battle_id: BattleId
    player: PlayerDTO
    opponent: PlayerDTO | None
    next_move: list[battle.Suggestion]
    complete_actions: list[battle.BattleEvent]
    moves: list[battle.Move]
