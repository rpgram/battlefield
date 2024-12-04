from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka.plotter import render_d2
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka as set_dish_api
from dishka.integrations.faststream import setup_dishka as set_dish_stream
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit.fastapi import RabbitBroker

from rpgram.app.config import config_factory
from rpgram.app.ioc import BattleProvider, InteractorsProvider
from rpgram.presentation.queue.battle import make_rabbit_router
from rpgram.presentation.routers.battle import battle_router
from rpgram.presentation.routers.fakes import fake_router
from rpgram.presentation.routers.players import players_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # fas = create_faststream()
    # assert fas.broker
    # await fas.broker.start()
    yield None
    # await fas.broker.close()
    await app.state.dishka_container.close()


container = make_async_container(BattleProvider(), InteractorsProvider())


def create_faststream() -> FastStream:
    broker = RabbitBroker()
    faststream_app = FastStream(broker)
    router = make_rabbit_router(None)
    set_dish_stream(container, faststream_app)
    broker.include_router(router)
    return faststream_app


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(fake_router)
    app.include_router(players_router)
    app.include_router(battle_router)
    set_dish_api(container, app)
    return app


def create_app():
    fa_app = create_fastapi_app()
    return fa_app
