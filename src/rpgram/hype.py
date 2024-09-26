from typing import Any

from hypercorn.config import Config

import asyncio
from hypercorn.asyncio import serve

from rpgram.main import create_app


def hyper_app() -> Any:
    return create_app()


if __name__ == '__main__':
    config = Config()
    config.bind = ["localhost:8000"]
    asyncio.run(serve(hyper_app(), config))
