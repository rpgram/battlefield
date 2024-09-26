from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from rpgram.app.ioc import BattleProvider, InteractorsProvider
from rpgram.presentation.routers.battle import battle_router
from rpgram.presentation.routers.fakes import fake_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield None
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(fake_router)
    app.include_router(battle_router)
    container = make_async_container(BattleProvider(), InteractorsProvider())
    setup_dishka(container, app)
    return app
