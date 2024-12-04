import asyncio
import time

from rpgram.app.converters import battle_to_run
from rpgram.app.sse import Streamer
from rpgram.domain.algos.loop import battle_loop_until_victory_or_timeout
from rpgram.data.battle import BattleRepository
from rpgram.data.player import PlayerRepo
from rpgram.domain.apis import StatisticsGateway
from rpgram.domain.errors import AlreadyInBattle, NoPlayer, NoBattle
from rpgram.domain.models.battle import (
    PlayerState,
    Battle,
    HeroState,
    PlayInfo,
    World,
    CreateBattle,
    RunningBattle,
    BattleResult,
    SSEEvent,
    BattleStarted,
)
from rpgram.domain.utypes import PlayerId, BattleId
from rpgram.presentation.models.battle import Side


class BattleService:
    def __init__(
        self,
        battle_repo: BattleRepository,
        player_repo: PlayerRepo,
        world: World,
        stats: StatisticsGateway,
    ):
        self.stats = stats
        self.world = world
        self.player_repo = player_repo
        self.battle_repo = battle_repo

        # todo isn't it too much player id?

    def get_all_battles(self) -> list[Battle]:
        return [
            battle
            for battle in self.battle_repo.get_battles()
            if isinstance(battle, Battle)
        ]

    def get_battle(self, player_id: PlayerId) -> Battle:
        battle = self.battle_repo.get_battle(player_id)
        if battle is None:
            raise NoBattle(player_id=player_id)
        return battle

    def check_battle_result(self, player_id: PlayerId) -> BattleResult:
        battle_result = self.battle_repo.get_battle_result(player_id)
        if battle_result:
            return battle_result
        raise NoBattle(player_id=player_id)

    def start_battle(
        self,
        player_id: PlayerId,
        opponent_id: PlayerId | None,
        streamer: Streamer,
        is_npc: bool = False,
    ) -> BattleStarted:
        if self.battle_repo.get_battle(player_id):
            raise AlreadyInBattle(player_id)
        if opponent_id and self.battle_repo.get_battle(opponent_id):
            raise AlreadyInBattle(opponent_id)
        player = self.player_repo.get_player(player_id)
        if player is None:
            raise NoPlayer(player_id)
        if opponent_id is not None:
            opponent = self.player_repo.get_player(opponent_id)
            if opponent is None:
                raise NoPlayer(player_id)
            opponent_state = PlayerState(
                HeroState(opponent.hero.health, []),
                PlayInfo(player.hero.combo_tree, player.hero.combo_tree),
                opponent_id,
            )
        else:
            opponent_state = None

        battle = CreateBattle(
            PlayerState(
                HeroState(player.hero.health, []),
                PlayInfo(player.hero.combo_tree, player.hero.combo_tree),
                player_id,
            ),
            opponent_state,
        )
        battle_id = self.battle_repo.add_battle(battle)
        if opponent_state is not None:
            running_battle = self.battle_repo.get_battle(battle_id=battle_id)
            if running_battle is None:
                raise NoBattle(battle_id)
            if isinstance(running_battle, RunningBattle):
                asyncio.create_task(
                    battle_loop_until_victory_or_timeout(
                        running_battle,
                        self.world,
                        streamer,
                        self.battle_repo,
                        self.stats,
                    )
                )
            battle_started = time.time()
            if is_npc:
                battle_started += self.world.battle_preparation
            return BattleStarted(int(battle_started), battle_id)
        return BattleStarted(None, battle_id)

    def connect(
        self, opponent_id: PlayerId, battle_id: BattleId, streamer: Streamer
    ) -> int:
        # todo return this to restrict self battles
        # if self.battle_repo.get_battle(opponent_id):
        #     raise AlreadyInBattle(opponent_id)
        opponent = self.player_repo.get_player(opponent_id)
        if opponent is None:
            raise NoPlayer(opponent_id)
        battle = self.battle_repo.get_battle(battle_id=battle_id)
        if battle is None:
            raise NoBattle(battle_id)
        player_state = PlayerState(
            HeroState(opponent.hero.health, []),
            PlayInfo(opponent.hero.combo_tree, opponent.hero.combo_tree),
            opponent_id,
        )
        battle.opponent = player_state
        self.battle_repo.connect_side(opponent_id, Side.RIGHT, battle_id)
        running_battle = battle_to_run(battle)
        self.battle_repo.upgrade_battle(running_battle)
        asyncio.create_task(
            battle_loop_until_victory_or_timeout(
                running_battle, self.world, streamer, self.battle_repo, self.stats
            )
        )
        return int(time.time() + self.world.battle_preparation)

    def leave_battle(self, player_id: PlayerId) -> None:
        battle = self.battle_repo.get_battle(player_id)
        if battle is None:
            raise NoBattle(player_id=player_id)
        self.battle_repo.remove_battle(battle.battle_id)
