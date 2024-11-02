import asyncio
import dataclasses
import time

from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleRepository
from rpgram.domain.algos.loop import battle_loop_until_victory_or_timeout
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.errors import NoBattle
from rpgram.domain.models.battle import RunningBattle, PlayerState, HeroState, PlayInfo, CreateBattle, World, \
    BattleStarted
from rpgram.domain.utypes import PlayerId


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
            player.player_id),
        PlayerState(
            HeroState(opponent.hero.health, []),
            PlayInfo(COMBO_ROOT, COMBO_ROOT),
            opponent.player_id
        )
    )


class StartBattleMicroservices:
    def __init__(self, battle_repo: BattleRepository, streamer: Streamer, world: World):
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
                    running_battle, self.world, self.streamer, self.battle_repo
                )
            )
        battle_started = time.time()
        battle_started += self.world.battle_preparation
        return BattleStarted(int(battle_started), battle_id)
