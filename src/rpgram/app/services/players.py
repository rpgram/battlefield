from rpgram.data.player import PlayerRepo
from rpgram.presentation.models.players import PlayerDTO


def get_players(player_repo: PlayerRepo) -> list[PlayerDTO]:
    return [
        PlayerDTO(username=p.username, player_id=p.player_id)
        for p in player_repo.get_players()
    ]


