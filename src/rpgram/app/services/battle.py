import asyncio

from rpgram.app.sse import Streamer
from rpgram.domain.algos.loop import start_battle_loop_until_victory
from rpgram.domain.data.battle import BattleRepository
from rpgram.domain.data.player import PlayerRepo
from rpgram.domain.errors import AlreadyInBattle, NoPlayer, NoBattle
from rpgram.domain.models.battle import PlayerState, Battle, HeroState, PlayInfo, World
from rpgram.domain.types import PlayerId, BattleId
from rpgram.presentation.models.battle import Side


class BattleService:
    def __init__(
        self,
        battle_repo: BattleRepository,
        player_repo: PlayerRepo,
        streamer: Streamer,
        world: World,
    ):
        self.world = world
        self.player_repo = player_repo
        self.battle_repo = battle_repo
        self.streamer = streamer

    def start_battle(
        self, player_id: PlayerId, opponent_id: PlayerId | None
    ) -> BattleId:
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
        else:
            opponent = None
        if opponent is None:
            opponent_state = None
        else:
            opponent_state = PlayerState(
                HeroState(opponent.hero.health, []), PlayInfo(player.hero.combo_tree), opponent_id
            )
        battle = Battle(
            PlayerState(
                HeroState(player.hero.health, []), PlayInfo(player.hero.combo_tree), player_id
            ),
            opponent_state,
        )
        battle_id = self.battle_repo.add_battle(battle, player_id)
        if opponent_state is not None:
            asyncio.create_task(
                start_battle_loop_until_victory(battle, self.world, self.streamer)
            )
        return battle_id

    def connect(self, opponent_id: PlayerId, battle_id: BattleId) -> None:
        opponent = self.player_repo.get_player(opponent_id)
        if opponent is None:
            raise NoPlayer(opponent_id)
        battle = self.battle_repo.get_battle(battle_id)
        if battle is None:
            raise NoBattle(battle_id)
        player_state = PlayerState(
            HeroState(opponent.hero.health, []), PlayInfo(opponent.hero.combo_tree)
        )
        battle.opponent = player_state
        self.battle_repo.connect_side(opponent_id, Side.RIGHT, battle_id)
        asyncio.create_task(
            start_battle_loop_until_victory(battle, self.world, self.streamer)
        )

    def leave_battle(self, player_id: PlayerId) -> None:
        battle = self.battle_repo.get_battle(player_id)
        if battle is None:
            return
        self.battle_repo.remove_battle(battle.battle_id)
