from dishka import Provider, provide, Scope

from rpgram.app.services.battle import BattleService
from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleStorage, BattleRepository
from rpgram.data.player import PlayerRepo, PlayerStorage
from rpgram.domain.models.battle import (
    World,
    Move,
    Action,
)


# class InteractorsProvider(Provider):
#     scope = Scope.REQUEST
#
#     battle_runner = provide(BattleRunner)
#
#     @provide
#     def action_interactor(self, battle: Battle, world: World) -> ActionInteractor:
#         return ActionInteractor(COMBO_ROOT, world, battle)


class BattleProvider(Provider):
    scope = Scope.APP

    battle_storage = provide(BattleStorage)
    player_storage = provide(PlayerStorage)

    # @provide
    # def battle_repo(self, storage: BattleStorage):
    #     return BattleRepository(storage)
    battle_repo = provide(BattleRepository)
    player_repo = provide(PlayerRepo)
    streamer = provide(Streamer)

    @provide
    def battle_service(
        self,
        battle_repo: BattleRepository,
        player_repo: PlayerRepo,
        world: World,
        streamer: Streamer,
    ) -> BattleService:
        return BattleService(battle_repo, player_repo, streamer, world)

    @provide
    def world(self) -> World:
        return World(Move(Action("nop", 0, None), Action("nop", 0, None)))
