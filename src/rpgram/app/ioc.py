from dishka import Provider, provide, Scope

from rpgram.app.services.action import ActionInteractor
from rpgram.app.services.battle import BattleService
from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleStorage, BattleRepository
from rpgram.data.player import PlayerRepo, PlayerStorage, FakeStorage, InMemoryPlayers
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.interfaces.memory_storage import IPlayerStorage
from rpgram.domain.models.battle import (
    World,
    Move,
    Action,
)


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def action_interactor(
        self, battle_repo: BattleRepository, world: World
    ) -> ActionInteractor:
        return ActionInteractor(COMBO_ROOT, world, battle_repo)


class BattleProvider(Provider):
    scope = Scope.APP

    battle_storage = provide(BattleStorage)
    player_storage = provide(FakeStorage, provides=InMemoryPlayers)

    battle_repo = provide(BattleRepository)
    player_repo = provide(PlayerRepo)
    streamer = provide(Streamer, scope=Scope.APP)

    battle_service = provide(BattleService)

    @provide
    def world(self) -> World:
        return World(Move(Action("nop", 0, None), Action("nop", 0, None)))
