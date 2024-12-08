from typing import AsyncIterable

import aio_pika
from aio_pika import RobustConnection
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
    AbstractChannel,
)
from dishka import Provider, provide, Scope

from rpgram.app.interactors.create_battle import StartBattleMicroservices
from rpgram.app.interactors.process import BattlePollInteractor
from rpgram.app.services.action import ActionInteractor
from rpgram.app.services.battle import BattleService
from rpgram.app.sse import Streamer
from rpgram.data.battle import BattleStorage, BattleRepository
from rpgram.data.player import PlayerRepo, PlayerStorage, FakeStorage, InMemoryPlayers
from rpgram.data.rabbit import RabbitGateway
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.apis import StatisticsGateway
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

    battle_interactor = provide(BattlePollInteractor)

    battle_rmq = provide(StartBattleMicroservices)


class BattleProvider(Provider):
    scope = Scope.APP

    battle_storage = provide(BattleStorage)
    player_storage = provide(FakeStorage, provides=InMemoryPlayers)

    battle_repo = provide(BattleRepository)
    player_repo = provide(PlayerRepo)
    streamer = provide(Streamer, scope=Scope.APP)

    battle_service = provide(BattleService, scope=Scope.REQUEST)

    @provide
    async def aio_pika_con(self) -> StatisticsGateway:
        con = await aio_pika.connect_robust()
        # con = await aio_pika.connect_robust("amqp://guest:guest@host.docker.internal:5672/")
        return RabbitGateway(con)

    @provide
    def world(self) -> World:
        return World(Move(Action("nop", 0, None), Action("nop", 0, None)))
