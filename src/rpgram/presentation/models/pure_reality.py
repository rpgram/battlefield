from dataclasses import dataclass

from rpgram.domain.models.battle import EffectState


@dataclass
class HeroStateDTO:
    health: int
    effect_states: list[EffectState]
    # maybe better to move it to the world? or even to PureFabrication?
    previous: list[str] | None = None


@dataclass
class BattleDTO:
    hero: HeroStateDTO
    opponent: HeroStateDTO
