from dataclasses import dataclass, asdict


@dataclass
class EffectTick:
    health_delta: int


@dataclass
class Effect:
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


class ComboNode:
    """Would be nice two rewrite this with some memorable format, but perf is perf"""

    def __init__(
        self,
        value: str,
        children: list["ComboNode"],
        prefix: str = "",
        action: Action | None = None,
    ):
        self.children = children
        self.value = value
        self.combo = prefix + value
        self.action = action

    def propagate_combo(self, call: str, root: "ComboNode") -> list["ComboNode"]:
        next_combos = []
        for c in self.children:
            if c.value == call:
                next_combos.append(c)
        if next_combos:
            return next_combos
        for c in root.children:
            if c.value == call:
                next_combos.append(c)
        if next_combos:
            return next_combos
        return root.children

    @property
    def is_leaf(self) -> bool:
        if not self.children:
            assert self.effect
            return True
        return False

    @property
    def effect(self) -> Action:
        return self.action

    @property
    def next_combos_with_distance(self): ...


@dataclass
class HeroState:
    health: int
    effect_states: list[EffectState]
    # maybe better to move it to the world? or even to PureFabrication?
    previous: list[ComboNode] | None = None


@dataclass
class Battle:
    hero: HeroState
    opponent: HeroState

    def __eq__(self, other: "Battle"):
        return asdict(self) == asdict(other)


@dataclass
class BattleResult:
    hero_victory: bool
    #  todo here is award also
