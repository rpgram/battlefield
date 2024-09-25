from typing import Any

from rpgram.domain.types import PlayerId, BattleId


class AlreadyInBattle(Exception):
    def __init__(self, player_id: PlayerId) -> None:
        self.player_id = player_id

    def __str__(self) -> str:
        return f"""Player {self.player_id} is in battle."""


class NoPlayer(Exception):
    def __init__(self, param: Any) -> None:
        self.param = param

    def __str__(self):
        return f"""No player characterized by {self.param}."""


class NoBattle(Exception):
    def __init__(
        self, battle_id: BattleId | None = None, player_id: PlayerId | None = None
    ) -> None:
        assert battle_id or player_id
        self._id = battle_id
        self.player_id = player_id

    def __str__(self):
        if self._id:
            return f"""No battle with {self._id}."""
        return f"""No battle with player {self.player_id}"""
