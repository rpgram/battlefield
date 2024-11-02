import dataclasses
import os


@dataclasses.dataclass
class AppConfig:
    queue_dsn: str


def config_factory() -> AppConfig:
    return AppConfig(os.environ["QUEUE_DSN"])
