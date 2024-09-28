import asyncio
import collections
from asyncio import QueueFull
from contextlib import suppress
from types import TracebackType
from typing import Generic

from rpgram.data.battle import BattleRepository
from rpgram.domain.errors import NoBattle
from rpgram.domain.models.battle import SSEEvent
from rpgram.domain.utypes import PlayerId


class Streamer:
    def __init__(self, battle_repo: BattleRepository) -> None:
        self.battle_streams: dict[PlayerId, asyncio.Queue[SSEEvent]] = {}
        self.battle_repo = battle_repo

    async def get_battle_state(self, player_id: PlayerId) -> SSEEvent | None:
        battle = self.battle_repo.get_battle(player_id)
        if battle is None:
            raise NoBattle(player_id=player_id)
        q = self.battle_streams.get(player_id)
        if q is None:
            return None
        return await q.get()

    def send_battle(self, player_id: PlayerId, event: SSEEvent) -> None:
        with suppress(QueueFull):
            self.battle_streams[player_id].put_nowait(event)

    def streamer_context(self, player_id: PlayerId) -> "StreamerContext":
        return StreamerContext(player_id, self)

    def init_stream(self, player_id: PlayerId) -> None:
        self.battle_streams[player_id] = asyncio.Queue(maxsize=3)

    def close_stream(self, player_id: PlayerId) -> None:
        self.battle_streams.pop(player_id)


class StreamerContext:

    def __init__(self, player_id: PlayerId, streamer: Streamer):
        self.player_id = player_id
        self.streamer = streamer

    def __enter__(self) -> None:
        self.streamer.init_stream(self.player_id)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.streamer.close_stream(self.player_id)
