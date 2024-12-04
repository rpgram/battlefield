from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.rabbit import RabbitRouter


from rpgram.app.interactors.create_battle import StartBattleMicroservices
from rpgram.presentation.queue.models import PlayerDTO, from_stream_player_converter


def make_rabbit_router(q_dsn: str | None):
    if q_dsn:
        router = RabbitRouter(q_dsn)
    else:
        router = RabbitRouter()

    sub = router.subscriber("starts")

    sub(start_by_micro)
    return router


@inject
async def start_by_micro(
    player: PlayerDTO,
    opponent: PlayerDTO,
    interactor: FromDishka[StartBattleMicroservices],
):
    interactor.execute(
        from_stream_player_converter(player), from_stream_player_converter(opponent)
    )
