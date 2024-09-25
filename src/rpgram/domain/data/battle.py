from rpgram.domain.interfaces.memory_storage import IMemoryEntityStorage
from rpgram.domain.models.battle import Battle
from rpgram.domain.types import BattleId, PlayerId
from rpgram.presentation.models.battle import Side


class BattleStorage(IMemoryEntityStorage):
    def __init__(self) -> None:
        self.battles: dict[BattleId, Battle] = {}
        self.players_battle: dict[PlayerId, tuple[BattleId, Side]] = {}
        self._reset_id()

    def _reset_id(self) -> None:
        self._battle_id_counter = BattleId(0)

    @property
    def generate_id(self) -> BattleId:
        self._next_id()
        return self._battle_id_counter

    def _next_id(self) -> None:
        if self._battle_id_counter == 2**32 - 1:
            self._reset_id()
            return
        self._battle_id_counter += 1


class BattleRepository:
    def __init__(self, storage: BattleStorage):
        self._storage = storage

    def add_battle(self, battle: Battle, player_id: PlayerId) -> BattleId:
        battle_id = self._storage.generate_id
        self._storage.battles[battle_id] = battle
        self.connect_side(player_id, Side.LEFT, battle_id)
        return battle_id

    def connect_side(
        self, player_id: PlayerId, side: Side, battle_id: BattleId
    ) -> None:
        self._storage.players_battle[player_id] = battle_id, side

    def get_battle(self, param: PlayerId | BattleId) -> Battle | None:
        if type(param) is BattleId:
            return self._storage.battles.get(param)
        battle_id = self._storage.players_battle.get(param)
        if battle_id is None:
            return None
        return self._storage.battles.get(battle_id[0])

    def remove_battle(self, battle_id: BattleId) -> None:
        pb = self._storage.players_battle
        for i in pb:
            if pb[i][0] == battle_id:
                pb.pop(i)
        self._storage.battles.pop(battle_id)

    # def get_opponents(self, battle_id: BattleId) -> tuple[PlayerId, PlayerId]:
    #     pb = self._storage.players_battle
    #     player_id = None
    #     for i in pb:
    #         if pb[i][0] == battle_id:
    #             if player_id is None:
    #                 player_id

    # def set_player(self, player):
