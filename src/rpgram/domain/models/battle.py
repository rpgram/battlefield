from dataclasses import dataclass, asdict, is_dataclass
from typing import TypeVar

from rpgram.domain.utypes import BattleId, PlayerId


@dataclass
class EffectTick:
    health_delta: int


@dataclass
class Effect:
    name: str
    ticks: list[EffectTick]
    # todo here are stacks also


@dataclass
class EffectState:
    effect: Effect
    tick: int


@dataclass
class Action:
    name: str
    opponent_health_delta: int
    opponent_effect: Effect | None


@dataclass
class Move:
    hero: Action
    opponent: Action


@dataclass
class World:
    move: Move
    turn_time: int = 3


@dataclass
class Hint:
    key: str
    distance: int
    action_name: str


class ComboNode:
    """todo Would be nice two rewrite combo with some memorable format, but perf is perf"""

    def __init__(
        self,
        value: str,
        children: list["ComboNode"],
        prefix: str = "",
        distance: int = 0,
        action: Action | None = None,
    ):
        self._distance = distance
        self._children = children
        self.value = value
        self.combo = prefix + value
        self.action = action
        self.hints: list[Hint] = []
        self._next_combos_with_distance(self._children)

    def propagate_combo(self, call: str, root: "ComboNode") -> "ComboNode":
        for c in self._children:
            if c.value == call:
                return c
        for c in root._children:
            if c.value == call:
                return c
        return root

    @property
    def is_leaf(self) -> bool:
        if not self._children:
            assert self.action is not None
            return True
        return False

    def _next_combos_with_distance(self, children: list["ComboNode"]) -> None:
        for c in children:
            if c.is_leaf and c.action:
                self.hints.append(
                    Hint(c.value, c._distance - self._distance, c.action.name)
                )
            else:
                self._next_combos_with_distance(c._children)


@dataclass
class HeroState:
    health: int
    effect_states: list[EffectState]  # later will be setup as buffs are before!
    # maybe better to move it to the world? or even to PureFabrication?


@dataclass
class PlayInfo:
    combo_tree: ComboNode
    previous: ComboNode | None = None


@dataclass
class PlayerState:
    unit_state: HeroState
    plays: PlayInfo
    player_id: PlayerId
    # username: str = "TESTER"  # it will be id


@dataclass
class CreateBattle:
    hero: PlayerState
    opponent: PlayerState | None


@dataclass
class Battle(CreateBattle):
    battle_id: BattleId

    def __eq__(self, other: object) -> bool:
        if is_dataclass(other) and not isinstance(other, type):
            return asdict(self) == asdict(other)
        return super().__eq__(other)


@dataclass
class RunningBattle(Battle):
    opponent: PlayerState


@dataclass
class BattleResult:
    hero_victory: bool
    #  todo here is award also


SSEEvent = TypeVar("SSEEvent", RunningBattle, BattleResult)
