from dishka import Provider, provide, Scope

from rpgram.app.battle import BattleRunner
from rpgram.app.services.action import ActionInteractor
from rpgram.domain.algos.trie import COMBO_ROOT
from rpgram.domain.models.battle import (
    Battle,
    World,
    HeroState,
    Move,
    Action,
    PlayerState,
    PlayInfo,
)


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    battle_runner = provide(BattleRunner)

    @provide
    def action_interactor(self, battle: Battle, world: World) -> ActionInteractor:
        return ActionInteractor(COMBO_ROOT, world, battle)


class BattleProvider(Provider):
    scope = Scope.APP

    @provide
    def battle(self) -> Battle:
        return Battle(
            PlayerState(HeroState(50, []), PlayInfo()),
            PlayerState(
                HeroState(30, []),
                PlayInfo(),
            ),
        )

    @provide
    def world(self) -> World:
        return World(Move(Action("nop", 0, None), Action("nop", 0, None)))
