import logging
from typing import Any

from hypercorn.config import Config

import asyncio
from hypercorn.asyncio import serve

from rpgram.main import create_app


def hyper_app() -> Any:
    return create_app()


if __name__ == "__main__":
    config = Config()
    config.loglevel = "DEBUG"
    config.bind = ["0.0.0.0:8000"]
    logging.warning("Setup finished...")
    asyncio.run(serve(hyper_app(), config))
