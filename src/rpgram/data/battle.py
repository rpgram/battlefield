import logging

from rpgram.domain.errors import NoBattle
from rpgram.domain.interfaces.memory_storage import IMemoryEntityStorage
from rpgram.domain.models.battle import (
    Battle,
    CreateBattle,
    RunningBattle,
    RelatedBattleResult,
    BattleResult,
)
from rpgram.domain.utypes import BattleId, PlayerId
from rpgram.presentation.models.battle import Side


logger = logging.getLogger(__name__)


class BattleStorage(IMemoryEntityStorage[BattleId]):
    def __init__(self) -> None:
        # todo separate this types storages?
        self.battles: dict[BattleId, Battle | RunningBattle] = {}
        self.players_battle: dict[PlayerId, tuple[BattleId, Side]] = {}
        # player_id, is_hero, win
        self.battle_results: dict[BattleId, tuple[tuple[PlayerId, bool, bool], ...]] = (
            {}
        )
        self.players_keys: dict[str, PlayerId] = {}
        self._reset_id()

    def _reset_id(self) -> None:
        self._battle_id_counter = BattleId(0)

    @property
    def generated_id(self) -> BattleId:
        self._next_id()
        return self._battle_id_counter

    def _next_id(self) -> None:
        if self._battle_id_counter == 2**32 - 1:
            self._reset_id()
        self._battle_id_counter = BattleId(self._battle_id_counter + 1)


class BattleRepository:
    def __init__(self, storage: BattleStorage) -> None:
        self._storage = storage

    def upgrade_battle(self, battle: RunningBattle) -> None:
        previous = self.get_battle(battle_id=battle.battle_id)
        if previous is None:
            raise NoBattle(battle.battle_id)
        self._storage.battles[battle.battle_id] = battle

    def add_battle(self, battle: CreateBattle) -> BattleId:
        battle_id = self._storage.generated_id
        if battle.opponent is None:
            to_insert = Battle(hero=battle.hero, opponent=None, battle_id=battle_id)
        else:
            to_insert = RunningBattle(
                hero=battle.hero, opponent=battle.opponent, battle_id=battle_id
            )
        self._storage.battles[battle_id] = to_insert
        self.connect_side(battle.hero.player_id, Side.LEFT, battle_id)
        return battle_id

    def connect_side(
        self, player_id: PlayerId, side: Side, battle_id: BattleId
    ) -> None:
        self._storage.players_battle[player_id] = battle_id, side

    def get_players_side(self, player_id: PlayerId) -> Side | None:
        players_position = self._storage.players_battle.get(player_id)
        if players_position is None:
            return None
        return players_position[1]

    def get_battle(
        self, player_id: PlayerId | None = None, battle_id: BattleId | None = None
    ) -> Battle | RunningBattle | None:
        logger.debug("Getting battle", extra={"storage": self._storage.players_battle})
        if battle_id:
            return self._storage.battles.get(battle_id)
        if player_id is None:
            return None
        player_position = self._storage.players_battle.get(player_id)
        if player_position is None:
            return None
        return self._storage.battles.get(player_position[0])

    def remove_battle(self, battle_id: BattleId) -> None:
        pb = self._storage.players_battle
        keys_to_rm = set()
        for i in pb:
            if pb[i][0] == battle_id:
                keys_to_rm.add(i)
        for i in keys_to_rm:
            pb.pop(i, None)
        self._storage.battles.pop(battle_id, None)

    def set_battle_result(
        self, battle_id: BattleId, result: RelatedBattleResult
    ) -> None:
        for_one_of = self._storage.battle_results.get(battle_id)
        result_in_storage = result.player_id, result.is_hero, result.win
        if for_one_of is None:
            self._storage.battle_results[battle_id] = (result_in_storage,)
        else:
            self._storage.battle_results[battle_id] = for_one_of[0], result_in_storage

    def get_battle_result(self, player_id: PlayerId) -> BattleResult | None:
        res_storage = self._storage.battle_results
        battle_id = BattleId(-1)
        for k in res_storage:
            for p, *_ in res_storage[k]:
                if p == player_id:
                    # todo make this ring check(save ts)
                    if k > battle_id:
                        battle_id = k
        if battle_id == -1:
            return None
        hero_result = opponent_result = None
        for p, h, r in res_storage[battle_id]:
            if h:
                hero_result = RelatedBattleResult(p, h, r)
            else:
                opponent_result = RelatedBattleResult(p, h, r)
        if hero_result and opponent_result:
            return BattleResult(battle_id, hero_result, opponent_result)
        return None

    def update_keys(self, player_id: PlayerId, key: str):
        self._storage.players_keys[key] = player_id

    def get_player_id(self, key: str) -> PlayerId | None:
        logging.debug("Storage query", extra={"storage": self._storage.players_keys})
        return self._storage.players_keys.get(key)

    # def get_opponents(self, battle_id: BattleId) -> tuple[PlayerId, PlayerId]:
    #     pb = self._storage.players_battle
    #     player_id = None
    #     for i in pb:
    #         if pb[i][0] == battle_id:
    #             if player_id is None:
    #                 player_id

    # def set_player(self, player):
    def get_battles(self) -> list[Battle | RunningBattle]:
        return list(self._storage.battles.values())
