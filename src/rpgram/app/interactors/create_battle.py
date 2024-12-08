import asyncio
import dataclasses
import logging
import time

from rpgram.app.services.auth import secure_string_generator
from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleRepository
from rpgram.domain.algos.loop import battle_loop_until_victory_or_timeout
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.apis import StatisticsGateway
from rpgram.domain.errors import NoBattle
from rpgram.domain.models.battle import (
    RunningBattle,
    PlayerState,
    HeroState,
    PlayInfo,
    CreateBattle,
    World,
    BattleKeysResponse,
)
from rpgram.domain.utypes import PlayerId

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class StartBattleHeroDTO:
    health: int
    combo_root_id: int


@dataclasses.dataclass
class StartBattlePlayerDTO:
    name: str
    player_id: PlayerId
    hero: StartBattleHeroDTO


def create_battle(player: StartBattlePlayerDTO, opponent: StartBattlePlayerDTO):
    return CreateBattle(
        PlayerState(
            HeroState(player.hero.health, []),
            PlayInfo(COMBO_ROOT, COMBO_ROOT),
            player.player_id,
        ),
        PlayerState(
            HeroState(opponent.hero.health, []),
            PlayInfo(COMBO_ROOT, COMBO_ROOT),
            opponent.player_id,
        ),
    )


class StartBattleMicroservices:
    def __init__(
        self,
        battle_repo: BattleRepository,
        streamer: Streamer,
        world: World,
        stats: StatisticsGateway,
    ):
        self.stats = stats
        self.world = world
        self.streamer = streamer
        self.battle_repo = battle_repo

    def execute(self, player: StartBattlePlayerDTO, opponent: StartBattlePlayerDTO):
        battle = create_battle(player, opponent)
        battle_id = self.battle_repo.add_battle(battle)
        running_battle = self.battle_repo.get_battle(battle_id=battle_id)
        if running_battle is None:
            raise NoBattle(battle_id)
        if isinstance(running_battle, RunningBattle):
            asyncio.create_task(
                battle_loop_until_victory_or_timeout(
                    running_battle,
                    self.world,
                    self.streamer,
                    self.battle_repo,
                    self.stats,
                )
            )
        battle_started = time.time()
        battle_started += self.world.battle_preparation

        def insert_key(player_id: PlayerId) -> str:
            key = secure_string_generator()
            while self.battle_repo.get_player_id(key):
                key = secure_string_generator()
            self.battle_repo.update_keys(player_id, key)
            return key

        pk = insert_key(player.player_id)
        ok = insert_key(opponent.player_id)
        logger.info("Battle %s started", battle_id, extra={"scope": "battle"})
        return BattleKeysResponse(battle_id, pk, ok)
