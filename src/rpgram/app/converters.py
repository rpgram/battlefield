from adaptix.conversion import link
from adaptix.conversion import get_converter
from adaptix.provider import P

from rpgram.domain.errors import NoPlayer
from rpgram.domain.models.battle import Battle, RunningBattle, PlayerState


def check_no_player(player_state: PlayerState | None) -> PlayerState:
    if player_state is None:
        raise NoPlayer
    return player_state


battle_to_run = get_converter(
    Battle,
    RunningBattle,
    recipe=[
        link(P[Battle].opponent, P[RunningBattle].opponent, coercer=check_no_player)
    ],
)
