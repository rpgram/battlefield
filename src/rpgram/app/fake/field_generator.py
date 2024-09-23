import random
import string

from rpgram.app.fake.event_generator import generate_events
from rpgram.presentation.models.battle import (
    BattleField,
    Player,
    PlayerState,
    Suggestion,
    Move,
    ActionName,
)


def generate_random_string(length: int):
    return "".join(
        random.choice(string.ascii_lowercase) for _ in range(length)
    ).capitalize()


def generate_player() -> Player:
    state = random.randint(0, 2)
    hp = random.randint(0, 150)
    return Player(
        username=generate_random_string(10),
        state=PlayerState(state),
        health_points=hp,
        effects=[generate_random_string(5) for _ in range(3)],
    )


def generate_suggestion() -> Suggestion:
    button = random.randint(1, 4)
    action = random.choice([n for n in ActionName])
    return Suggestion(
        button=Move(button), steps_left=random.randint(1, 15), action=ActionName(action)
    )


def generate_moves() -> list[Move]:
    return [Move(random.randint(1, 4)) for _ in range(15)]


def generate_field() -> BattleField:
    return BattleField(
        player=generate_player(),
        opponent=generate_player(),
        next_move=[generate_suggestion() for _ in range(20)],
        complete_actions=generate_events(2),
        moves=generate_moves(),
    )
