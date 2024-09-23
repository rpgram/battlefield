from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    LEFT = 1
    RIGHT = 2


class Action(Enum):
    CIRCLE = 1
    TRIANGLE = 2
    CROSS = 3
    SQUARE = 4


class Combo(Enum):
    HIT = 0


class ActionName(str, Enum):
    SWEEP = "SWEEP"
    FREEZE = "FREEZE"
    STUN = "STUN"
    HIT = "HIT"
    PIERCE = "PIERCE"


@dataclass
class BattleEvent:
    side: Side
    action: Action | Combo
    eid: int


class Move(Enum):
    CIRCLE = 1
    TRIANGLE = 2
    CROSS = 3
    SQUARE = 4


@dataclass
class Suggestion:
    button: Move
    steps_left: int  # later will encounter casting
    action: ActionName


class PlayerState(Enum):
    ALIVE = 0
    MUTED = 1
    PREPARATION = 2


@dataclass
class Player:
    username: str
    state: PlayerState
    health_points: int
    effects: list


@dataclass
class BattleField:
    player: Player
    opponent: Player
    next_move: list[Suggestion]
    complete_actions: list[BattleEvent]
    moves: list[Move]
