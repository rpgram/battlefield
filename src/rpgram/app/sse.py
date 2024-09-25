import asyncio
import collections
from asyncio import QueueFull
from contextlib import suppress

from rpgram.domain.data.battle import BattleRepository
from rpgram.domain.errors import NoBattle
from rpgram.domain.models.battle import Battle
from rpgram.domain.types import PlayerId


class StreamerContext:

    def __init__(self, player_id: PlayerId, streamer: "Streamer"):
        self.player_id = player_id
        self.streamer = streamer

    def __enter__(self) -> None:
        self.streamer.init_stream(self.player_id)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.streamer.close_stream(self.player_id)


class Streamer:
    def __init__(self, battle_repo: BattleRepository) -> None:
        self.battle_streams: dict[PlayerId, asyncio.Queue] = collections.defaultdict(
            asyncio.Queue
        )
        self.battle_repo = battle_repo

    async def get_battle_state(self, player_id: PlayerId) -> Battle | None:
        battle = self.battle_repo.get_battle(player_id)
        if battle is None:
            raise NoBattle(player_id=player_id)
        q = self.battle_streams.get(player_id)
        if q is None:
            return None
        return await q.get()

    def send_battle(self, player_id: PlayerId, battle: Battle):
        with suppress(QueueFull):
            self.battle_streams[player_id].put_nowait(battle)

    def streamer_context(self, player_id: PlayerId) -> StreamerContext:
        return StreamerContext(player_id, self)

    def init_stream(self, player_id: PlayerId) -> None:
        self.battle_streams[player_id] = asyncio.Queue(maxsize=3)

    def close_stream(self, player_id: PlayerId) -> None:
        self.battle_streams.pop(player_id)
