from rpgram.app.services.battle import BattleService
from rpgram.data.battle import BattleRepository
from rpgram.domain.errors import NoPlayer
from rpgram.domain.utypes import PlayerId
from rpgram.presentation.models.converter import convert_battle_to_dto_by_side
from rpgram.presentation.models.pure_reality import BattleFieldDTO


class BattlePollInteractor:
    def __init__(self, battle_repo: BattleRepository, battle_service: BattleService):
        self.battle_repo = battle_repo
        self.battle_service = battle_service

    def execute(self, player_id: PlayerId) -> BattleFieldDTO:
        battle = self.battle_service.get_battle(player_id)
        side = self.battle_repo.get_players_side(player_id)
        if side is None:
            raise NoPlayer
        dto = convert_battle_to_dto_by_side(battle, side)
        return dto
