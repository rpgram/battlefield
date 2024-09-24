import asyncio
from contextlib import asynccontextmanager

import hypercorn
import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from rpgram.app.ioc import InteractorsProvider, BattleProvider
from rpgram.presentation.routers.battle import battle_router
from rpgram.presentation.routers.fakes import fake_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


def create_app():
    app = FastAPI()
    app.include_router(fake_router)
    app.include_router(battle_router)
    container = make_async_container(InteractorsProvider(), BattleProvider())
    setup_dishka(container, app)
    return app


# config = Config()
# config.bind = ["localhost:8080"]
# asyncio.run(serve(app=create_app(), config=config))
