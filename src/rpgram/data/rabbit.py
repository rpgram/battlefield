import json
from dataclasses import asdict

from aio_pika import Message
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from rpgram.domain.apis import StatisticsGateway
from rpgram.domain.models.battle import BattleResult


class RabbitGateway(StatisticsGateway):
    def __init__(self, con: AbstractRobustConnection):
        self.con = con

    async def battle_finished(self, battle_result: BattleResult) -> None:
        chan = await self.con.channel()
        await chan.default_exchange.publish(
            Message(body=json.dumps(asdict(battle_result)).encode()),
            routing_key="events",
        )
        await chan.close()
