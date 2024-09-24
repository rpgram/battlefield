from typing import Generator, TypeVar

from rpgram.domain.models.battle import Battle, BattleResult, World


BattleStream = TypeVar(
    "BattleStream", bound=Generator[Battle | BattleResult, BattleResult | Battle, None]
)


class Streamer:
    def __init__(self, battle_stream: BattleStream):
        self.battle_stream = battle_stream

    def view(self):
        return next()


def battle_sse_generator() -> BattleStream:

    while True:
        event: Battle | BattleResult = yield
        # if isinstance(event, BattleResult):
        #     return event
        yield event
